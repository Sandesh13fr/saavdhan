"""Record a synthetic, isolated agent lifecycle without paid providers."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "evidence"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bakaya-agent-evidence-") as data:
        environment = {**os.environ, "BAKAYA_DATA_DIR": data, "BAKAYA_ENV": "local", "BAKAYA_ENABLE_LLM": "false", "NEATLOGS_API_KEY": "", "CRUSTDATA_API_KEY": "", "OPENAI_API_KEY": "", "LITELLM_API_KEY": ""}
        with (OUTPUT / "server.log").open("w") as log:
            server = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "18081", "--no-access-log"], cwd=ROOT, env=environment, stdout=log, stderr=log)
            try:
                client = httpx.Client(base_url="http://127.0.0.1:18081", timeout=30)
                for _ in range(100):
                    try:
                        if client.get("/api/health").status_code == 200:
                            break
                    except httpx.TransportError:
                        time.sleep(.1)
                else:
                    raise RuntimeError("Isolated server failed to start")
                with sync_playwright() as p:
                    browser = p.chromium.launch(channel="msedge", headless=True)
                    context = browser.new_context(viewport={"width":1440,"height":1000}, record_video_dir=str(OUTPUT / "video"), record_video_size={"width":1440,"height":1000})
                    page = context.new_page()
                    errors = []
                    page.on("pageerror",lambda error:errors.append(str(error)))
                    page.goto(str(client.base_url), wait_until="networkidle")
                    page.get_by_role("button",name="Explore a demo",exact=True).click()
                    page.get_by_text("Synthetic demo",exact=True).wait_for()
                    case = client.get("/api/cases").json()[0]
                    cid = case["id"]
                    page.get_by_role("button",name="Prepare claim",exact=True).click()
                    page.locator(".working-bar").wait_for(state="hidden")
                    page.get_by_text("Preparation checkpoints",exact=True).click()
                    page.wait_for_timeout(2000)
                    first = client.get(f"/api/cases/{cid}").json()
                    assert first["agent"]["status"] == "waiting_review"
                    assert client.get(f"/api/cases/{cid}/export").status_code == 409
                    page.get_by_role("button",name="Review claim packet",exact=True).click()
                    page.get_by_label("Reviewer name").fill("Synthetic QA reviewer")
                    page.get_by_label("Allocate receipt to an invoice").first.select_option("INV-004")
                    page.get_by_label("Supporting evidence").first.select_option("REMIT-003")
                    page.get_by_label("Why is this the right allocation?").first.fill("Synthetic remittance explicitly identifies INV-004.")
                    page.get_by_label("I have confirmed the buyer’s details.",exact=False).check()
                    page.get_by_label("I have reviewed the rate assumptions.",exact=False).check()
                    page.get_by_role("button",name="Save review decisions",exact=True).click()
                    page.get_by_text("Verification checks are clear.",exact=True).wait_for()
                    reviewed = client.get(f"/api/cases/{cid}").json()
                    page.get_by_role("button",name="Resume preparation",exact=True).click()
                    page.locator(".working-bar").wait_for(state="hidden")
                    waiting = client.get(f"/api/cases/{cid}").json()
                    assert waiting["agent"]["status"] == "waiting_approval" and waiting["approval"] is None
                    assert client.get(f"/api/cases/{cid}/export").status_code == 409
                    page.wait_for_timeout(2000)
                    page.get_by_label("I have reviewed the records, calculations, and assumptions in this packet.",exact=True).check()
                    page.get_by_role("button",name="Approve packet",exact=True).click()
                    page.get_by_role("button",name="Download claim packet",exact=True).wait_for()
                    approved = client.get(f"/api/cases/{cid}").json()
                    page.get_by_role("button",name="Resume preparation",exact=True).click()
                    page.locator(".working-bar").wait_for(state="hidden")
                    final = client.get(f"/api/cases/{cid}").json()
                    assert final["agent"]["status"] == "complete"
                    assert final["agent"]["steps"][-1]["tool"] == "build_local_packet"
                    with page.expect_download() as download:
                        page.get_by_role("button",name="Download claim packet",exact=True).click()
                    download.value.save_as(str(OUTPUT / "agent-claim-packet.zip"))
                    packet = (OUTPUT / "agent-claim-packet.zip").read_bytes()
                    with zipfile.ZipFile(io.BytesIO(packet)) as archive:
                        assert {"approval.json","evidence-index.csv","interest-schedule.pdf","demand-letter.txt","odr-field-sheet.json"} <= set(archive.namelist())
                        assert "SYNTHETIC DEMO" in archive.read("demand-letter.txt").decode()
                    assert first["agent"]["run_id"] == final["agent"]["run_id"]
                    assert reviewed["revision"] > first["revision"]
                    assert final["approval"]["revision"] == final["revision"]
                    assert final["totals"]["principal"] == "470000.00"
                    assert final["agent"]["model_attempts"] == 0
                    page.screenshot(path=str(OUTPUT / "agent-complete.png"),full_page=True)
                    page.wait_for_timeout(2000)
                    video = page.video
                    context.close()
                    video.save_as(str(OUTPUT / "agent-lifecycle.webm"))
                    browser.close()
                    assert not errors, errors
                recovery_case = client.post("/api/cases/demo").json()["id"]
                failed = client.post(f"/api/cases/{recovery_case}/agent/run",json={"simulate_tool_failure":True}).json()
                recovered = client.post(f"/api/cases/{recovery_case}/agent/resume",json={"simulate_tool_failure":True}).json()
                assert failed["agent"]["status"] == "recoverable_failure" and recovered["agent"]["status"] == "waiting_review"
                assert [s["tool"] for s in recovered["agent"]["steps"]].count("inventory_evidence") == 1
                assert recovered["agent"]["attempts"]["verify_reconciliation"] == 2
                report = {"synthetic":True,"paid_calls":0,"workflow":"real local tools; model planning disabled; scripted human review inputs", "stages":{"waiting_review":first,"reviewed":reviewed,"waiting_approval":waiting,"approved":approved,"complete":final},"recovery":{"label":"SIMULATED local failure, not provider outage","failed":failed["agent"],"resumed":recovered["agent"]},"packet_bytes":len(packet),"browser_errors":errors}
                (OUTPUT / "agent-lifecycle.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
                print(json.dumps({"status":"complete","packet_bytes":len(packet),"checkpoints":len(final["agent"]["checkpoints"]),"run_id":final["agent"]["run_id"],"paid_calls":0,"recovery":"passed","video":"agent-lifecycle.webm"}))
            finally:
                server.terminate()
                server.wait(timeout=15)


if __name__ == "__main__":
    main()
