"""Exercise navigation, hazard filtering, map data and dashboard rendering."""
import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def run(base_url, screenshots):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
                                                    "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1550, "height": 1050}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(base_url)
        expect(page.get_by_role("heading", name="When Nature Strikes")).to_be_visible(timeout=30000)
        expect(page.get_by_text("15,727", exact=True)).to_be_visible()
        expect(page.get_by_role("heading", name="Recorded events by hazard")).to_be_visible()
        if screenshots:
            screenshots.mkdir(parents=True, exist_ok=True)
            page.locator(".plotly .main-svg").first.wait_for()
            page.screenshot(path=screenshots / "dashboard_overview.png")
        sidebar = page.get_by_test_id("stSidebar")
        hazard = sidebar.get_by_role("combobox").nth(0)
        hazard.fill("Flood")
        page.get_by_role("option", name="Flood", exact=True).click()
        expect(page.get_by_text("5,814", exact=True)).to_be_visible()
        sidebar.get_by_text("Frequency vs impact", exact=True).click()
        expect(page.get_by_text("Flood leads this reported total, based on")).to_be_visible()
        page.get_by_text("Median", exact=True).first.click()
        expect(page.get_by_text("Flood leads this reported median, based on")).to_be_visible()
        sidebar.get_by_text("Trends", exact=True).click()
        expect(page.get_by_role("heading", name="Annual recorded frequency by hazard")).to_be_visible()
        sidebar.get_by_text("Geography", exact=True).click()
        expect(page.get_by_role("heading", name="Recorded impacts by affected country")).to_be_visible()
        expect(page.locator("canvas.maplibregl-canvas")).to_be_visible(timeout=30000)
        expect(page.get_by_role("tab", name="Unmapped records")).to_be_visible()
        page.get_by_role("tab", name="Unmapped records").click()
        expect(page.get_by_test_id("stException")).to_have_count(0)
        page.get_by_role("tab", name="Country rankings").click()
        if screenshots:
            page.locator("canvas.maplibregl-canvas").scroll_into_view_if_needed()
            page.wait_for_timeout(1300)
            page.screenshot(path=screenshots / "dashboard_geography.png")
        assert not errors, errors
        browser.close()
    print("Browser acceptance passed for four views, synchronized hazard filter, metric mode and offline map.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    run(args.url, args.screenshots)
