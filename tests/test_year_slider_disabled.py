#!/usr/bin/env python3
"""
Test to verify year slider is hidden when year column is not filled.

Expected behavior:
- Year slider should be hidden when year is not mapped
- All studies should be shown (no filtering based on year)
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def test_year_slider_hidden():
    """Test that year slider is hidden when year column is not filled"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=30)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        try:
            print("=" * 60)
            print("TEST: Year slider hidden when year not filled")
            print("=" * 60)

            # Navigate to setup page
            await page.goto("http://localhost:8050/setup", wait_until="networkidle")
            print(f"Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 1: Upload CSV file
            print("\n[Step 1] Uploading CSV file...")
            csv_path = (
                Path(__file__).parent.parent / "db" / "psoriasis_long_complete.csv"
            )
            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1500)

            # Step 2: Select long format
            print("\n[Step 2] Selecting long format...")
            await page.click("#radio-format label:has-text('long')")
            print("Selected: Long format")
            await page.wait_for_timeout(2000)

            # Step 3: Select ONLY required columns (skip year)
            print("\n[Step 3] Selecting data columns (SKIPPING YEAR)...")
            dropdowns = await page.query_selector_all(".dash-dropdown")
            columns_values = ["unique_id", "treat"]

            for idx, value in enumerate(columns_values):
                if idx < len(dropdowns):
                    select_control = await dropdowns[idx].query_selector(
                        ".Select-control"
                    )
                    if select_control:
                        await select_control.click()
                        await page.keyboard.type(value)
                        await page.wait_for_timeout(300)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(300)
            print("Selected: unique_id, treat (SKIPPED year)")

            # Step 4: Set number of outcomes
            print("\n[Step 4] Setting up outcomes...")
            await page.fill("#number-outcomes", "1")
            await page.click("#num_outcomes_button")
            await page.wait_for_timeout(2000)

            # Step 5: Skip league table
            skip_labels = await page.query_selector_all('label:has-text("Skip")')
            if len(skip_labels) > 0:
                await skip_labels[0].click()
                await page.wait_for_timeout(1000)

            # Step 6: Select outcome type (binary)
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            if len(binary_labels) > 0:
                await binary_labels[0].click()
                await page.wait_for_timeout(500)

            # Step 7: Select effect measure and direction
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 0:
                await or_labels[0].click()

            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            if len(beneficial_labels) > 0:
                await beneficial_labels[0].click()
            await page.wait_for_timeout(500)

            # Step 8: Select outcome variables
            print("\n[Step 5] Selecting outcome variables...")
            dropdowns = await page.query_selector_all(".dash-dropdown")
            outcome_vars = []
            for dropdown in dropdowns:
                dropdown_id = await dropdown.get_attribute("id") or ""
                if "variableselectors" in dropdown_id and '"index":"0"' in dropdown_id:
                    outcome_vars.append(dropdown)

            variables = ["rPASI90", "nPASI90"]
            for i, (var_dropdown, var_name) in enumerate(zip(outcome_vars, variables)):
                select_control = await var_dropdown.query_selector(".Select-control")
                if select_control:
                    await select_control.click()
                    await page.wait_for_timeout(300)
                    await page.keyboard.type(var_name)
                    await page.wait_for_timeout(200)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(300)
            print("Selected outcome variables")

            # Step 9: Select effect modifier
            age_checkbox = page.locator('label:has-text("age")')
            if await age_checkbox.count() > 0:
                await age_checkbox.first.click()
                await page.wait_for_timeout(500)

            # Step 10: Run Analysis
            print("\n[Step 6] Running analysis...")
            await page.click("#upload_modal_data2")
            await page.wait_for_timeout(2000)

            # Wait for analysis steps
            await page.wait_for_selector(
                "#modal_data_checks", state="visible", timeout=10000
            )

            for step_id in [
                "para-check-data",
                "para-anls-data",
                "para-pairwise-data",
                "para-LT-data",
                "para-FA-data",
            ]:
                try:
                    await page.wait_for_function(
                        f"() => document.getElementById('{step_id}')?.getAttribute('data') === '__Para_Done__'",
                        timeout=60000,
                    )
                except Exception:
                    break
                await page.wait_for_timeout(300)

            # Submit
            print("\n[Step 7] Submitting...")
            await page.wait_for_timeout(2000)
            await page.click("#submit_modal_data")
            await page.wait_for_timeout(2000)

            # Wait for results page
            await page.wait_for_url("**/results", timeout=15000)
            print(f"Redirected to: {page.url}")
            await page.wait_for_timeout(3000)

            # Check slider visibility
            print("\n[Step 8] Checking slider visibility...")
            slider_container = page.locator("#slider-container")
            is_visible = await slider_container.is_visible()
            print(f"Slider container visible: {is_visible}")

            # Take screenshot
            screenshot_path = Path(__file__).parent / "test_year_slider_result.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"Screenshot: {screenshot_path}")

            # Result
            if not is_visible:
                print("\n✅ TEST PASSED: Slider is hidden!")
                return {"success": True}
            else:
                print("\n❌ TEST FAILED: Slider is visible but should be hidden!")
                return {"success": False}

        except Exception as e:
            print(f"\nTest error: {e}")
            import traceback

            traceback.print_exc()
            screenshot_path = Path(__file__).parent / "test_year_slider_error.png"
            await page.screenshot(path=str(screenshot_path))
            return {"success": False, "error": str(e)}

        finally:
            await browser.close()


if __name__ == "__main__":
    results = asyncio.run(test_year_slider_hidden())
    exit(0 if results and results.get("success") else 1)
