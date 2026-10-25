"""Optional Playwright check against the real ASGI app, with an isolated HTTPS test origin.

No network deployment or TLS certificate validation is claimed by this check.
"""
import os
import tempfile
import sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.update(BAKAYA_ENV="production", BAKAYA_PUBLIC_ORIGIN="https://bakayaai-sandesh.vercel.app", BAKAYA_ALLOWED_HOSTS="bakayaai-sandesh.vercel.app", BAKAYA_ENABLE_LLM="false", NEATLOGS_API_KEY="", NEATLOGS_PROJECT_TOKEN="", CRUSTDATA_API_KEY="")

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from backend import auth, storage
from backend.main import app


def main():
    output = Path(__file__).resolve().parents[1] / "artifacts" / "qa"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        storage.DATA_DIR = Path(directory)
        for email, tenant in (("reviewer@example.com", "a"), ("other@example.com", "b")):
            auth.provision(email, "QA reviewer", tenant, "reviewer", "test-only-password-123")
        with TestClient(app, base_url="https://bakayaai-sandesh.vercel.app") as client, sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width":1440,"height":1000}, reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def bridge(route):
                request = route.request
                url = urlsplit(request.url)
                client.cookies.clear()  # Only browser-supplied cookies authorize each request.
                response = client.request(request.method, url.path + ("?" + url.query if url.query else ""), headers=request.all_headers(), content=request.post_data_buffer)
                headers = {k:v for k,v in response.headers.items() if k not in {"content-length","content-encoding","transfer-encoding"}}
                route.fulfill(status=response.status_code, headers=headers, body=response.content)

            page.route("https://bakayaai-sandesh.vercel.app/**", bridge)
            page.goto("https://bakayaai-sandesh.vercel.app", wait_until="networkidle")
            page.get_by_role("button", name="Sign in", exact=True).wait_for()
            for width in (1440,390):
                page.set_viewport_size({"width":width,"height":1000})
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                page.screenshot(path=str(output / f"sign-in-{width}.png"), full_page=True)
            page.set_viewport_size({"width":1440,"height":1000})
            page.get_by_role("button", name="Use demo credentials", exact=True).click()
            assert page.get_by_label("Email", exact=True).input_value() == "demo@bakaya.example"
            page.get_by_label("Email", exact=True).fill("reviewer@example.com")
            page.get_by_label("Password", exact=True).fill("wrong-password")
            page.get_by_role("button", name="Sign in", exact=True).click()
            page.get_by_role("alert").get_by_text("Invalid credentials", exact=True).wait_for()
            page.get_by_label("Password", exact=True).fill("test-only-password-123")
            page.get_by_role("button", name="Sign in", exact=True).click()
            page.get_by_role("button", name="Sign out", exact=True).wait_for()
            page.get_by_role("button", name="Explore a demo", exact=True).click()
            page.locator(".working-bar").wait_for(state="hidden")
            page.get_by_role("button", name="Review claim packet", exact=True).click()
            reviewer = page.get_by_label("Reviewer name", exact=True)
            assert reviewer.input_value() == "QA reviewer" and reviewer.get_attribute("readonly") is not None
            page.screenshot(path=str(output / "authenticated-review.png"), full_page=True)
            page.set_viewport_size({"width":390,"height":844})
            opener = page.get_by_role("button", name="Open navigation", exact=True)
            opener.click()
            drawer = page.get_by_role("dialog", name="Workspace navigation")
            drawer.wait_for()
            page.keyboard.press("Tab")
            assert page.evaluate("Boolean(document.activeElement.closest('[role=dialog]'))")
            page.keyboard.press("Escape")
            drawer.wait_for(state="hidden")
            assert opener.evaluate("element => element === document.activeElement")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=str(output / "workspace-mobile-polished.png"), full_page=True)
            page.set_viewport_size({"width":1440,"height":1000})
            page.get_by_role("button", name="Sign out", exact=True).click()
            page.get_by_role("button", name="Sign in", exact=True).wait_for()
            page.get_by_label("Email", exact=True).fill("other@example.com")
            page.get_by_label("Password", exact=True).fill("test-only-password-123")
            page.get_by_role("button", name="Sign in", exact=True).click()
            page.get_by_role("button", name="Sign out", exact=True).wait_for()
            assert page.get_by_text("Synthetic demo", exact=True).count() == 0, "Previous tenant leaked into UI"
            assert not errors, errors
            browser.close()
    print("Sign-in, error, CSRF mutation, reviewer identity, logout and tenant switch UI checks passed.")


if __name__ == "__main__":
    main()
