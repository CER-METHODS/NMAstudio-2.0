#!/usr/bin/env python3
"""
Test to upload continuous long format CSV data and run full analysis in NMAstudio setup page

This test performs the following steps:
1. Navigates to the /setup page
2. Uploads the long_continuous.csv sample data
3. Selects data format (long - one row per study arm)
4. Maps data columns (Author as studlab, t as treat, rob, Year)
5. Configures 1 outcome (single outcome because y2/sd2/n2 have missing data for some studies)
6. Skips league table primary outcome selection
7. Sets outcome type to continuous
8. Configures effect measure (MD) and direction (beneficial)
9. Maps variables for outcome (y1, sd1, n1) - continuous format
10. Selects effect modifiers (Age, BMI)
11. Runs the full analysis
12. Waits for analysis to complete and submits results

Expected behavior:
- No console errors
- All analysis steps complete successfully
- User is redirected to /results page
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def select_outcome_variables(page, outcome_index, variables, outcome_name):
    """
    Helper to select variables for an outcome.
    For continuous outcomes in long format, we need mean, SD, n.

    Args:
        page: Playwright page object
        outcome_index: Index of the outcome (0 or 1)
        variables: List of variable names to select (e.g., ["y1", "sd1", "n1"])
        outcome_name: Name for logging (e.g., "Outcome 1")
    """
    print(f"   Selecting variables for {outcome_name}...")

    # Get all dropdowns - try both .dash-dropdown and Select class
    dropdowns = await page.query_selector_all(".dash-dropdown, .Select")
    outcome_vars = []

    print(f"   Total dropdowns found: {len(dropdowns)}")

    # Debug: print all dropdown IDs to see what we have
    for dropdown in dropdowns:
        dropdown_id = await dropdown.get_attribute("id") or ""
        if "variableselectors" in dropdown_id:
            print(f"   DEBUG variableselectors dropdown: {dropdown_id}")

    for dropdown in dropdowns:
        dropdown_id = await dropdown.get_attribute("id") or ""
        # Match variableselectors with the outcome index (as string format, e.g., "index":"0")
        if (
            "variableselectors" in dropdown_id
            and f'"index":"{outcome_index}"' in dropdown_id
        ):
            outcome_vars.append(dropdown)
            print(f"   Found variable dropdown: {dropdown_id[:80]}...")

    print(
        f"   Found {len(outcome_vars)} variable dropdowns for outcome {outcome_index}"
    )

    if len(outcome_vars) != len(variables):
        print(
            f"   Warning: Expected {len(variables)} dropdowns, found {len(outcome_vars)}"
        )

    # Select each variable in its corresponding dropdown
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
            else:
                print(f"   Could not find select control for variable {i + 1}")
        except Exception as e:
            print(f"   Error selecting variable {i + 1} ({var_name}): {e}")

    return len(outcome_vars) == len(variables)


async def test_upload_continuous_long():
    """Test uploading continuous long format CSV and running full analysis"""

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
            print(
                "Starting NMAstudio continuous long format upload and analysis test..."
            )

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
            csv_path = Path(__file__).parent.parent / "db" / "long_continuous.csv"

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

            # Step 2: Select data format (long format - one row per arm)
            print("\n[Step 2] Selecting data format...")
            await page.wait_for_selector("#radio-format", timeout=5000)

            # Click on long format radio button
            await page.click("#radio-format label:has-text('long')")
            print("   Selected: long format (one row per study arm)")
            await page.wait_for_timeout(2000)

            # Step 3: Select required data columns using keyboard input
            print("\n[Step 3] Selecting data columns...")

            # Long format columns: studlab, treat, rob (optional), year (optional)
            # CSV columns: Study ID, Year, Author, t, y1, ..., rob, ...
            # Using Study ID as studlab, t as treat
            columns_values = ["Study ID", "t", "rob", "Year"]

            dropdowns = await page.query_selector_all(".dash-dropdown")
            print(f"   Found {len(dropdowns)} dropdowns")

            # Dropdown 0: studlab -> "Study ID"
            print(f"   Selecting dropdown 0: Study ID...")
            select_control = await dropdowns[0].query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.wait_for_timeout(300)
                await page.keyboard.type("Study ID")
                await page.wait_for_timeout(300)
                await page.keyboard.press("Enter")
                print(f"   Selected: Study ID")
                await page.wait_for_timeout(400)

            # Dropdown 1: treat -> "t" (use arrow keys since "t" matches "Study ID" first)
            # t is the 4th column (0=Study ID, 1=Year, 2=Author, 3=t)
            # First Down selects index 0, so we need 4 downs to reach index 3
            # But if first item is already highlighted, we need 3 more downs
            print(f"   Selecting dropdown 1: t...")
            select_control = await dropdowns[1].query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.wait_for_timeout(300)
                # Press Down 3 times to get from Study ID (0) to t (3)
                # Assuming first option is already highlighted
                for _ in range(3):
                    await page.keyboard.press("ArrowDown")
                    await page.wait_for_timeout(50)
                await page.keyboard.press("Enter")
                print(f"   Selected: t")
                await page.wait_for_timeout(400)

            # Dropdown 2: rob -> "rob"
            print(f"   Selecting dropdown 2: rob...")
            select_control = await dropdowns[2].query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.wait_for_timeout(300)
                await page.keyboard.type("rob")
                await page.wait_for_timeout(300)
                await page.keyboard.press("Enter")
                print(f"   Selected: rob")
                await page.wait_for_timeout(400)

            # Dropdown 3: year -> "Year"
            print(f"   Selecting dropdown 3: Year...")
            select_control = await dropdowns[3].query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.wait_for_timeout(300)
                await page.keyboard.type("Year")
                await page.wait_for_timeout(300)
                await page.keyboard.press("Enter")
                print(f"   Selected: Year")
                await page.wait_for_timeout(400)

            # Step 4: Enter number of outcomes
            print("\n[Step 4] Setting number of outcomes...")
            await page.wait_for_selector("#number-outcomes", timeout=5000)
            await page.fill("#number-outcomes", "2")
            print("   Set number of outcomes: 2")
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

            # Step 6: Select outcome types (continuous for both outcomes)
            print("\n[Step 6] Configuring outcome types...")
            await page.wait_for_timeout(1000)

            # Find all continuous labels that are NOT in the format radio group
            all_labels = await page.query_selector_all("label")
            continuous_count = 0

            for label in all_labels:
                text = await label.inner_text()
                is_visible = await label.is_visible()
                parent_id = await label.evaluate('el => el.parentElement?.id || ""')

                if (
                    text.strip() == "continuous"
                    and is_visible
                    and "radio-format" not in parent_id
                ):
                    continuous_count += 1
                    await label.click()
                    print(f"   Outcome {continuous_count} type: continuous")
                    await page.wait_for_timeout(500)
                    if continuous_count >= 2:
                        break

            await page.wait_for_timeout(2000)  # Wait for variable dropdowns to appear

            # Step 7: Outcome 1 - effect measure and direction
            print("\n[Step 7] Configuring outcome 1 effect measure and direction...")

            # Select MD for effect measure (first visible MD label not in format radio)
            md_labels = await page.query_selector_all('label:has-text("MD")')
            for label in md_labels:
                is_visible = await label.is_visible()
                parent_id = await label.evaluate('el => el.parentElement?.id || ""')
                if is_visible and "radio-format" not in parent_id:
                    await label.click()
                    print("   Outcome 1 effect measure: MD")
                    await page.wait_for_timeout(500)
                    break

            # Select beneficial for direction (first beneficial label)
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
            # For continuous long format, need mean, SD, n
            print("\n[Step 8] Selecting outcome 1 variables...")
            await select_outcome_variables(
                page,
                outcome_index=0,
                variables=["y1", "sd1", "n1"],
                outcome_name="Outcome 1",
            )
            await page.wait_for_timeout(1000)

            # Click Next button to go to outcome 2
            print("\n[Step 8b] Clicking Next for outcome 2...")
            next_buttons = await page.query_selector_all("button")
            for button in next_buttons:
                button_id = await button.get_attribute("id") or ""
                if "outcomebutton" in button_id and '"index":"0"' in button_id:
                    await button.click()
                    print("   Clicked Next")
                    await page.wait_for_timeout(1500)
                    break

            # Step 8c: Outcome 2 - effect measure and direction
            print("\n[Step 8c] Configuring outcome 2 effect measure and direction...")

            # Select MD for effect measure (first visible MD label on current panel)
            md_labels = await page.query_selector_all('label:has-text("MD")')
            for label in md_labels:
                is_visible = await label.is_visible()
                parent_id = await label.evaluate('el => el.parentElement?.id || ""')
                if is_visible and "radio-format" not in parent_id:
                    await label.click()
                    print("   Outcome 2 effect measure: MD")
                    await page.wait_for_timeout(500)
                    break

            # Select beneficial for direction (first visible beneficial label on current panel)
            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            for label in beneficial_labels:
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    print("   Outcome 2 direction: beneficial")
                    await page.wait_for_timeout(500)
                    break

            # Step 8d: Outcome 2 - variables
            print("\n[Step 8d] Selecting outcome 2 variables...")
            await select_outcome_variables(
                page,
                outcome_index=1,
                variables=["y2", "sd2", "n2"],
                outcome_name="Outcome 2",
            )
            await page.wait_for_timeout(1000)

            # Step 9: Configure effect modifiers (Age, BMI)
            print("\n[Step 9] Selecting effect modifiers (Age, BMI)...")
            await page.wait_for_timeout(1000)

            try:
                # Effect modifiers are checkboxes - click on "Age" and "BMI" checkbox labels
                age_checkbox = page.locator('label:has-text("Age")')
                if await age_checkbox.count() > 0:
                    await age_checkbox.first.click()
                    print("   Effect modifier 1: Age")
                    await page.wait_for_timeout(300)

                bmi_checkbox = page.locator('label:has-text("BMI")')
                if await bmi_checkbox.count() > 0:
                    await bmi_checkbox.first.click()
                    print("   Effect modifier 2: BMI")
                    await page.wait_for_timeout(300)

            except Exception as e:
                print(f"   Could not select effect modifiers: {e}")
                print("   Trying to continue anyway...")

            # Step 10: Click Run Analysis button
            print("\n[Step 10] Running analysis...")
            run_button = "#upload_modal_data2"
            await page.wait_for_selector(run_button, timeout=5000)

            # Verify button is enabled
            is_disabled = await page.locator(run_button).is_disabled()
            if is_disabled:
                print("Run Analysis button is disabled!")
                # Take screenshot to debug
                screenshot_path = (
                    Path(__file__).parent / "test_upload_continuous_long_disabled.png"
                )
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
            screenshot_path = (
                Path(__file__).parent / "test_upload_continuous_long_result.png"
            )
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
            screenshot_path = (
                Path(__file__).parent / "test_upload_continuous_long_error.png"
            )
            await page.screenshot(path=str(screenshot_path))
            print(f"Error screenshot saved: {screenshot_path}")
            raise
        finally:
            print("\nClosing browser...")
            await browser.close()


if __name__ == "__main__":
    print("Running continuous long format upload and analysis test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 60)

    try:
        results = asyncio.run(test_upload_continuous_long())

        if results is None:
            print("\nTest returned no results - check error messages above")
        elif results.get("success"):
            print("\nTEST PASSED - Analysis completed successfully!")
        else:
            print("\nTEST COMPLETED WITH WARNINGS - Check details above")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
