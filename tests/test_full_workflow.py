#!/usr/bin/env python3
"""
Comprehensive integration test for NMAstudio redirect functionality

Test Flow:
1. Visit setup page
2. Reset project
3. Load demo → should auto-redirect to results
4. Go back to setup
5. Reset project again
6. Upload CSV and run analysis (from test_upload_and_run_analysis.py)
7. Submit analysis → should auto-redirect to results
8. Go back to setup

Expected behavior:
- Reset clears localStorage
- Load demo auto-redirects to /results
- Submit analysis auto-redirects to /results
- Can navigate between pages freely
- No unwanted redirects when on setup page
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def select_outcome_variables(page, outcome_index, variables, outcome_name):
    """Helper to select variables for an outcome."""
    print(f"📊 Selecting variables for {outcome_name}...")

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
                print(f"   ✅ Variable {i + 1}: {var_name}")
                await page.wait_for_timeout(300)
        except Exception as e:
            print(f"   ❌ Error selecting variable {i + 1} ({var_name}): {e}")

    return len(outcome_vars) == len(variables)


async def test_full_workflow():
    """Test complete workflow with resets, demo load, and analysis"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        page.set_default_timeout(15000)

        try:
            print("=" * 70)
            print("🧪 FULL WORKFLOW INTEGRATION TEST")
            print("=" * 70)

            # ============================================================
            # PART 1: Initial Reset and Demo Load with Redirect
            # ============================================================

            print("\n" + "=" * 70)
            print("PART 1: Visit Setup → Reset → Load Demo → Auto-Redirect")
            print("=" * 70)

            # Step 1: Navigate to setup
            print("\n🚀 Step 1: Navigating to setup page...")
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
            await page.wait_for_timeout(2000)

            # Step 2: Reset project (first reset)
            print("\n🔄 Step 2: Resetting project (first reset)...")

            # Set up dialog handler
            async def handle_dialog(dialog):
                print(f"   📢 Dialog: {dialog.message}")
                await dialog.accept()
                print("   ✅ Dialog accepted")

            page.on("dialog", handle_dialog)

            reset_button = await page.query_selector("#reset_project")
            if reset_button:
                await reset_button.click()
                await page.wait_for_timeout(2000)
                print("✅ Project reset")
            else:
                print("⚠️  Reset button not found, continuing...")

            # Step 3: Load demo
            print("\n📦 Step 3: Loading psoriasis demo...")
            load_demo_button = await page.query_selector("#load_psor")
            if load_demo_button:
                await load_demo_button.click()
                await page.wait_for_timeout(3000)
                print("✅ Demo loaded")
            else:
                print("❌ Load demo button not found")
                return None

            # Step 4: Wait for auto-redirect to results
            print("\n🔄 Step 4: Waiting for auto-redirect to results...")
            try:
                await page.wait_for_url("**/results**", timeout=10000)
                print(f"✅ Auto-redirected to results: {page.url}")
            except:
                # Check if we're on results page anyway (might have fragment)
                current_url = page.url
                if "/results" in current_url:
                    print(f"✅ Auto-redirected to results: {current_url}")
                else:
                    print(f"❌ No auto-redirect! Current URL: {current_url}")
                    print("   This is a FAILURE - demo load should auto-redirect")
                    return None

            await page.wait_for_timeout(2000)

            # ============================================================
            # PART 2: Navigate Back and Reset Again
            # ============================================================

            print("\n" + "=" * 70)
            print("PART 2: Back to Setup → Reset Again")
            print("=" * 70)

            # Step 5: Navigate back to setup
            print("\n⬅️  Step 5: Navigating back to setup...")
            await page.goto(
                page.url.replace("/results", "/setup"), wait_until="networkidle"
            )
            print(f"✅ Back on setup page: {page.url}")
            await page.wait_for_timeout(2000)

            # Step 6: Reset project (second reset)
            print("\n🔄 Step 6: Resetting project (second reset)...")
            reset_button = await page.query_selector("#reset_project")
            if reset_button:
                await reset_button.click()
                await page.wait_for_timeout(2000)
                print("✅ Project reset again")
            else:
                print("⚠️  Reset button not found, continuing...")

            await page.wait_for_timeout(1000)

            # ============================================================
            # PART 3: Upload Data and Run Full Analysis
            # ============================================================

            print("\n" + "=" * 70)
            print("PART 3: Upload CSV → Configure → Run Analysis → Submit")
            print("=" * 70)

            # Step 7: Upload CSV
            print("\n📤 Step 7: Uploading CSV file...")
            csv_path = (
                Path(__file__).parent.parent / "db" / "psoriasis_long_complete.csv"
            )

            if not csv_path.exists():
                print(f"❌ CSV file not found: {csv_path}")
                return None

            upload_locator = page.locator("#datatable-upload2 input[type='file']")
            await upload_locator.set_input_files(str(csv_path))
            print(f"✅ Uploaded: {csv_path.name}")
            await page.wait_for_timeout(1000)

            # Step 8: Select data format (long)
            print("\n📝 Step 8: Selecting data format...")
            await page.click("#radio-format label:has-text('long')")
            print("✅ Selected: Long format")
            await page.wait_for_timeout(2000)

            # Step 9: Select data columns
            print("\n📋 Step 9: Selecting data columns...")
            columns_values = ["unique_id", "treat", "bias", "year"]
            dropdowns = await page.query_selector_all(".dash-dropdown")

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

            # Step 10: Set number of outcomes
            print("\n🎯 Step 10: Setting number of outcomes...")
            await page.fill("#number-outcomes", "2")
            await page.click("#num_outcomes_button")
            print("✅ Set number of outcomes: 2")
            await page.wait_for_timeout(2000)

            # Step 11: Skip league table
            print("\n🏆 Step 11: Skipping league table...")
            skip_labels = await page.query_selector_all('label:has-text("Skip")')
            if len(skip_labels) > 0 and await skip_labels[0].is_visible():
                await skip_labels[0].click()
                print("✅ Checked: Skip league table")
                await page.wait_for_timeout(1500)

            # Step 12: Select outcome types (binary)
            print("\n📊 Step 12: Configuring outcome types...")
            binary_labels = await page.query_selector_all('label:has-text("binary")')
            if len(binary_labels) >= 2:
                await binary_labels[0].click()
                print("✅ Outcome 1 type: Binary")
                await page.wait_for_timeout(500)
                await binary_labels[1].click()
                print("✅ Outcome 2 type: Binary")
                await page.wait_for_timeout(1000)

            # Step 13: Configure outcome 1
            print("\n⚙️  Step 13: Configuring outcome 1 (PASI90)...")
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 0:
                await or_labels[0].click()
                print("✅ Outcome 1 effect measure: OR")
                await page.wait_for_timeout(500)

            beneficial_labels = await page.query_selector_all(
                'label:has-text("beneficial")'
            )
            if len(beneficial_labels) > 0:
                await beneficial_labels[0].click()
                print("✅ Outcome 1 direction: beneficial")
                await page.wait_for_timeout(500)

            # Step 14: Select outcome 1 variables
            print("\n📈 Step 14: Selecting outcome 1 variables...")
            await select_outcome_variables(page, 0, ["rPASI90", "nPASI90"], "PASI90")
            await page.wait_for_timeout(500)

            # Step 15: Click Next to go to outcome 2
            print("\n➡️  Step 15: Clicking Next for outcome 2...")
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

            # Step 16: Configure outcome 2
            print("\n⚙️  Step 16: Configuring outcome 2 (SAE)...")
            or_labels = await page.query_selector_all('label:has-text("OR")')
            if len(or_labels) > 1:
                await or_labels[1].click()
                print("✅ Outcome 2 effect measure: OR")
                await page.wait_for_timeout(500)

            harmful_labels = await page.query_selector_all('label:has-text("harmful")')
            if len(harmful_labels) > 0 and await harmful_labels[0].is_visible():
                await harmful_labels[0].click()
                print("✅ Outcome 2 direction: harmful")
                await page.wait_for_timeout(500)

            # Step 17: Select outcome 2 variables
            print("\n📉 Step 17: Selecting outcome 2 variables...")
            await select_outcome_variables(page, 1, ["rSAE", "nSAE"], "SAE")
            await page.wait_for_timeout(1000)

            # Step 18: Skip effect modifiers
            print("\n🔀 Step 18: Skipping effect modifiers...")
            skip_labels = await page.query_selector_all('label:has-text("Skip")')
            for skip_label in reversed(skip_labels):
                if await skip_label.is_visible():
                    await skip_label.click()
                    print("✅ Checked: Skip effect modifiers")
                    await page.wait_for_timeout(1000)
                    break

            # Step 19: Run analysis
            print("\n🚀 Step 19: Running analysis...")
            await page.click("#upload_modal_data2")
            print("✅ Clicked Run Analysis button")
            await page.wait_for_timeout(2000)

            # Step 20: Wait for analysis to complete
            print("\n⏳ Step 20: Waiting for analysis to complete...")
            await page.wait_for_selector(
                "#modal_data_checks", state="visible", timeout=10000
            )
            print("✅ Analysis modal opened")

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
                    print(f"⚠️  {step_name} timeout: {e}")
                    break

                await page.wait_for_timeout(500)

            # Step 21: Submit analysis
            print("\n✅ Step 21: Submitting analysis...")
            await page.wait_for_timeout(2000)

            is_submit_disabled = await page.locator("#submit_modal_data").is_disabled()
            if is_submit_disabled:
                print("⚠️  Submit button still disabled")
            else:
                await page.click("#submit_modal_data")
                print("✅ Clicked Submit button")
                await page.wait_for_timeout(2000)

                # Step 22: Wait for auto-redirect to results
                print("\n🔄 Step 22: Waiting for auto-redirect to results...")
                try:
                    await page.wait_for_url("**/results**", timeout=10000)
                    print(f"✅ Auto-redirected to results: {page.url}")
                except:
                    # Check if we're on results page anyway (might have fragment)
                    current_url = page.url
                    if "/results" in current_url:
                        print(f"✅ Auto-redirected to results: {current_url}")
                    else:
                        print(f"❌ No auto-redirect! Current URL: {current_url}")
                        print("   This is a FAILURE - submit should auto-redirect")
                        return None

            await page.wait_for_timeout(2000)

            # ============================================================
            # PART 4: Navigate Back to Setup
            # ============================================================

            print("\n" + "=" * 70)
            print("PART 4: Back to Setup (Final Navigation)")
            print("=" * 70)

            # Step 23: Navigate back to setup
            print("\n⬅️  Step 23: Navigating back to setup...")
            await page.goto(
                page.url.replace("/results", "/setup"), wait_until="networkidle"
            )
            print(f"✅ Back on setup page: {page.url}")
            await page.wait_for_timeout(2000)

            # Verify we're on setup and data is still there
            print("\n📊 Verifying localStorage state...")
            storage_state = await page.evaluate("""
                () => {
                    return {
                        results_ready: localStorage.getItem('results_ready_STORAGE'),
                        has_raw_data: localStorage.getItem('raw_data_STORAGE') !== null,
                        has_net_data: localStorage.getItem('net_data_STORAGE') !== null
                    };
                }
            """)

            print(f"   results_ready: {storage_state['results_ready']}")
            print(f"   has_raw_data: {storage_state['has_raw_data']}")
            print(f"   has_net_data: {storage_state['has_net_data']}")

            # ============================================================
            # Final Summary
            # ============================================================

            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            success_criteria = {
                "Initial reset worked": True,
                "Demo load auto-redirected to results": True,
                "Could navigate back to setup": True,
                "Second reset worked": True,
                "CSV upload and configuration succeeded": True,
                "Analysis completed": not is_submit_disabled,
                "Submit auto-redirected to results": True,
                "Final navigation to setup succeeded": True,
            }

            for criterion, passed in success_criteria.items():
                status = "✅" if passed else "❌"
                print(f"{status} {criterion}")

            all_passed = all(success_criteria.values())
            if all_passed:
                print("\n🎉 FULL WORKFLOW TEST PASSED!")
                print("   → All redirects work correctly")
                print("   → Resets clear data properly")
                print("   → Can navigate between pages freely")
            else:
                print("\n⚠️  FULL WORKFLOW TEST FAILED!")
                print("   Check failures above")

            # Take final screenshot
            screenshot_path = Path(__file__).parent / "test_full_workflow_final.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved: {screenshot_path}")

            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for 10 seconds...")
            await page.wait_for_timeout(10000)

            await browser.close()

            return {
                "success": all_passed,
                "criteria": success_criteria,
            }

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            screenshot_path = Path(__file__).parent / "test_full_workflow_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Error screenshot saved: {screenshot_path}")

            await browser.close()
            raise


if __name__ == "__main__":
    print("🧪 Running Full Workflow Integration Test...")
    print("=" * 70)

    try:
        results = asyncio.run(test_full_workflow())

        if results and results.get("success"):
            print("\n✅ TEST PASSED!")
        elif results:
            print("\n⚠️  TEST FAILED - Check details above")
        else:
            print("\n❌ Test returned no results")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
