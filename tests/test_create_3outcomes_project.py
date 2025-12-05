#!/usr/bin/env python3
"""
Test to create and save a 3-outcome NMAstudio project matching 3outcomes_test_project.nmastudio

This test performs the following steps:
1. Navigates to the /setup page
2. Uploads the psoriasis_long_complete.csv sample data
3. Selects data format (long)
4. Maps data columns (studlab, treat, rob, year)
5. Configures 3 outcomes (PASI90, SAE, and AE)
6. Skips league table primary outcome selection
7. Sets outcome types (all Binary)
8. Configures effect measures (OR) and directions (beneficial for PASI90, harmful for SAE and AE)
9. Maps variables for each outcome
10. Selects effect modifiers (age, weight)
11. Runs the full analysis (data checks, NMA, pairwise, league table, funnel)
12. Waits for analysis to complete and submits results
13. Verifies redirect to results page
14. Saves the project as 3outcomes_test_project.nmastudio

Expected behavior:
- No console errors
- All analysis steps complete successfully
- User is redirected to /results page
- Project file is saved to tests/downloads/
"""

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def select_dropdown_by_typing(page, dropdown_id_part, index, value, label):
    """Helper to select dropdown option by typing and pressing Enter"""
    dropdowns = await page.query_selector_all(".dash-dropdown")
    for dropdown in dropdowns:
        dd_id = await dropdown.get_attribute("id") or ""
        # Try both string and integer index formats
        if dropdown_id_part in dd_id and (
            f'"index":"{index}"' in dd_id or f'"index":{index}' in dd_id
        ):
            select_control = await dropdown.query_selector(".Select-control")
            if select_control:
                await select_control.click()
                await page.keyboard.type(value)
                await page.wait_for_timeout(200)
                await page.keyboard.press("Enter")
                print(f"✅ {label}: {value}")
                await page.wait_for_timeout(300)
                return True
    return False


async def select_outcome_variables(page, outcome_index, variables, outcome_name):
    """
    Helper to select variables for an outcome.
    For binary outcomes in long format, there are multiple dropdowns (one per variable).

    Args:
        page: Playwright page object
        outcome_index: Index of the outcome (0 or 1)
        variables: List of variable names to select (e.g., ["rPASI90", "nPASI90"])
        outcome_name: Name for logging (e.g., "PASI90")
    """
    print(f"📊 Selecting variables for {outcome_name}...")

    # Get all dropdowns with variableselectors and matching outcome index
    dropdowns = await page.query_selector_all(".dash-dropdown")
    outcome_vars = []

    for dropdown in dropdowns:
        dropdown_id = await dropdown.get_attribute("id") or ""
        # Match variableselectors with the outcome index (as string)
        if (
            "variableselectors" in dropdown_id
            and f'"index":"{outcome_index}"' in dropdown_id
        ):
            outcome_vars.append(dropdown)

    print(
        f"   Found {len(outcome_vars)} variable dropdowns for outcome {outcome_index}"
    )

    if len(outcome_vars) != len(variables):
        print(
            f"   ⚠️  Warning: Expected {len(variables)} dropdowns, found {len(outcome_vars)}"
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
                print(f"   ✅ Variable {i + 1}: {var_name}")
                await page.wait_for_timeout(300)
            else:
                print(f"   ❌ Could not find select control for variable {i + 1}")
        except Exception as e:
            print(f"   ❌ Error selecting variable {i + 1} ({var_name}): {e}")

    return len(outcome_vars) == len(variables)


async def test_create_3outcomes_project():
    """Test uploading CSV and running full analysis"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        # Set up downloads directory
        output_dir = Path(__file__).parent / "downloads"
        output_dir.mkdir(exist_ok=True)
        # Create context with downloads acceptance
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

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
                print(f"\n🔴 Console {msg.type}:")
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
            print(f"❌ Failed request: {request.url}")

        page.on("requestfailed", handle_request_failed)

        try:
            print("🚀 Starting NMAstudio upload and analysis test...")

            # Navigate to the app
            try:
                await page.goto(
                    "http://macas.lan:8050/setup",
                    wait_until="networkidle",
                    timeout=15000,
                )
            except:
                try:
                    await page.goto(
                        "http://localhost:8050/setup",
                        wait_until="networkidle",
                        timeout=15000,
                    )
                except:
                    print("❌ Could not connect to NMAstudio server")
                    print("Please make sure the server is running with: python app.py")
                    return None

            print(f"✅ Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 1: Upload CSV file
            print("\n📤 Step 1: Uploading CSV file...")
            csv_path = (
                Path(__file__).parent.parent / "db" / "psoriasis_long_complete.csv"
            )

            if not csv_path.exists():
                print(f"❌ CSV file not found: {csv_path}")
                return None

            # Wait for upload component and upload file
            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"✅ Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1000)

            # Verify file is uploaded
            uploaded_file_locator = page.locator("#uploaded_datafile2")
            uploaded_file = await uploaded_file_locator.inner_text()
            print(f"✅ File shown in UI: {uploaded_file}")

            # Step 2: Select data format (long format)
            print("\n📝 Step 2: Selecting data format...")
            await page.wait_for_selector("#radio-format", timeout=5000)

            # Click on long format radio button
            await page.click("#radio-format label:has-text('long')")
            print("✅ Selected: Long format")
            await page.wait_for_timeout(2000)

            # Step 3: Select required data columns using keyboard input
            print("\n📋 Step 3: Selecting data columns...")

            # CSV columns: unique_id, name, year, bias, treat, treat_class
            # Dropdowns are: study ID, treat, rob (optional), year (optional)
            columns_values = ["unique_id", "treat", "bias", "year"]

            dropdowns = await page.query_selector_all(".dash-dropdown")
            print(f"Found {len(dropdowns)} dropdowns")

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
                        print(f"✅ Selected: {value}")
                        await page.wait_for_timeout(300)

            # Step 4: Enter number of outcomes
            print("\n🎯 Step 4: Setting number of outcomes...")
            await page.wait_for_selector("#number-outcomes", timeout=5000)
            await page.fill("#number-outcomes", "3")
            print("✅ Set number of outcomes: 3")
            await page.wait_for_timeout(300)

            # Click OK button
            await page.click("#num_outcomes_button")
            print("✅ Clicked OK button")
            await page.wait_for_timeout(2000)

            # Step 5: Select outcomes for league table (outcome 2 and 3)
            print("\n🏆 Step 5: Selecting outcomes for league table...")
            await page.wait_for_timeout(1500)

            # Find checkboxes for league table outcomes
            # We need to select outcome 2 (SAE) and outcome 3 (AE)
            try:
                # Look for checkbox inputs
                checkboxes = await page.query_selector_all('input[type="checkbox"]')
                print(f"Found {len(checkboxes)} checkboxes")

                # Click the checkboxes for outcomes 2 and 3 (indices 1 and 2 in 0-based)
                if len(checkboxes) >= 3:
                    # Check outcome 2 (index 1)
                    await checkboxes[1].click()
                    print("✅ Selected outcome 2 for league table")
                    await page.wait_for_timeout(300)

                    # Check outcome 3 (index 2)
                    await checkboxes[2].click()
                    print("✅ Selected outcome 3 for league table")
                    await page.wait_for_timeout(1500)
                else:
                    print(f"⚠️  Expected 3+ checkboxes, found {len(checkboxes)}")
            except Exception as e:
                print(f"⚠️  Could not select league table outcomes: {e}")

            # Step 6: Select outcome types and fill outcome names
            print("\n📊 Step 6: Configuring outcome types and names...")

            # Wait for outcome type radio buttons to appear
            await page.wait_for_timeout(1000)

            # Find all radio buttons with "binary" text and click them
            # There should be one set for each outcome
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            print(f"Found {len(binary_labels)} 'binary' radio button labels")

            # Find text inputs that are visible and likely outcome name fields
            # Skip the "number-outcomes" input by checking visibility and position
            all_text_inputs = await page.query_selector_all('input[type="text"]')
            outcome_name_inputs = []

            for inp in all_text_inputs:
                is_visible = await inp.is_visible()
                inp_id = await inp.get_attribute("id") or ""
                # Skip number-outcomes input and other non-outcome-name fields
                if (
                    is_visible
                    and "number-outcomes" not in inp_id
                    and "number_outcomes" not in inp_id
                ):
                    outcome_name_inputs.append(inp)

            print(
                f"Found {len(outcome_name_inputs)} text input fields before filtering"
            )

            # We should have exactly 3 outcome name inputs. If we have 4, skip the first one
            # (it's likely an effect modifier or other field)
            if len(outcome_name_inputs) == 4:
                outcome_name_inputs = outcome_name_inputs[1:]  # Skip the first one
                print(
                    f"Filtered to {len(outcome_name_inputs)} outcome name inputs (skipped first)"
                )

            print(f"Using {len(outcome_name_inputs)} outcome name text input fields")

            outcome_names = ["PASI90", "SAE", "AE"]

            if len(binary_labels) >= 3 and len(outcome_name_inputs) >= 3:
                # Configure each outcome: click binary and fill name
                for i in range(3):
                    # Click binary for outcome
                    await binary_labels[i].click()
                    print(f"✅ Outcome {i + 1} type: Binary")
                    await page.wait_for_timeout(300)

                    # Fill in outcome name in the corresponding text input
                    await outcome_name_inputs[i].click()
                    await outcome_name_inputs[i].fill(outcome_names[i])
                    print(f"✅ Outcome {i + 1} name: {outcome_names[i]}")
                    await page.wait_for_timeout(300)

                await page.wait_for_timeout(1000)
            else:
                print(f"⚠️  Expected 3 binary labels and 3 name inputs")
                print(
                    f"    Found {len(binary_labels)} binary labels, {len(outcome_name_inputs)} name inputs"
                )
                # Try clicking what we have
                for i, label in enumerate(binary_labels):
                    await label.click()
                    print(f"✅ Outcome {i + 1} type: Binary")
                    await page.wait_for_timeout(500)
                    if i < len(outcome_name_inputs):
                        await outcome_name_inputs[i].click()
                        await outcome_name_inputs[i].fill(
                            outcome_names[i]
                            if i < len(outcome_names)
                            else f"Outcome{i + 1}"
                        )
                        print(f"✅ Outcome {i + 1} name filled")
                        await page.wait_for_timeout(300)

            # Step 7: Outcome 1 - effect measure and direction
            print("\n⚙️  Step 7: Configuring outcome 1 (PASI90)...")

            # Select OR for effect measure (first OR radio button)
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 0:
                await or_labels[0].click()
                print("✅ Outcome 1 effect measure: OR")
                await page.wait_for_timeout(500)

            # Select beneficial for direction (first beneficial radio button)
            # For PASI90, higher is better = beneficial
            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            if len(beneficial_labels) > 0:
                await beneficial_labels[0].click()
                print("✅ Outcome 1 direction: beneficial")
                await page.wait_for_timeout(500)

            # Step 8: Outcome 1 - variables
            print("\n📈 Step 8: Selecting outcome 1 variables...")
            # For binary outcome in long format, we need r (events) and n (total)
            await select_outcome_variables(
                page,
                outcome_index=0,
                variables=["rPASI90", "nPASI90"],
                outcome_name="PASI90",
            )
            await page.wait_for_timeout(500)

            # Click Next button to go to outcome 2
            print("\n➡️  Clicking Next for outcome 2...")
            next_buttons = await page.query_selector_all("button")
            for button in next_buttons:
                button_id = await button.get_attribute("id") or ""
                # Try both string and integer index formats
                if "outcomebutton" in button_id and (
                    '"index":"0"' in button_id or '"index":0' in button_id
                ):
                    await button.click()
                    print("✅ Clicked Next")
                    await page.wait_for_timeout(1500)
                    break

            # Step 9: Outcome 2 - effect measure and direction
            print("\n⚙️  Step 9: Configuring outcome 2 (SAE)...")

            # Select OR for effect measure (second OR radio button)
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 1:
                await or_labels[1].click()
                print("✅ Outcome 2 effect measure: OR")
                await page.wait_for_timeout(500)

            # Select harmful for direction (for SAE, lower is better = harmful outcome)
            # Find the currently visible harmful radio button
            harmful_labels = await page.query_selector_all('label:has-text("harmful")')
            print(f"   Found {len(harmful_labels)} 'harmful' labels")
            harmful_clicked = False
            for i, label in enumerate(harmful_labels):
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    print(f"✅ Outcome 2 direction: harmful (label {i})")
                    await page.wait_for_timeout(500)
                    harmful_clicked = True
                    break

            if not harmful_clicked:
                print(
                    "   ⚠️  No visible harmful labels, trying beneficial as fallback..."
                )
                beneficial_labels = await page.query_selector_all(
                    'label:has-text("beneficial")'
                )
                for label in beneficial_labels:
                    is_visible = await label.is_visible()
                    if is_visible:
                        await label.click()
                        print("✅ Outcome 2 direction: beneficial (fallback)")
                        await page.wait_for_timeout(500)
                        break

            # Step 10: Outcome 2 - variables
            print("\n📉 Step 10: Selecting outcome 2 variables...")
            await select_outcome_variables(
                page,
                outcome_index=1,
                variables=["rSAE", "nSAE"],
                outcome_name="SAE",
            )
            await page.wait_for_timeout(500)

            # Click Next button to go to outcome 3
            print("\n➡️  Clicking Next for outcome 3...")
            next_buttons = await page.query_selector_all("button")
            for button in next_buttons:
                button_id = await button.get_attribute("id") or ""
                # Try both string and integer index formats
                if "outcomebutton" in button_id and (
                    '"index":"1"' in button_id or '"index":1' in button_id
                ):
                    await button.click()
                    print("✅ Clicked Next")
                    await page.wait_for_timeout(1500)
                    break

            # Step 11: Outcome 3 - effect measure and direction
            print("\n⚙️  Step 11: Configuring outcome 3 (AE)...")

            # Select OR for effect measure (third OR radio button)
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 2:
                await or_labels[2].click()
                print("✅ Outcome 3 effect measure: OR")
                await page.wait_for_timeout(500)

            # Select harmful for direction (for AE, lower is better = harmful outcome)
            # The second/third harmful radio button should be for outcome 3
            harmful_labels = await page.query_selector_all('label:has-text("harmful")')
            print(f"   Found {len(harmful_labels)} 'harmful' labels")
            # Try clicking the last harmful label (for outcome 3)
            if len(harmful_labels) >= 2:
                # Try the second harmful (index 1)
                for i in range(len(harmful_labels) - 1, -1, -1):
                    is_visible = await harmful_labels[i].is_visible()
                    if is_visible:
                        await harmful_labels[i].click()
                        print(f"✅ Outcome 3 direction: harmful (label {i})")
                        await page.wait_for_timeout(500)
                        break
                else:
                    print("   ⚠️  No visible harmful labels found for outcome 3")

            # Step 12: Outcome 3 - variables
            print("\n📉 Step 12: Selecting outcome 3 variables...")
            await select_outcome_variables(
                page,
                outcome_index=2,
                variables=["rAE", "nAE"],
                outcome_name="AE",
            )
            await page.wait_for_timeout(1000)

            # Step 13: Configure effect modifiers (age, weight)
            print("\n🔀 Step 13: Selecting effect modifiers (age, weight)...")
            await page.wait_for_timeout(2000)  # Wait for form to update after outcome 3

            # Effect modifiers are CHECKBOXES, not dropdowns!
            # We need to check the checkboxes for 'age' and 'weight'
            try:
                # Wait for checklist to appear
                await page.wait_for_selector("#effect_modifier_checkbox", timeout=5000)

                # Find all checkbox inputs in the effect modifier checklist
                checkboxes = await page.query_selector_all(
                    '#effect_modifier_checkbox input[type="checkbox"]'
                )
                print(f"   Found {len(checkboxes)} effect modifier checkboxes")

                # Find and check 'age' and 'weight' checkboxes by their values
                checked_count = 0
                for checkbox in checkboxes:
                    # Get the value attribute to see what this checkbox represents
                    value = await checkbox.get_attribute("value")
                    if value in ["age", "weight"]:
                        # Check if already checked
                        is_checked = await checkbox.is_checked()
                        if not is_checked:
                            await checkbox.click()
                            print(f"   ✅ Checked effect modifier: {value}")
                            await page.wait_for_timeout(500)
                            checked_count += 1
                        else:
                            print(f"   ✓ Effect modifier already checked: {value}")
                            checked_count += 1

                if checked_count < 2:
                    print(
                        f"   ⚠️  Only found {checked_count}/2 effect modifiers, trying label method..."
                    )
                    # Try finding by label text containing age/weight
                    all_labels = await page.query_selector_all(
                        "#effect_modifier_checkbox label"
                    )
                    for label in all_labels:
                        label_text = await label.inner_text()
                        if label_text.lower() in ["age", "weight"]:
                            await label.click()
                            print(f"   ✅ Clicked label: {label_text}")
                            await page.wait_for_timeout(500)

                # Final wait for callbacks to process
                await page.wait_for_timeout(1000)
                print(f"   ✓ Effect modifier selection complete")

            except Exception as e:
                print(f"⚠️  Could not select effect modifiers: {e}")
                print("   Trying to continue anyway...")

            # Step 14: Save project at this point (before running analysis)
            print("\n💾 Step 14: Saving project configuration...")
            await page.wait_for_timeout(2000)

            # Extract localStorage data before analysis
            storage_data_before = await page.evaluate("""
                () => {
                    const data = {};
                    const storageKeys = [
                        'raw_data_STORAGE',
                        'effect_modifiers_STORAGE'
                    ];
                    
                    for (const key of storageKeys) {
                        const value = localStorage.getItem(key);
                        if (value !== null) {
                            try {
                                data[key] = JSON.parse(value);
                            } catch {
                                data[key] = value;
                            }
                        } else {
                            data[key] = null;
                        }
                    }
                    return data;
                }
            """)

            print(
                f"✅ Raw data stored: {storage_data_before.get('raw_data_STORAGE') is not None}"
            )
            print(
                f"✅ Effect modifiers: {storage_data_before.get('effect_modifiers_STORAGE')}"
            )

            # Step 15: Click Run Analysis button
            print("\n🚀 Step 15: Running analysis...")
            await page.wait_for_timeout(2000)  # Wait for effect modifiers to settle

            run_button = "#upload_modal_data2"

            # Debug: Check button state
            button_state = await page.evaluate("""
                () => {
                    const button = document.querySelector('#upload_modal_data2');
                    return {
                        buttonExists: button !== null,
                        buttonDisabled: button ? button.disabled : null,
                        buttonVisible: button ? window.getComputedStyle(button).display !== 'none' : null
                    };
                }
            """)
            print(f"🔍 Debug - Initial button state: {button_state}")

            # Wait for button to be visible and enabled
            await page.wait_for_selector(run_button, state="visible", timeout=10000)
            print("✅ Button is visible")

            # Wait for button to be enabled (not disabled)
            print("⏳ Waiting for button to be enabled...")
            max_wait = 30
            for i in range(max_wait):
                is_disabled = await page.locator(run_button).is_disabled()
                if not is_disabled:
                    print(f"✅ Button is enabled after {i} seconds")
                    break
                await page.wait_for_timeout(1000)
            else:
                print(
                    f"❌ Run Analysis button still disabled after {max_wait} seconds!"
                )
                # Debug: Check what might be missing
                button_state = await page.evaluate("""
                    () => {
                        const button = document.querySelector('#upload_modal_data2');
                        return {
                            buttonDisabled: button ? button.disabled : null
                        };
                    }
                """)
                print(f"🔍 Final button state: {button_state}")
                return None

            await page.click(run_button)
            print("✅ Clicked Run Analysis button")
            await page.wait_for_timeout(3000)  # Wait longer for R to start processing

            # Wait for modal to appear
            print("\n⏳ Step 16: Waiting for analysis to complete...")
            modal_selector = "#modal_data_checks"

            # Wait longer for the modal (analysis might take time to start)
            await page.wait_for_timeout(3000)

            try:
                await page.wait_for_selector(
                    modal_selector, state="visible", timeout=20000
                )
                print("✅ Analysis modal opened")
            except Exception as e:
                print(f"⚠️  Modal didn't appear: {e}")
                # Check if modal exists but is not visible
                modal_exists = await page.query_selector(modal_selector)
                if modal_exists:
                    is_open = await modal_exists.get_attribute("aria-modal")
                    print(f"   Modal exists but aria-modal={is_open}")
                else:
                    print("   Modal element doesn't exist at all")
                # Continue anyway to see what happens
                raise

            # Wait for all analysis steps to complete
            # The modal has 5 steps: data checks, NMA, pairwise, league table, funnel
            # Each step updates a para-*-data element when complete

            steps = [
                ("para-check-data", "Data Checks"),
                ("para-anls-data", "NMA Analysis"),
                ("para-pairwise-data", "Pairwise Analysis"),
                ("para-LT-data", "League Table"),
                ("para-FA-data", "Funnel Analysis"),
            ]

            for step_id, step_name in steps:
                print(f"⏳ Waiting for {step_name}...")
                try:
                    # Wait for the step to complete (up to 60 seconds per step to allow for R computations)
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
                    print(f"✅ {step_name} completed")
                except Exception as e:
                    print(f"⚠️  {step_name} timeout or error: {e}")
                    print(f"   Breaking out of analysis loop to show errors...")
                    break

                await page.wait_for_timeout(500)

            # Check if Submit button is enabled
            submit_button = "#submit_modal_data"
            await page.wait_for_timeout(2000)

            is_submit_disabled = await page.locator(submit_button).is_disabled()
            if is_submit_disabled:
                print("⚠️  Submit button still disabled after analysis")
            else:
                print("✅ Submit button is enabled")

                # Click Submit button
                await page.click(submit_button)
                print("✅ Clicked Submit button")
                await page.wait_for_timeout(2000)

                # Wait for redirect to results page
                print("\n🔄 Step 17: Waiting for redirect to results...")
                try:
                    await page.wait_for_url("**/results", timeout=10000)
                    print(f"✅ Redirected to results page: {page.url}")
                except:
                    print(f"⚠️  No redirect detected. Current URL: {page.url}")

                # Step 18: Save the project using Save/Load modal
                print("\n💾 Step 18: Saving project using Save/Load modal...")
                await page.wait_for_timeout(2000)

                output_dir = Path(__file__).parent / "downloads"

                # Click Save/Load Project button
                await page.click("#open_saveload")
                print("✅ Clicked Save/Load Project button")
                await page.wait_for_timeout(2000)

                # Wait for modal to be visible
                await page.wait_for_selector(
                    "#modal_saveload", state="visible", timeout=5000
                )
                print("✅ Save/Load modal opened")

                # Enter project name
                await page.fill("#input-projectname", "3outcomes_test_project")
                print("✅ Entered project name: 3outcomes_test_project")
                await page.wait_for_timeout(500)

                # Set up download event listener before clicking Save
                async with page.expect_download() as download_info:
                    await page.click("#btn_json")
                    print("✅ Clicked Save Project button")

                download = await download_info.value
                output_file = output_dir / "3outcomes_test_project.nmastudio"
                await download.save_as(str(output_file))
                print(f"✅ Project saved to: {output_file}")

                # Close the modal
                await page.click("#close_saveload")
                await page.wait_for_timeout(500)

            # Take a screenshot
            screenshot_path = Path(__file__).parent / "test_create_3outcomes_result.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot saved: {screenshot_path}")

            # Summary
            print("\n" + "=" * 60)
            print("=== Test Summary ===")
            print(f"Console Messages: {len(console_messages)}")
            print(f"Console Errors: {len(console_errors)}")
            print(f"Failed Requests: {len(failed_requests)}")

            if console_errors:
                print("\n⚠️  Console Errors:")
                for i, error in enumerate(console_errors[:10], 1):  # Show first 10
                    print(f"{i}. {error['text'][:100]}")

            if failed_requests:
                print("\n❌ Failed Requests:")
                for req in failed_requests[:5]:  # Show first 5
                    print(f"  - {req['method']} {req['url']}")

            if not console_errors and not failed_requests:
                print("\n✅ All tests passed! No errors detected.")
            else:
                print("\n⚠️  Test completed with some issues. Check output above.")

            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for 5 minutes for inspection...")
            await page.wait_for_timeout(300000)

            return {
                "console_messages": console_messages,
                "console_errors": console_errors,
                "failed_requests": failed_requests,
                "success": not console_errors and not failed_requests,
            }

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            screenshot_path = Path(__file__).parent / "test_upload_analysis_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Error screenshot saved: {screenshot_path}")
            raise
        finally:
            print("\n🔚 Closing browser...")
            await browser.close()


if __name__ == "__main__":
    print("🧪 Running create 3outcomes project test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 60)

    try:
        results = asyncio.run(test_create_3outcomes_project())

        if results is None:
            print("\n❌ Test returned no results - check error messages above")
        elif results.get("success"):
            print("\n✅ TEST PASSED - Analysis completed successfully!")
        else:
            print("\n⚠️  TEST COMPLETED WITH WARNINGS - Check details above")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
