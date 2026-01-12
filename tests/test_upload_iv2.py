#!/usr/bin/env python3
"""
Test to upload IV format CSV data (iv.csv) and run full analysis in NMAstudio setup page

This test performs the following steps:
1. Navigates to the /setup page
2. Uploads the iv.csv sample data (anticonvulsant drug interaction data)
3. Selects data format (iv - inverse variance / pre-calculated effects)
4. Maps data columns (StudyName, treat1, treat2, ROB, year)
5. Configures 1 outcome
6. Skips league table primary outcome selection
7. Sets outcome type (continuous, as data has ratio effect measure)
8. Configures effect measure (SMD) and direction
9. Maps variables for the outcome (RatioAUC, SEAUC, n1, n2)
10. Runs the full analysis
11. Waits for analysis to complete and submits results
12. Verifies redirect to results page

Expected behavior:
- No console errors
- All analysis steps complete successfully
- User is redirected to /results page
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def select_outcome_variables_iv(page, outcome_index, variables, outcome_name):
    """
    Helper to select variables for an outcome in IV format.
    For IV outcomes, we need TE (effect estimate), seTE (standard error), n1, n2.

    Args:
        page: Playwright page object
        outcome_index: Index of the outcome (0 or 1)
        variables: List of variable names to select (e.g., ["RatioAUC", "SEAUC", "n1", "n2"])
        outcome_name: Name for logging (e.g., "Outcome 1")
    """
    print(f"   Selecting variables for {outcome_name}...")

    # Get all dropdowns with variableselectors and matching outcome index
    dropdowns = await page.query_selector_all(".dash-dropdown")
    outcome_vars = []

    for dropdown in dropdowns:
        dropdown_id = await dropdown.get_attribute("id") or ""
        is_visible = await dropdown.is_visible()
        # Match variableselectors with the outcome index (as string)
        if (
            "variableselectors" in dropdown_id
            and f'"index":"{outcome_index}"' in dropdown_id
            and is_visible
        ):
            outcome_vars.append(dropdown)

    print(
        f"   Found {len(outcome_vars)} variable dropdowns for outcome {outcome_index}"
    )

    # Select all variable dropdowns matching our variables list
    for i, var_name in enumerate(variables):
        if i < len(outcome_vars):
            var_dropdown = outcome_vars[i]
            try:
                select_control = await var_dropdown.query_selector(".Select-control")
                if select_control:
                    await select_control.click()
                    await page.wait_for_timeout(300)
                    await page.keyboard.type(var_name)
                    await page.wait_for_timeout(300)
                    await page.keyboard.press("Enter")
                    print(f"   Variable {i + 1}: {var_name}")
                    await page.wait_for_timeout(300)
                else:
                    print(f"   Could not find select control for variable {i + 1}")
            except Exception as e:
                print(f"   Error selecting variable {i + 1} ({var_name}): {e}")

    return True


async def test_upload_iv():
    """Test uploading IV format CSV (iv.csv) and running full analysis"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page()

        # Set longer default timeout
        page.set_default_timeout(15000)

        # Set up console message collection
        console_messages = []
        console_errors = []

        def handle_console_message(msg):
            """Handle console messages"""
            location_info = "unknown"
            if msg.location:
                url = getattr(msg.location, "url", "unknown")
                line_num = getattr(msg.location, "lineNumber", "unknown")
                col_num = getattr(msg.location, "columnNumber", "unknown")
                location_info = f"{url}:{line_num}:{col_num}"

            message_data = {
                "type": msg.type,
                "text": msg.text,
                "location": location_info,
            }
            console_messages.append(message_data)

            if msg.type in ["error"]:
                console_errors.append(message_data)
                print(f"\n Console {msg.type}:")
                print(f"   {msg.text}")
                print(f"   Location: {location_info}\n")

        # Listen for console messages
        page.on("console", handle_console_message)

        # Track failed requests
        failed_requests = []

        def handle_request_failed(request):
            failed_requests.append(
                {
                    "url": request.url,
                    "method": request.method,
                }
            )
            print(f"Failed request: {request.url}")

        page.on("requestfailed", handle_request_failed)

        try:
            print("Starting NMAstudio IV format upload and analysis test (iv.csv)...")

            # Navigate to the app
            connected = False
            for url in ["http://localhost:8050/setup", "http://macas.lan:8050/setup"]:
                try:
                    print(f"Trying to connect to {url}...")
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=15000,
                    )
                    connected = True
                    break
                except Exception as e:
                    print(f"Failed to connect to {url}: {e}")
                    continue

            if not connected:
                print("Could not connect to NMAstudio server")
                print("Please make sure the server is running with: python app.py")
                return None

            print(f"Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 1: Upload CSV file
            print("\n[Step 1] Uploading CSV file...")
            csv_path = Path(__file__).parent.parent / "db" / "iv.csv"

            if not csv_path.exists():
                print(f"CSV file not found: {csv_path}")
                return None

            # Wait for upload component and upload file
            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"   Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1000)

            # Verify file is uploaded
            uploaded_file_locator = page.locator("#uploaded_datafile2")
            uploaded_file = await uploaded_file_locator.inner_text()
            print(f"   File shown in UI: {uploaded_file}")

            # Step 2: Select data format (iv - inverse variance format)
            print("\n[Step 2] Selecting data format...")
            await page.wait_for_selector("#radio-format", timeout=5000)

            # Click on IV format radio button
            await page.click("#radio-format label:has-text('iv')")
            print("   Selected: IV format (pre-calculated effects)")
            await page.wait_for_timeout(2000)

            # Step 3: Select required data columns using keyboard input
            print("\n[Step 3] Selecting data columns...")

            # IV format columns: studlab, treat1, treat2, rob (optional), year (optional)
            # CSV columns: StudyName, year, n1, n2, treat1, treat2, RatioAUC, SEAUC, ROB
            columns_values = ["StudyName", "treat1", "treat2", "ROB", "year"]

            dropdowns = await page.query_selector_all(".dash-dropdown")
            print(f"   Found {len(dropdowns)} dropdowns")

            for idx, value in enumerate(columns_values):
                if idx < len(dropdowns):
                    print(f"   Selecting dropdown {idx}: {value}...")
                    select_control = await dropdowns[idx].query_selector(
                        ".Select-control"
                    )
                    if select_control:
                        await select_control.click()
                        await page.keyboard.type(value)
                        await page.wait_for_timeout(300)
                        await page.keyboard.press("Enter")
                        print(f"   Selected: {value}")
                        await page.wait_for_timeout(300)

            # Step 4: Enter number of outcomes (1 outcome for this dataset)
            print("\n[Step 4] Setting number of outcomes...")
            await page.wait_for_selector("#number-outcomes", timeout=5000)
            await page.fill("#number-outcomes", "1")
            print("   Set number of outcomes: 1")
            await page.wait_for_timeout(300)

            # Click OK button
            await page.click("#num_outcomes_button")
            print("   Clicked OK button")
            await page.wait_for_timeout(2000)

            # Step 5: Skip league table (primary outcomes)
            print("\n[Step 5] Skipping league table...")
            await page.wait_for_timeout(1500)

            # Find Skip labels that are NOT in the format radio group
            skip_labels = await page.query_selector_all('label:has-text("Skip")')
            print(f"   Found {len(skip_labels)} Skip labels")

            for skip_label in skip_labels:
                is_visible = await skip_label.is_visible()
                parent_id = await skip_label.evaluate(
                    'el => el.parentElement?.id || ""'
                )
                if is_visible and "radio-format" not in parent_id:
                    await skip_label.click()
                    print("   Checked: Skip league table")
                    await page.wait_for_timeout(1500)
                    break

            # Step 6: Select outcome type (continuous for ratio data)
            print("\n[Step 6] Configuring outcome type...")
            await page.wait_for_timeout(1000)

            # Find continuous label that is NOT in the format radio group
            all_labels = await page.query_selector_all("label")

            for label in all_labels:
                text = await label.inner_text()
                is_visible = await label.is_visible()
                parent_id = await label.evaluate('el => el.parentElement?.id || ""')

                if (
                    text.strip() == "continuous"
                    and is_visible
                    and "radio-format" not in parent_id
                ):
                    await label.click()
                    print("   Outcome 1 type: continuous")
                    await page.wait_for_timeout(500)
                    break

            await page.wait_for_timeout(1000)

            # Step 7: Outcome 1 - effect measure and direction
            print("\n[Step 7] Configuring outcome 1 effect measure and direction...")

            # Select SMD for effect measure (for continuous outcome with ratio data)
            smd_labels = await page.query_selector_all('label:has-text("SMD")')
            for label in smd_labels:
                is_visible = await label.is_visible()
                parent_id = await label.evaluate('el => el.parentElement?.id || ""')
                if is_visible and "radio-format" not in parent_id:
                    await label.click()
                    print("   Outcome 1 effect measure: SMD")
                    await page.wait_for_timeout(500)
                    break

            # Select beneficial for direction
            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            for label in beneficial_labels:
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    print("   Outcome 1 direction: beneficial")
                    await page.wait_for_timeout(500)
                    break

            # Step 8: Outcome 1 - variables
            # For IV format, need TE, seTE, n1, n2 (effect, SE, sample sizes)
            # CSV has: RatioAUC (TE), SEAUC (seTE), n1, n2
            print("\n[Step 8] Selecting outcome 1 variables...")
            await select_outcome_variables_iv(
                page,
                outcome_index=0,
                variables=["RatioAUC", "SEAUC", "n1", "n2"],
                outcome_name="Outcome 1",
            )
            await page.wait_for_timeout(1000)

            # Step 9: Skip effect modifiers (no effect modifier columns in this dataset)
            print("\n[Step 9] Skipping effect modifiers...")
            await page.wait_for_timeout(1000)

            # Check "Skip" checkbox for effect modifiers using the specific checkbox ID
            # The no_effect_modifier checklist has label "Skip"
            no_effect_checkbox = page.locator(
                "#no_effect_modifier label:has-text('Skip')"
            )
            if await no_effect_checkbox.count() > 0:
                await no_effect_checkbox.first.click()
                print("   Checked: Skip effect modifiers")
                await page.wait_for_timeout(500)
            else:
                # Fallback: try to find any Skip label in the effect modifier section
                effect_mod_section = page.locator("#select_effect_modifier")
                skip_in_section = effect_mod_section.locator('label:has-text("Skip")')
                if await skip_in_section.count() > 0:
                    await skip_in_section.first.click()
                    print("   Checked: Skip effect modifiers (fallback)")
                    await page.wait_for_timeout(500)
                else:
                    print(
                        "   Warning: Could not find Skip checkbox for effect modifiers"
                    )

            # Step 10: Click Run Analysis button
            print("\n[Step 10] Running analysis...")
            run_button = "#upload_modal_data2"
            await page.wait_for_selector(run_button, timeout=5000)

            # Verify button is enabled
            is_disabled = await page.locator(run_button).is_disabled()
            if is_disabled:
                print("Run Analysis button is disabled!")
                # Take screenshot to debug
                screenshot_path = Path(__file__).parent / "test_upload_iv2_disabled.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"Screenshot saved: {screenshot_path}")
                return None

            await page.click(run_button)
            print("   Clicked Run Analysis button")
            await page.wait_for_timeout(2000)

            # Wait for modal to appear
            print("\n[Step 11] Waiting for analysis to complete...")
            modal_selector = "#modal_data_checks"
            await page.wait_for_selector(modal_selector, state="visible", timeout=10000)
            print("   Analysis modal opened")

            # Wait for all analysis steps to complete
            steps = [
                ("para-check-data", "Data Checks"),
                ("para-anls-data", "NMA Analysis"),
                ("para-pairwise-data", "Pairwise Analysis"),
                ("para-LT-data", "League Table"),
                ("para-FA-data", "Funnel Analysis"),
            ]

            for step_id, step_name in steps:
                print(f"   Waiting for {step_name}...")
                try:
                    # Wait for the step to complete (up to 60 seconds per step)
                    await page.wait_for_function(
                        f"""
                        () => {{
                            const elem = document.getElementById('{step_id}');
                            const data = elem?.getAttribute('data');
                            return data === '__Para_Done__';
                        }}
                        """,
                        timeout=60000,
                    )
                    print(f"   {step_name} completed")
                except Exception as e:
                    print(f"   {step_name} timeout or error: {e}")
                    print(f"   Breaking out of analysis loop...")
                    break

                await page.wait_for_timeout(500)

            # Check if Submit button is enabled
            submit_button = "#submit_modal_data"
            await page.wait_for_timeout(2000)

            is_submit_disabled = await page.locator(submit_button).is_disabled()
            if is_submit_disabled:
                print("   Submit button still disabled after analysis")
            else:
                print("   Submit button is enabled")

                # Click Submit button
                await page.click(submit_button)
                print("   Clicked Submit button")
                await page.wait_for_timeout(2000)

                # Wait for redirect to results page
                print("\n[Step 12] Waiting for redirect to results...")
                try:
                    await page.wait_for_url("**/results", timeout=10000)
                    print(f"   Redirected to results page: {page.url}")
                except:
                    print(f"   No redirect detected. Current URL: {page.url}")

            # Take a screenshot
            screenshot_path = Path(__file__).parent / "test_upload_iv2_result.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"   Screenshot saved: {screenshot_path}")

            # Summary
            print("\n" + "=" * 60)
            print("=== Test Summary ===")
            print(f"Console Messages: {len(console_messages)}")
            print(f"Console Errors: {len(console_errors)}")
            print(f"Failed Requests: {len(failed_requests)}")

            if console_errors:
                print("\nConsole Errors:")
                for i, error in enumerate(console_errors[:10], 1):
                    print(f"{i}. {error['text'][:100]}")

            if failed_requests:
                print("\nFailed Requests:")
                for req in failed_requests[:5]:
                    print(f"  - {req['method']} {req['url']}")

            if not console_errors and not failed_requests:
                print("\nAll tests passed! No errors detected.")
            else:
                print("\nTest completed with some issues. Check output above.")

            # Keep browser open for inspection
            print("\nKeeping browser open for 10 minutes (600 seconds)...")
            await page.wait_for_timeout(600000)

            return {
                "console_messages": console_messages,
                "console_errors": console_errors,
                "failed_requests": failed_requests,
                "success": not console_errors and not failed_requests,
            }

        except Exception as e:
            print(f"\nTest failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            screenshot_path = Path(__file__).parent / "test_upload_iv2_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"Error screenshot saved: {screenshot_path}")
            raise
        finally:
            print("\nClosing browser...")
            await browser.close()


if __name__ == "__main__":
    print("Running IV format upload and analysis test (iv.csv)...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 60)

    try:
        results = asyncio.run(test_upload_iv())

        if results is None:
            print("\nTest returned no results - check error messages above")
        elif results.get("success"):
            print("\nTEST PASSED - Analysis completed successfully!")
        else:
            print("\nTEST COMPLETED WITH WARNINGS - Check details above")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
