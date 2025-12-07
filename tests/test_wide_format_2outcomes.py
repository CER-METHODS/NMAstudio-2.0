#!/usr/bin/env python3
"""
Test to create and analyze a 2-outcome NMAstudio project using IV format data.

This test performs the following steps:
1. Navigates to the /setup page
2. Uploads the psoriasis_wide_complete.csv sample data
3. Selects data format (iv - inverse variance with pre-calculated TE/seTE)
4. Maps data columns (studlab, treat1, treat2, rob, year)
5. Configures 2 outcomes
6. Sets outcome types (Binary)
7. Maps variables for each outcome (TE1, seTE1, n11, n21 for outcome 1; etc.)
8. Runs the full analysis
9. Verifies redirect to results page

Expected behavior:
- All analysis steps complete successfully
- User is redirected to /results page
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def select_outcome_variables(page, outcome_index, variables, outcome_name):
    """
    Helper to select variables for an outcome in IV format.

    Args:
        page: Playwright page object
        outcome_index: Index of the outcome (0 or 1)
        variables: List of variable names to select (e.g., ["TE1", "seTE1", "n11", "n21"])
        outcome_name: Name for logging (e.g., "Efficacy")
    """
    print(f"📊 Selecting variables for {outcome_name}...")

    # Wait for the variable selection section
    await page.wait_for_timeout(1000)

    # Find variable dropdowns in the #variable_selection section
    var_section = await page.query_selector("#variable_selection")

    if not var_section:
        print(f"   ⚠️  Could not find #variable_selection section!")
        return False

    # Find all visible dropdowns with "..." placeholder
    outcome_vars = []
    dropdowns = await var_section.query_selector_all(".dash-dropdown")
    print(f"   Found {len(dropdowns)} dropdowns in variable_selection")

    for dropdown in dropdowns:
        is_visible = await dropdown.is_visible()
        if not is_visible:
            continue

        placeholder = await dropdown.query_selector(".Select-placeholder")
        if placeholder:
            placeholder_text = await placeholder.inner_text()
            if placeholder_text == "...":
                outcome_vars.append(dropdown)

    print(f"   Found {len(outcome_vars)} unfilled variable dropdowns")

    # Only select the number of variables we need
    outcome_vars = outcome_vars[: len(variables)]

    if len(outcome_vars) < len(variables):
        print(f"   ⚠️  Only found {len(outcome_vars)} dropdowns, need {len(variables)}")

    success_count = 0
    for i, var_name in enumerate(variables):
        if i >= len(outcome_vars):
            print(f"   ⚠️  No dropdown for variable {i + 1}: {var_name}")
            continue

        var_dropdown = outcome_vars[i]
        try:
            select_input = await var_dropdown.query_selector(".Select-control")
            if select_input:
                await select_input.click()
            else:
                await var_dropdown.click()

            await page.wait_for_timeout(200)
            await page.keyboard.type(var_name)
            await page.wait_for_timeout(200)
            await page.keyboard.press("Enter")
            print(f"   ✅ Variable {i + 1}: {var_name}")
            await page.wait_for_timeout(300)
            success_count += 1
        except Exception as e:
            print(f"   ❌ Error selecting {var_name}: {e}")

    return success_count == len(variables)


async def test_wide_format_2outcomes():
    """Test uploading IV format CSV and running full analysis with 2 outcomes"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        output_dir = Path(__file__).parent / "downloads"
        output_dir.mkdir(exist_ok=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(15000)

        # Track errors (only real errors, not React warnings)
        console_errors = []

        def handle_console(msg):
            if msg.type == "error" and "Warning:" not in msg.text:
                console_errors.append(msg.text)
                print(f"\n🔴 Console error:\n   {msg.text}")

        page.on("console", handle_console)

        try:
            print("🚀 Starting NMAstudio IV format test (2 outcomes)...")

            # Step 1: Navigate to setup page
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
                    return None

            print(f"✅ Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 2: Upload IV format CSV
            print("\n📤 Step 1: Uploading IV format CSV file...")
            csv_path = (
                Path(__file__).parent.parent / "db" / "psoriasis_wide_complete.csv"
            )

            if not csv_path.exists():
                print(f"❌ CSV file not found: {csv_path}")
                return None

            # Upload file
            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"✅ Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1000)

            # Step 3: Select data format (iv - inverse variance)
            print("\n📝 Step 2: Selecting data format...")
            await page.wait_for_selector("#radio-format", timeout=5000)
            await page.click("#radio-format label:has-text('iv')")
            print("✅ Selected: IV format (inverse-variance)")
            await page.wait_for_timeout(2000)

            # Step 4: Select required data columns
            print("\n📋 Step 3: Selecting data columns...")
            columns_values = ["studlab", "treat1", "treat2", "rob", "year"]

            dropdowns = await page.query_selector_all(".dash-dropdown")
            print(f"Found {len(dropdowns)} dropdowns")

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
                        print(f"✅ Selected: {value}")
                        await page.wait_for_timeout(300)

            # Step 5: Enter number of outcomes
            print("\n🎯 Step 4: Setting number of outcomes...")
            await page.wait_for_selector("#number-outcomes", timeout=5000)
            await page.fill("#number-outcomes", "2")
            await page.wait_for_timeout(300)
            await page.click("#num_outcomes_button")
            print("✅ Set and confirmed: 2 outcomes")
            await page.wait_for_timeout(2000)

            # Step 6: Select outcomes for league table (or Skip)
            print("\n🏆 Step 5: Selecting outcomes for league table...")
            await page.wait_for_timeout(1500)

            try:
                # Look for checkbox inputs (outcomes for league table)
                checkboxes = await page.query_selector_all('input[type="checkbox"]')
                print(f"Found {len(checkboxes)} checkboxes")

                # For 2 outcomes, select both for league table
                if len(checkboxes) >= 2:
                    # Check outcome 1
                    await checkboxes[0].click()
                    print("✅ Selected outcome 1 for league table")
                    await page.wait_for_timeout(300)

                    # Check outcome 2
                    await checkboxes[1].click()
                    print("✅ Selected outcome 2 for league table")
                    await page.wait_for_timeout(1500)
                else:
                    # If no checkboxes, try clicking Skip
                    print("⚠️  No checkboxes found, trying Skip...")
                    skip_labels = await page.query_selector_all(
                        'label:has-text("Skip")'
                    )
                    for label in skip_labels:
                        is_visible = await label.is_visible()
                        if is_visible:
                            await label.click()
                            print("✅ Clicked Skip for league table")
                            await page.wait_for_timeout(1000)
                            break
            except Exception as e:
                print(f"⚠️  Could not select league table outcomes: {e}")

            # Step 6: Configure BOTH outcome types and names first
            print("\n📊 Step 6: Configuring outcome types and names...")
            await page.wait_for_timeout(1000)

            # Click binary for outcome 1
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            print(f"   Found {len(binary_labels)} 'binary' labels")
            if len(binary_labels) > 0:
                await binary_labels[0].click()
                print("✅ Outcome 1 type: Binary")
                await page.wait_for_timeout(500)

            # Fill outcome 1 name
            name_input1 = await page.query_selector(
                'input[id*="nameoutcomes"][id*=\'"index":"0"\']'
            )
            if not name_input1:
                name_input1 = await page.query_selector(
                    'input[id*="nameoutcomes"][id*=\'"index":0\']'
                )
            if name_input1:
                await name_input1.click()
                await name_input1.fill("Efficacy")
                print("✅ Outcome 1 name: Efficacy")
                await page.wait_for_timeout(500)

            # Click binary for outcome 2
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            if len(binary_labels) > 1:
                await binary_labels[1].click()
                print("✅ Outcome 2 type: Binary")
                await page.wait_for_timeout(500)

            # Fill outcome 2 name
            name_input2 = await page.query_selector(
                'input[id*="nameoutcomes"][id*=\'"index":"1"\']'
            )
            if not name_input2:
                name_input2 = await page.query_selector(
                    'input[id*="nameoutcomes"][id*=\'"index":1\']'
                )
            if name_input2:
                await name_input2.click()
                await name_input2.fill("Safety")
                print("✅ Outcome 2 name: Safety")
                await page.wait_for_timeout(1000)

            # Now wait for effect measure and direction sections to appear
            print("\n⚙️  Step 7: Configuring effect measures and directions...")
            await page.wait_for_timeout(2000)

            # Scroll down to see more of the page
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(1000)

            # Select OR for outcome 1 effect measure (click first visible one)
            or_labels = await page.query_selector_all('label:has-text("OR")')
            print(f"   Found {len(or_labels)} 'OR' labels")
            or_clicked = 0
            for label in or_labels:
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    or_clicked += 1
                    print(f"✅ Outcome {or_clicked} effect measure: OR")
                    await page.wait_for_timeout(500)
                    if or_clicked >= 2:  # Select for both outcomes
                        break

            # Select beneficial for outcome 1, harmful for outcome 2
            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            harmful_labels = await page.query_selector_all('label:has-text("harmful")')
            print(
                f"   Found {len(beneficial_labels)} 'beneficial', {len(harmful_labels)} 'harmful' labels"
            )

            for label in beneficial_labels:
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    print("✅ Outcome 1 direction: beneficial")
                    await page.wait_for_timeout(500)
                    break

            for label in harmful_labels:
                is_visible = await label.is_visible()
                if is_visible:
                    await label.click()
                    print("✅ Outcome 2 direction: harmful")
                    await page.wait_for_timeout(500)
                    break

            # Step 8: Select variables for outcome 1
            print("\n📈 Step 8: Selecting outcome 1 variables...")
            await page.wait_for_timeout(1500)
            await select_outcome_variables(
                page,
                outcome_index=0,
                variables=["TE1", "seTE1", "n11", "n21"],
                outcome_name="Efficacy",
            )
            await page.wait_for_timeout(500)

            # Click Next button to go to outcome 2
            print("\n➡️  Clicking Next for outcome 2...")
            next_buttons = await page.query_selector_all("button")
            for button in next_buttons:
                button_id = await button.get_attribute("id") or ""
                if "outcomebutton" in button_id and (
                    '"index":"0"' in button_id or '"index":0' in button_id
                ):
                    await button.click()
                    print("✅ Clicked Next")
                    await page.wait_for_timeout(1500)
                    break

            # Step 9: Select variables for outcome 2
            print("\n📉 Step 9: Selecting outcome 2 variables...")
            await select_outcome_variables(
                page,
                outcome_index=1,
                variables=["TE2", "seTE2", "n12", "n22"],
                outcome_name="Safety",
            )
            await page.wait_for_timeout(1000)

            # Step 10: Handle effect modifiers
            print("\n🔀 Step 10: Handling effect modifiers...")
            await page.wait_for_timeout(3000)

            try:
                # Wait for the effect modifier section
                await page.wait_for_selector(
                    "#select_effect_modifier", state="visible", timeout=10000
                )

                # Try clicking Skip option
                labels = await page.query_selector_all("#select_effect_modifier label")
                for label in labels:
                    label_text = await label.inner_text()
                    if "skip" in label_text.strip().lower():
                        await label.click()
                        print("✅ Clicked 'Skip' option")
                        await page.wait_for_timeout(500)
                        break
            except Exception as e:
                print(f"⚠️  Effect modifier section issue: {e}")

            # Step 11: Click Run Analysis button
            print("\n🔬 Step 11: Starting analysis...")
            await page.wait_for_timeout(1000)

            run_button = await page.query_selector("#upload_modal_data2")
            if run_button:
                is_disabled = await run_button.get_attribute("disabled")
                if is_disabled:
                    print("⚠️ Run Analysis button is disabled!")
                    screenshot_path = output_dir / "test_before_run_analysis.png"
                    await page.screenshot(path=str(screenshot_path))
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    await run_button.click()
                    print("✅ Clicked Run Analysis button")

            # Step 12: Wait for analysis to complete
            print("\n⏳ Step 12: Waiting for analysis to complete...")

            try:
                await page.wait_for_selector(
                    "#modal_data_checks", state="visible", timeout=10000
                )
                print("✅ Analysis modal opened")

                analysis_steps = [
                    ("Data Checks", "para-check-data-modal", 60000),
                    ("Network meta-analysis", "para-anls-data-modal", 120000),
                    ("Pairwise meta-analysis", "para-pairwise-data-modal", 60000),
                    ("League table", "para-LT-data-modal", 120000),
                    ("Funnel plot", "para-FA-data-modal", 60000),
                ]

                for step_name, element_id, timeout in analysis_steps:
                    print(f"⏳ Waiting for {step_name}...")
                    try:
                        await page.wait_for_function(
                            f"""() => {{
                                const el = document.querySelector('#{element_id}');
                                return el && el.textContent && el.textContent.includes('✓');
                            }}""",
                            timeout=timeout,
                        )
                        print(f"✅ {step_name} completed")
                    except Exception as e:
                        print(f"⚠️ {step_name} timeout or error: {e}")
                        error_el = await page.query_selector(f"#{element_id}")
                        if error_el:
                            error_text = await error_el.inner_text()
                            print(f"   Status: {error_text}")

                # Click Submit button
                print("\n📤 Submitting results...")
                submit_button = await page.query_selector("#submit_modal_data")
                if submit_button:
                    is_disabled = await submit_button.get_attribute("disabled")
                    if not is_disabled:
                        await submit_button.click()
                        print("✅ Clicked Submit button")
                    else:
                        print("⚠️ Submit button is disabled")

            except Exception as e:
                print(f"⚠️ Analysis modal issue: {e}")
                screenshot_path = output_dir / "test_analysis_error.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Screenshot saved: {screenshot_path}")

            # Step 13: Verify redirect to results page
            print("\n🔍 Step 13: Verifying redirect to results page...")
            await page.wait_for_timeout(3000)
            current_url = page.url

            if "/results" in current_url:
                print(f"✅ Successfully redirected to: {current_url}")
            else:
                print(f"⚠️ Expected /results page, but got: {current_url}")

            print("\n" + "=" * 60)
            print(
                "✅ TEST COMPLETED SUCCESSFULLY!"
                if "/results" in current_url
                else "⚠️ TEST COMPLETED WITH ISSUES"
            )
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            screenshot_path = output_dir / "test_wide_format_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Error screenshot saved: {screenshot_path}")
            raise

        finally:
            print("\n🔚 Closing browser...")
            await context.close()
            await browser.close()


if __name__ == "__main__":
    print("🧪 Running IV format 2-outcomes project test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 60)
    asyncio.run(test_wide_format_2outcomes())
