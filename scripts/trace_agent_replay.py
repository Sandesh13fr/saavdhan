"""Controlled synthetic replay against a checkout supplied as the working directory."""
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

assert os.getenv("BAKAYA_ENV") == "local" and os.getenv("BAKAYA_ENABLE_LLM") == "false", "Replay requires local mode with models disabled"
assert all(os.environ.get(key) == "" for key in ("LITELLM_API_KEY","OPENAI_API_KEY","CRUSTDATA_API_KEY")), "Paid provider keys must be explicitly blank"
data_dir = Path(os.environ["BAKAYA_DATA_DIR"]).resolve()
assert not data_dir.exists(), "Replay must use a new isolated data directory"
sys.path.insert(0, os.getcwd())
import httpx
import neatlogs
from fastapi.testclient import TestClient
from backend.main import app
from backend import storage


def main():
    revision, destination = sys.argv[1:]
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with TestClient(app) as client:
        with neatlogs.trace("bakaya-controlled-full-lifecycle", kind="WORKFLOW") as root:
            trace_id = format(root.get_span_context().trace_id, "032x")
            for key, value in {"controlled_replay":True,"synthetic":True,"commit":revision,"model_calls":0,"model_tokens":0,"model_cost_usd":0.0}.items():
                root.set_attribute("bakaya." + key, value)
            case = client.post("/api/cases/demo").json()
            cid = case["id"]
            first = client.post(f"/api/cases/{cid}/agent/run", json={}).json()
            assert first["agent"]["status"] == "waiting_review"
            with neatlogs.trace("checkpoint-waiting-review-revision-1", kind="TOOL"):
                assert first["revision"] == 1
            assert client.get(f"/api/cases/{cid}/export").status_code == 409
            with neatlogs.trace("scripted-human-review", kind="TOOL") as span:
                span.set_attribute("bakaya.review_origin", "scripted synthetic QA; not professional review")
                review = client.patch(f"/api/cases/{cid}/review", json={"reviewer":"Synthetic QA reviewer","rate_confirmed":True,"buyer_confirmed":True,"resolutions":[{"payment_id":"PAY-003","source_id":"REMIT-003","reason":"Synthetic source identifies INV-004","allocations":[{"invoice_id":"INV-004","amount":"150000"}]}]}).json()
                assert review["status"] == "ready"
            waiting = client.post(f"/api/cases/{cid}/agent/resume", json={}).json()
            assert waiting["agent"]["status"] == "waiting_approval"
            with neatlogs.trace("checkpoint-waiting-approval-revision-2", kind="TOOL"):
                assert waiting["revision"] == 2
            with neatlogs.trace("scripted-explicit-approval", kind="TOOL"):
                assert client.post(f"/api/cases/{cid}/approve", json={"reviewer":"Synthetic QA reviewer"}).status_code == 200
            final = client.post(f"/api/cases/{cid}/agent/resume", json={}).json()
            assert final["agent"]["status"] == "complete" and final["agent"]["model_attempts"] == 0
            with neatlogs.trace("checkpoint-complete-revision-2", kind="TOOL"):
                assert len(final["agent"]["checkpoints"]) == 10
            with neatlogs.trace("verify-approved-export", kind="TOOL") as span:
                response = client.get(f"/api/cases/{cid}/export")
                assert response.status_code == 200
                with zipfile.ZipFile(io.BytesIO(response.content)) as packet:
                    assert {"approval.json","evidence-index.csv","demand-letter.txt"} <= set(packet.namelist())
                    assert "SYNTHETIC DEMO" in packet.read("demand-letter.txt").decode()
                    nested = [name for name in packet.namelist() if "approved-packet-" in name]
                redundant = list(storage.upload_dir(cid).glob("approved-packet-*.zip"))
                span.set_attribute("bakaya.redundant_packet_files", len(redundant))
                span.set_attribute("bakaya.export_valid", True)
                (output / (revision + "-packet.zip")).write_bytes(response.content)
            with neatlogs.trace("simulated-local-failure-recovery", kind="WORKFLOW") as span:
                span.set_attribute("bakaya.simulated_failure", True)
                recovery_id = client.post("/api/cases/demo").json()["id"]
                failed = client.post(f"/api/cases/{recovery_id}/agent/run", json={"simulate_tool_failure":True}).json()["agent"]
                recovered = client.post(f"/api/cases/{recovery_id}/agent/resume", json={"simulate_tool_failure":True}).json()["agent"]
                assert failed["status"] == "recoverable_failure" and recovered["status"] == "waiting_review"
                assert [s["tool"] for s in recovered["steps"]].count("inventory_evidence") == 1
            for key, value in {"run_id":final["agent"]["run_id"],"status":"complete","checkpoints":len(final["agent"]["checkpoints"]),"redundant_packet_files":len(redundant)}.items():
                root.set_attribute("bakaya." + key, value)
            result = {"revision":revision,"controlled_replay":True,"synthetic":True,"trace_id":trace_id,"run_id":final["agent"]["run_id"],"states":[first["agent"]["status"],waiting["agent"]["status"],final["agent"]["status"]],"checkpoints":final["agent"]["checkpoints"],"totals":final["totals"],"model_calls":0,"model_tokens":0,"model_inference_cost_usd":0,"total_delivery_cost_usd":None,"redundant_packet_files":len(redundant),"nested_packet_entries":nested,"export_bytes":len(response.content),"export_valid":True,"simulated_recovery_passed":True,"observed_local_seconds":time.perf_counter()-started}
    for attempt in range(12):
        response = httpx.get("https://ingest.neatlogs.com/api/traces/v3/" + trace_id, headers={"x-api-key":os.environ["NEATLOGS_API_KEY"],"x-neatlogs-doctor":"v1"}, timeout=15)
        if response.status_code == 200:
            readback = response.json()
            names = [span["node_name"] for span in readback.get("spans", [])]
            required = {"bakaya-controlled-full-lifecycle","inventory_evidence","analyze_ledger","verify_reconciliation","request_review","request_approval","build_local_packet","scripted-human-review","scripted-explicit-approval","verify-approved-export","simulated-local-failure-recovery","checkpoint-waiting-review-revision-1","checkpoint-waiting-approval-revision-2","checkpoint-complete-revision-2"}
            if not required <= set(names) or len(names) != 27:
                time.sleep(2)
                continue
            spans = {span["span_id"]:span for span in readback["spans"]}
            root_id = next(span["span_id"] for span in spans.values() if span["node_name"] == "bakaya-controlled-full-lifecycle")
            for span in spans.values():
                assert span["traceId"] == trace_id
                node, seen = span, set()
                while node.get("parent_span_id"):
                    assert node["span_id"] not in seen
                    seen.add(node["span_id"])
                    node = spans[node["parent_span_id"]]
                assert node["span_id"] == root_id
            assert readback["llmCalls"] == 0 and readback["totalTokensUsed"] == 0
            recovery_root = next(span["span_id"] for span in spans.values() if span["node_name"] == "simulated-local-failure-recovery")
            retry_spans = []
            for span in spans.values():
                if span["node_name"] == "verify_reconciliation":
                    node = span
                    while node.get("parent_span_id") and node["parent_span_id"] != recovery_root:
                        node = spans[node["parent_span_id"]]
                    if node.get("parent_span_id") == recovery_root:
                        retry_spans.append(span)
            assert len(retry_spans) == 2
            result["readback_span_count"] = len(spans)
            result["all_spans_descend_from_lifecycle_root"] = True
            (output / (revision + "-trace-readback.json")).write_text(json.dumps(readback, indent=2))
            result["readback_http_status"] = 200
            break
        time.sleep(2)
    else:
        raise RuntimeError("Exact trace readback unavailable: HTTP " + str(response.status_code))
    (output / (revision + "-result.json")).write_text(json.dumps(result, indent=2))
    print(json.dumps({"revision":revision,"trace_id":trace_id,"readback":200,"redundant_packet_files":len(redundant)}))


if __name__ == "__main__":
    main()
