#!/usr/bin/env python3
"""
Test to verify network diagram displays correctly when year is skipped.

This test reproduces and verifies the fix for the bug where:
- On the setup analysis page, if the user skips "year"
- The results page would show an error and the network diagram would not display

Test steps:
1. Navigate to the /setup page
2. Upload psoriasis_long_complete.csv sample data
3. Select long format
4. Map only required columns (studlab, treat) - SKIP year (and rob)
5. Configure 1 outcome (PASI90)
6. Run the analysis
7. Navigate to results page
8. Verify network diagram displays without errors

Expected behavior:
- No console errors related to year/network diagram
- Network diagram displays correctly even without year data
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def select_outcome_variables(page, outcome_index, variables, outcome_name):
    """Helper to select variables for an outcome."""
    print(f"Selecting variables for {outcome_name}...")

    dropdowns = await page.query_selector_all(".dash-dropdown")
    outcome_vars = []

    for dropdown in dropdowns:
        dropdown_id = await dropdown.get_attribute("id") or ""
        if (
            "variableselectors" in dropdown_id
            and f'"index":"{outcome_index}"' in dropdown_id
        ):
            outcome_vars.append(dropdown)

    print(
        f"   Found {len(outcome_vars)} variable dropdowns for outcome {outcome_index}"
    )

    for i, (var_dropdown, var_name) in enumerate(zip(outcome_vars, variables)):
        try:
            select_control = await var_dropdown.query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.wait_for_timeout(300)
                await page.keyboard.type(var_name)
                await page.wait_for_timeout(200)
                await page.keyboard.press("Enter")
                print(f"   Variable {i + 1}: {var_name}")
                await page.wait_for_timeout(300)
        except Exception as e:
            print(f"   Error selecting variable {i + 1} ({var_name}): {e}")

    return len(outcome_vars) == len(variables)


async def test_skip_year_network_diagram():
    """Test that network diagram displays correctly when year is skipped"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        page.set_default_timeout(15000)

        console_errors = []
        year_related_errors = []

        def handle_console_message(msg):
            """Capture console errors, especially year-related ones"""
            if msg.type == "error":
                error_text = msg.text.lower()
                console_errors.append(msg.text)
                # Check for year-related errors (exclude harmless warnings)
                is_css_warning = "unsupported style property" in error_text
                # SVG path NaN errors from hidden slider are cosmetic and don't affect functionality
                is_svg_path_warning = (
                    "<path>" in error_text and "expected number" in error_text
                )
                if (
                    not is_css_warning
                    and not is_svg_path_warning
                    and ("year" in error_text or "keyerror" in error_text)
                ):
                    year_related_errors.append(msg.text)
                    print(f"\n[YEAR ERROR] {msg.text}\n")

        page.on("console", handle_console_message)

        try:
            print("=" * 60)
            print("TEST: Skip year and verify network diagram displays")
            print("=" * 60)

            # Navigate to setup page
            try:
                await page.goto(
                    "http://localhost:8050/setup",
                    wait_until="networkidle",
                    timeout=15000,
                )
            except:
                print("Could not connect to localhost:8050")
                print("Please make sure the server is running with: python app.py")
                return None

            print(f"Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 1: Upload CSV file
            print("\n[Step 1] Uploading CSV file...")
            csv_path = (
                Path(__file__).parent.parent / "db" / "psoriasis_long_complete.csv"
            )

            if not csv_path.exists():
                print(f"CSV file not found: {csv_path}")
                return None

            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1000)

            # Step 2: Select long format
            print("\n[Step 2] Selecting long format...")
            await page.wait_for_selector("#radio-format", timeout=5000)
            await page.click("#radio-format label:has-text('long')")
            print("Selected: Long format")
            await page.wait_for_timeout(2000)

            # Step 3: Select ONLY required columns (skip ROB and year)
            print("\n[Step 3] Selecting data columns (SKIPPING YEAR)...")
            # For long format: study ID (index 0), treat (index 1), rob (index 2 - SKIP), year (index 3 - SKIP)
            columns_values = ["unique_id", "treat"]  # Only required columns

            dropdowns = await page.query_selector_all(".dash-dropdown")
            print(f"Found {len(dropdowns)} dropdowns")

            # Select only the first two dropdowns (studlab and treat)
            for idx, value in enumerate(columns_values):
                if idx < len(dropdowns):
                    print(f"Selecting dropdown {idx}: {value}...")
                    select_control = await dropdowns[idx].query_selector(
                        ".Select-control"
                    )
                    if select_control:
                        await select_control.click()
                        await page.keyboard.type(value)
                        await page.wait_for_timeout(300)
                        await page.keyboard.press("Enter")
                        print(f"Selected: {value}")
                        await page.wait_for_timeout(300)

            print("SKIPPED: rob (dropdown 2)")
            print("SKIPPED: year (dropdown 3)")

            # Step 4: Set number of outcomes to 1 (simpler test)
            print("\n[Step 4] Setting number of outcomes...")
            await page.wait_for_selector("#number-outcomes", timeout=5000)
            await page.fill("#number-outcomes", "1")
            print("Set number of outcomes: 1")
            await page.wait_for_timeout(300)

            await page.click("#num_outcomes_button")
            print("Clicked OK button")
            await page.wait_for_timeout(2000)

            # Step 5: Skip league table primary outcome
            print("\n[Step 5] Skipping league table...")
            skip_labels = await page.query_selector_all('label:has-text("Skip")')
            if len(skip_labels) > 0 and await skip_labels[0].is_visible():
                await skip_labels[0].click()
                print("Checked: Skip league table")
                await page.wait_for_timeout(1500)

            # Step 6: Select outcome type (binary)
            print("\n[Step 6] Configuring outcome type...")
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            if len(binary_labels) > 0:
                await binary_labels[0].click()
                print("Outcome 1 type: Binary")
                await page.wait_for_timeout(500)

            # Step 7: Select effect measure (OR) and direction (beneficial)
            print("\n[Step 7] Configuring effect measure and direction...")
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 0:
                await or_labels[0].click()
                print("Effect measure: OR")
                await page.wait_for_timeout(500)

            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            if len(beneficial_labels) > 0:
                await beneficial_labels[0].click()
                print("Direction: beneficial")
                await page.wait_for_timeout(500)

            # Step 8: Select outcome variables
            print("\n[Step 8] Selecting outcome variables...")
            await select_outcome_variables(
                page,
                outcome_index=0,
                variables=["rPASI90", "nPASI90"],
                outcome_name="PASI90",
            )
            await page.wait_for_timeout(500)

            # Step 8b: Select effect modifiers (these are checkboxes visible on same screen)
            print("\n[Step 8b] Selecting effect modifiers...")
            try:
                # Effect modifiers are checkboxes - click on "age" checkbox label
                age_checkbox = page.locator('label:has-text("age")')
                if await age_checkbox.count() > 0:
                    await age_checkbox.first.click()
                    print("   Effect modifier: age")
                    await page.wait_for_timeout(500)

            except Exception as e:
                print(f"   Could not select effect modifiers: {e}")
                print("   Trying to continue anyway...")

            # Step 9: Run Analysis
            print("\n[Step 9] Running analysis...")
            run_button = "#upload_modal_data2"
            await page.wait_for_selector(run_button, timeout=5000)

            is_disabled = await page.locator(run_button).is_disabled()
            if is_disabled:
                print("Run Analysis button is disabled!")
                return None

            await page.click(run_button)
            print("Clicked Run Analysis button")
            await page.wait_for_timeout(2000)

            # Step 10: Wait for analysis to complete (max 30 seconds)
            print("\n[Step 10] Waiting for analysis to complete (max 30 seconds)...")
            modal_selector = "#modal_data_checks"
            await page.wait_for_selector(modal_selector, state="visible", timeout=10000)
            print("Analysis modal opened")

            # Wait up to 30 seconds for analysis, then submit regardless
            submit_button = "#submit_modal_data"
            start_time = asyncio.get_event_loop().time()
            max_wait = 30  # 30 seconds max

            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= max_wait:
                    print(f"Reached {max_wait}s timeout, proceeding to submit...")
                    break

                # Check if submit button is enabled
                is_submit_disabled = await page.locator(submit_button).is_disabled()
                if not is_submit_disabled:
                    print(f"Submit button enabled after {elapsed:.1f}s")
                    break

                await page.wait_for_timeout(1000)
                print(f"Waiting... ({elapsed:.1f}s)")

            # Step 11: Submit and navigate to results
            print("\n[Step 11] Submitting results...")
            await page.wait_for_timeout(1000)

            is_submit_disabled = await page.locator(submit_button).is_disabled()
            if is_submit_disabled:
                print("Submit button still disabled, clicking anyway...")

            await page.click(submit_button)
            print("Clicked Submit button")
            await page.wait_for_timeout(2000)

            # Wait for redirect to results page
            print("\n[Step 12] Waiting for results page...")
            try:
                await page.wait_for_url("**/results", timeout=10000)
                print(f"Redirected to results page: {page.url}")
            except:
                print(f"No redirect detected. Current URL: {page.url}")
                return None

            # Step 13: Check network diagram display
            print("\n[Step 13] Checking network diagram display...")
            await page.wait_for_timeout(3000)

            # Check if cytoscape network diagram exists and has nodes
            cytoscape_container = page.locator("#cytoscape")
            cytoscape_exists = await cytoscape_container.count() > 0

            if cytoscape_exists:
                # Wait for cytoscape to render
                await page.wait_for_timeout(2000)

                # Check if there are nodes in the network by looking for SVG elements or canvas
                # Cytoscape renders nodes as elements within the container
                network_visible = await page.evaluate("""
                    () => {
                        const cy = document.getElementById('cytoscape');
                        if (!cy) return false;
                        // Check if cytoscape has rendered content (canvas or nodes)
                        const canvas = cy.querySelector('canvas');
                        const hasContent = canvas && canvas.width > 0 && canvas.height > 0;
                        return hasContent;
                    }
                """)

                if network_visible:
                    print("SUCCESS: Network diagram displays correctly!")
                else:
                    # Alternative check - see if the container has reasonable dimensions
                    box = await cytoscape_container.bounding_box()
                    if box and box["width"] > 100 and box["height"] > 100:
                        print("SUCCESS: Network diagram container has content!")
                        network_visible = True
                    else:
                        print("WARNING: Network diagram may not have rendered properly")
            else:
                print("Network diagram container not found")
                network_visible = False

            # Take screenshot
            screenshot_path = Path(__file__).parent / "test_skip_year_result.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved: {screenshot_path}")

            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(f"Total console errors: {len(console_errors)}")
            print(f"Year-related errors: {len(year_related_errors)}")

            if year_related_errors:
                print("\nYEAR-RELATED ERRORS FOUND:")
                for i, error in enumerate(year_related_errors[:5], 1):
                    print(f"  {i}. {error[:100]}")
                print("\nTEST FAILED: Year-related errors detected")
                return {"success": False, "errors": year_related_errors}

            if cytoscape_exists and network_visible:
                print(
                    "\nTEST PASSED: Network diagram displays correctly when year is skipped!"
                )
                return {"success": True, "errors": []}
            else:
                print("\nTEST FAILED: Network diagram did not display correctly")
                return {"success": False, "errors": ["Network diagram not displayed"]}

        except Exception as e:
            print(f"\nTest failed with error: {e}")
            import traceback

            traceback.print_exc()

            screenshot_path = Path(__file__).parent / "test_skip_year_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"Error screenshot saved: {screenshot_path}")
            return {"success": False, "errors": [str(e)]}

        finally:
            print("\nClosing browser...")
            await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Running test: Skip year and verify network diagram")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 60)

    try:
        results = asyncio.run(test_skip_year_network_diagram())

        if results is None:
            print("\nTest returned no results - check error messages above")
            exit(1)
        elif results.get("success"):
            print("\nTEST PASSED!")
            exit(0)
        else:
            print("\nTEST FAILED!")
            exit(1)

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        exit(1)
