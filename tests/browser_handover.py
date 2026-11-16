"""Browser acceptance for ten views and the licensed-data-free demo."""
import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def run(url, evidence, synthetic=False):
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
                                                "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1550, "height": 1050}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(url)
        sidebar = page.get_by_test_id("stSidebar")
        main = page.get_by_test_id("stMain")

        def heading(name):
            expect(main.get_by_role("heading", name=name, exact=True)).to_be_visible(timeout=30000)

        def snap(name):
            expect(page.get_by_test_id("stException")).to_have_count(0)
            if evidence:
                evidence.mkdir(parents=True, exist_ok=True)
                page.evaluate("document.querySelector('[data-testid=stMain]').scrollTop=0")
                page.screenshot(path=evidence / f"{name}.png", animations="disabled")

        def view(name, title):
            sidebar.get_by_text(name, exact=True).click()
            heading(title)

        heading("Recorded events by hazard")
        expect(main.get_by_text("12" if synthetic else "15,727", exact=True).first).to_be_visible()
        if synthetic:
            expect(main.get_by_text("SYNTHETIC DEMONSTRATION", exact=False)).to_be_visible()
        expect(main.locator(".plotly .main-svg").first).to_be_visible()
        snap("01-overview")
        end_year = sidebar.get_by_role("slider").nth(1)
        end_year.press("ArrowLeft")
        expect(end_year).to_have_attribute("aria-valuetext", "2025")
        expect(main.get_by_text("11" if synthetic else "15,574", exact=True).first).to_be_visible()
        end_year.press("ArrowRight")
        expect(main.get_by_text("12" if synthetic else "15,727", exact=True).first).to_be_visible()
        region = sidebar.get_by_role("combobox", name="Affected regions")
        region.fill("Asia")
        page.get_by_role("option", name="Asia", exact=True).click()
        page.keyboard.press("Escape")
        expect(main.get_by_text("8" if synthetic else "6,598", exact=True).first).to_be_visible()
        country = sidebar.get_by_role("combobox").nth(2)
        country.fill("India")
        page.get_by_role("option", name="India (IND)", exact=True).click()
        page.keyboard.press("Escape")
        expect(main.get_by_text("3" if synthetic else "811", exact=True).first).to_be_visible()
        sidebar.get_by_test_id("stMultiSelect").nth(2).get_by_role("button", name="Clear all").click()
        sidebar.get_by_test_id("stMultiSelect").nth(1).get_by_role("button", name="Clear all").click()
        hazard = sidebar.get_by_role("combobox").nth(0)
        hazard.fill("Flood")
        page.get_by_role("option", name="Flood", exact=True).click()
        expect(main.get_by_text("6" if synthetic else "5,814", exact=True).first).to_be_visible()

        view("Frequency vs impact", "How does the ranking change with the impact measure?")
        main.get_by_text("Median", exact=True).first.click()
        expect(main.get_by_text("Flood leads this reported median", exact=False)).to_be_visible()
        snap("02-frequency")
        view("Trends", "Annual recorded frequency by hazard")
        expect(main.get_by_role("heading", name="Decades and reporting eras")).to_be_visible()
        snap("03-trends")
        view("Geography", "Recorded impacts by affected country")
        expect(page.locator("canvas.maplibregl-canvas")).to_be_visible(timeout=30000)
        main.get_by_role("tab", name="Unmapped records").click()
        expect(main.get_by_role("tab", name="Unmapped records")).to_have_attribute("aria-selected", "true")
        main.get_by_role("tab", name="Country rankings").click()
        page.locator("canvas.maplibregl-canvas").wait_for()
        snap("04-geography")

        view("Guided findings", "Follow the evidence")
        expect(main.get_by_text("Flood leads with", exact=False)).to_be_visible()
        for step, message in [
            ("Accumulated burden", "leads this total"),
            ("Typical severity", "leads this mean"),
            ("Time", "Compare complete years"),
            ("Geography", "These totals describe"),
            ("Limitations", "An unreported value remains"),
            ("Conclusion", "leads recorded frequency"),
        ]:
            main.get_by_role("radio", name=step, exact=True).click()
            expect(main.get_by_text(message, exact=False)).to_be_visible()
        main.get_by_role("radio", name="Accumulated burden", exact=True).click()
        expect(main.get_by_text("leads this total", exact=False)).to_be_visible()
        expect(main.locator(".plotly .main-svg").first).to_be_visible()
        snap("05-story")

        view("Machine learning", "Retrospective high-mortality ranking")
        expect(main.get_by_text("0.288", exact=True)).to_be_visible()
        main.get_by_role("combobox").first.click()
        page.get_by_role("option", name="Random forest", exact=True).click()
        expect(main.get_by_text("0.258", exact=True)).to_be_visible()
        snap("06-machine-learning")

        view("Explainable AI", "Explainable AI")
        expect(main.get_by_role("heading", name="Held-out permutation", exact=True)).to_be_visible()
        snap("07-global-xai")
        main.get_by_text("Local scenarios", exact=True).click()
        expect(main.get_by_text("Weighted surrogate R²", exact=False)).to_be_visible()
        main.get_by_role("combobox").first.click()
        page.get_by_role("option", name="Earthquake in the Americas scenario", exact=True).click()
        expect(main.get_by_text("9.4%", exact=True)).to_be_visible()
        snap("08-local-xai")
        main.get_by_text("Month PDP and ICE", exact=True).click()
        expect(main.get_by_text("Month is categorical", exact=False)).to_be_visible()
        snap("09-pdp-ice")

        view("Dimensionality reduction", "Compare impact projections")
        expect(main.get_by_text("84.8%", exact=True)).to_be_visible()
        main.get_by_role("radiogroup", name="PCA dimensions").get_by_text("3", exact=True).click()
        expect(main.locator(".gl-container canvas").first).to_be_visible(timeout=30000)
        snap("10-pca-3d")
        for method in ("t-SNE", "UMAP"):
            main.get_by_role("combobox").first.click()
            page.get_by_role("option", name=method, exact=True).click()
            expect(main.get_by_text("15-neighbor trustworthiness", exact=True)).to_be_visible()
            snap(f"11-{method.lower()}")

        view("Clustering and anomalies", "Cluster structure and anomalies")
        main.get_by_text("DBSCAN", exact=True).first.click()
        expect(main.get_by_text("DBSCAN returned one density-connected group", exact=False)).to_be_visible()
        main.get_by_text("Isolation Forest", exact=True).first.click()
        expect(main.get_by_text("Flagged profiles", exact=True)).to_be_visible()
        snap("12-clusters")
        view("Data quality and methodology", "Data quality and methodology")
        expect(main.get_by_text("27,962", exact=True)).to_be_visible()
        snap("13-data-quality")
        view("Overview", "Recorded events by hazard")
        expect(main.get_by_text("6" if synthetic else "5,814", exact=True).first).to_be_visible()
        assert not errors, errors
        browser.close()
    print(f"Passed ten-view Chromium acceptance, including selector changes and the map ({'synthetic' if synthetic else 'authorized'} scope).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8766")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()
    run(args.url, args.evidence, args.synthetic)
