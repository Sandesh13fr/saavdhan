"""Optional local visual/interaction check. Requires Playwright and installed Edge.

Run against an already running local server. Screenshots use synthetic data.
"""
from pathlib import Path
import argparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "qa"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="Save a silent synthetic workflow recording.")
    record = parser.parse_args().record
    OUTPUT.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, device_scale_factor=1, reduced_motion="reduce", **({"record_video_dir": str(OUTPUT / "video"), "record_video_size": {"width": 1440, "height": 1000}} if record else {}))
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.screenshot(path=str(OUTPUT / "desktop-start.png"), full_page=True)
        demo = page.get_by_role("button", name="Explore a demo", exact=True)
        if demo.count():
            demo.click()
        else:
            page.get_by_role("button", name="How Bakaya works", exact=False).first.click()
            page.get_by_role("button", name="Explore a synthetic case").click()
        page.get_by_text("Synthetic demo", exact=True).wait_for()
        if record:
            page.wait_for_timeout(8000)
        assert page.get_by_role("button", name="Interest schedule", exact=True).is_hidden()
        page.get_by_text("More details", exact=True).click()
        page.get_by_role("button", name="Interest schedule", exact=True).click()
        page.get_by_role("button", name="Claim workspace", exact=True).click()
        if page.get_by_role("button", name="Interest schedule", exact=True).is_visible():
            page.get_by_text("More details", exact=True).click()
        page.get_by_role("button", name="How Bakaya works", exact=False).first.click()
        page.get_by_role("dialog").wait_for()
        for _ in range(6):
            page.keyboard.press("Tab")
            assert page.evaluate("document.querySelector('[role=dialog]').contains(document.activeElement)"), "Dialog focus escaped"
        page.keyboard.press("Escape")
        page.get_by_role("dialog").wait_for(state="hidden")
        assert page.evaluate("document.activeElement.textContent.includes('How Bakaya works')"), "Dialog opener focus was not restored"
        page.set_viewport_size({"width": 768, "height": 1000})
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), "Tablet overflow"
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.locator(".working-bar").wait_for(state="hidden")
        page.screenshot(path=str(OUTPUT / "desktop-case.png"), full_page=True)
        if record:
            page.wait_for_timeout(8000)
        page.get_by_role("button", name="View source", exact=False).first.click()
        page.locator(".evidence-workspace").wait_for()
        page.screenshot(path=str(OUTPUT / "desktop-evidence.png"), full_page=True)
        if record:
            page.wait_for_timeout(8000)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(OUTPUT / "mobile-evidence.png"), full_page=True)
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.get_by_role("button", name="Claim workspace", exact=True).click()
        page.get_by_role("button", name="Review claim packet", exact=True).click()
        assert page.get_by_role("button", name="Approve packet", exact=True).is_disabled()
        if record:
            page.wait_for_timeout(8000)
        page.get_by_label("Reviewer name").fill("Synthetic QA reviewer")
        page.get_by_label("Allocate receipt to an invoice").first.select_option("INV-004")
        page.get_by_label("Supporting evidence").first.select_option("REMIT-003")
        page.get_by_label("Why is this the right allocation?").first.fill("Synthetic remittance explicitly identifies INV-004.")
        page.get_by_label("I have confirmed the buyer’s details.", exact=False).check()
        page.get_by_label("I have reviewed the rate assumptions.", exact=False).check()
        page.get_by_role("button", name="Save review decisions", exact=True).click()
        page.get_by_text("Verification checks are clear.", exact=True).wait_for()
        if record:
            page.wait_for_timeout(8000)
        page.get_by_label("I have reviewed the records, calculations, and assumptions in this packet.", exact=True).check()
        page.get_by_role("button", name="Approve packet", exact=True).click()
        download_button = page.get_by_role("button", name="Download claim packet", exact=True)
        download_button.wait_for()
        with page.expect_download() as download:
            download_button.click()
        download.value.save_as(str(OUTPUT / "synthetic-claim.zip"))
        page.screenshot(path=str(OUTPUT / "desktop-approved.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(OUTPUT / "mobile-approved.png"), full_page=True)
        overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth")
        assert not overflow, "Page-level mobile horizontal overflow"
        assert not errors, errors
        if record:
            page.wait_for_timeout(8000)
        video = page.video
        context.close()
        if record:
            video.save_as(str(OUTPUT / "bakaya-workflow.webm"))
        browser.close()
    print("Browser approval/export workflow passed; desktop/mobile screenshots saved.")


if __name__ == "__main__":
    main()
