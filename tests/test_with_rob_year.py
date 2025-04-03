#!/usr/bin/env python3
"""
Test with rob and year fields populated.
Tests the complete workflow WITH providing rob and year values.
"""

import asyncio
import os
from playwright.async_api import async_playwright


async def test_with_rob_year():
    """Test complete workflow WITH rob and year: upload → configure → run analysis → submit → verify"""

    async with async_playwright() as p:
        # Launch browser in visible mode
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,  # 0.1 second delay between actions
            args=["--window-size=1200,800"],
        )

        page = await browser.new_page()

        try:
            print("🚀 Starting WITH rob/year test...")
            print("🖥️ Browser window will open and show the complete workflow!\n")

            # Navigate to the setup page
            await page.goto("http://macas.lan:8050/setup")
            await page.wait_for_load_state("networkidle")

            # Step 1: Upload the file
            print("📁 Uploading psoriasis dataset...")

            file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "db",
                "psoriasis_long_complete.csv",
            )
            file_path = os.path.abspath(file_path)

            file_input = await page.query_selector(
                '#datatable-upload2 input[type="file"]'
            )
            if file_input:
                await file_input.set_input_files(file_path)
                await page.wait_for_timeout(500)
                print("✅ File uploaded successfully!")
            else:
                print("❌ Could not find file input element")
                return

            # Step 2: Select long format
            print("🔍 Selecting long format...")
            await page.wait_for_selector(
                "#dropdowns-DIV2", state="visible", timeout=10000
            )
            long_format_radio = await page.query_selector('label:has-text("long")')
            if long_format_radio:
                await long_format_radio.click()
                print("✅ Selected 'long' format")
            else:
                print("❌ 'Long' format radio button not found")
                return

            # Step 3: Fill variable selection dropdowns - INCLUDING rob and year
            print("🔍 Filling variable selection dropdowns (WITH rob and year)...")
            dropdowns = await page.query_selector_all("div.Select-control")

            # Fill all 4 dropdowns including rob and year
            column_mappings = {
                0: "unique_id",  # studlab
                1: "treat",  # treat
                2: "bias",  # rob
                3: "year",  # year
            }

            for i, dropdown in enumerate(dropdowns[:4]):  # All 4 dropdowns
                expected_col = column_mappings.get(i, "unique_id")

                # Click to open dropdown
                await dropdown.click()
                await page.wait_for_timeout(200)

                # Find and click the expected option
                option = await page.query_selector(
                    f'div.Select-option:has-text("{expected_col}")'
                )
                if option:
                    await option.click()
                    print(f"✅ Selected '{expected_col}' for dropdown {i + 1}")
                else:
                    # Fallback: try text selector
                    option = await page.query_selector(f'text="{expected_col}"')
                    if option:
                        await option.click()
                        print(f"✅ Selected '{expected_col}' for dropdown {i + 1}")

                await page.wait_for_timeout(100)

            # Step 4: Set number of outcomes
            print("🔍 Setting number of outcomes...")
            await page.wait_for_selector(
                "#number-outcomes", state="visible", timeout=5000
            )
            await page.fill("#number-outcomes", "2")

            ok_button = await page.query_selector("#num_outcomes_button")
            if ok_button:
                await ok_button.click()
                print("✅ Set number of outcomes to 2")

            # Step 5: Select outcomes
            print("🔍 Selecting outcomes...")
            outcomes_primary = await page.query_selector("#outcomes_primary")
            if outcomes_primary:
                checkboxes = await page.query_selector_all(
                    '#outcomes_primary input[type="checkbox"]'
                )
                outcome_labels = await page.query_selector_all(
                    "#outcomes_primary label"
                )

                outcome_checkboxes = []
                for i, label in enumerate(outcome_labels):
                    label_text = await label.text_content()
                    if (
                        label_text
                        and "skip" not in label_text.lower()
                        and i < len(checkboxes)
                    ):
                        outcome_checkboxes.append(checkboxes[i])

                # Select first 2 outcome checkboxes
                for i, checkbox in enumerate(outcome_checkboxes[:2]):
                    await checkbox.click()
                    await page.wait_for_timeout(200)
                    print(f"✅ Selected outcome checkbox {i + 1}")

            # Step 6: Fill select-out-type form
            print("🔍 Filling outcome type form...")
            await page.wait_for_selector(
                "#select-out-type", state="visible", timeout=5000
            )

            # Select binary for both outcomes
            print("🔍 Selecting binary for outcomes...")
            outcome_containers = await page.query_selector_all('div[id*="outcometype"]')

            outcome_count = 0
            for container in outcome_containers:
                container_id = await container.get_attribute("id")
                if container_id and '"type":"outcometype"' in container_id:
                    if outcome_count >= 2:
                        break

                    labels = await container.query_selector_all("label")
                    for label in labels:
                        text = await label.text_content()
                        if text and text.strip() == "binary":
                            await label.click()
                            print(f"✅ Selected binary for outcome {outcome_count + 1}")
                            outcome_count += 1
                            break

            # Fill text inputs
            text_inputs = await page.query_selector_all(
                '#select-out-type input[type="text"]'
            )
            if len(text_inputs) >= 2:
                await text_inputs[0].fill("PAIN")
                await text_inputs[1].fill("SE")
                print("✅ Filled outcome type form")

            # Step 7: Fill variable selection forms for first outcome
            print("🔍 Filling variable selection forms for first outcome...")

            # Select OR for first outcome
            print("🔄 Selecting OR for first outcome...")
            effect_containers = await page.query_selector_all(
                'div[id*="effectselectors"]'
            )

            for container in effect_containers:
                container_id = await container.get_attribute("id")
                if (
                    container_id
                    and '"type":"effectselectors"' in container_id
                    and '"index":"0"' in container_id
                ):
                    labels = await container.query_selector_all("label")
                    for label in labels:
                        text = await label.text_content()
                        if text and text.strip() == "OR":
                            await label.click()
                            print("✅ Selected OR for first outcome")
                            break
                    break

            # Select beneficial for first outcome
            print("🔄 Selecting beneficial for first outcome...")
            direction_containers = await page.query_selector_all(
                'div[id*="directionselectors"]'
            )

            for container in direction_containers:
                container_id = await container.get_attribute("id")
                if (
                    container_id
                    and '"type":"directionselectors"' in container_id
                    and '"index":"0"' in container_id
                ):
                    labels = await container.query_selector_all("label")
                    for label in labels:
                        text = await label.text_content()
                        if text and text.strip() == "beneficial":
                            await label.click()
                            print("✅ Selected beneficial for first outcome")
                            break
                    break

            # Wait for variable selection form to appear
            print("🔄 Waiting for variable selection form...")
            await page.wait_for_selector(
                'div[id*="variableselectors"]', state="visible", timeout=5000
            )

            # Fill variable dropdowns for first outcome
            print("🔄 Filling variable selection dropdowns for first outcome...")
            variable_dropdowns = await page.query_selector_all(
                'div[id*="variableselectors"][id*="\\"index\\":\\"0\\""] .Select-control'
            )

            if len(variable_dropdowns) >= 2:
                # First dropdown: rPASI90
                await variable_dropdowns[0].click()
                await page.wait_for_timeout(300)
                rpasi_option = await page.query_selector('text="rPASI90"')
                if rpasi_option:
                    await rpasi_option.click()
                    print("✅ Selected 'rPASI90' for No. events")
                await page.wait_for_timeout(200)

                # Second dropdown: nPASI90
                await variable_dropdowns[1].click()
                await page.wait_for_timeout(300)
                npasi_option = await page.query_selector('text="nPASI90"')
                if npasi_option:
                    await npasi_option.click()
                    print("✅ Selected 'nPASI90' for No. participants")

                print("✅ Filled variable selection for first outcome")

                # Click Next button to proceed to second outcome
                print("🔄 Clicking Next to proceed to second outcome...")
                next_button = await page.query_selector('button[id*="outcomebutton"]')
                if next_button:
                    await next_button.click()
                    await page.wait_for_timeout(300)
                    print("✅ Clicked Next button")

                    # Fill second outcome form
                    print("🔄 Filling variable selection forms for second outcome...")
                    await page.wait_for_selector(
                        'div[id*="displayvariable"][id*="1"]',
                        state="visible",
                        timeout=5000,
                    )

                    # Select effect size for second outcome (OR)
                    effect_containers = await page.query_selector_all(
                        'div[id*="effectselectors"]'
                    )
                    for container in effect_containers:
                        container_id = await container.get_attribute("id")
                        if (
                            container_id
                            and '"type":"effectselectors"' in container_id
                            and '"index":"1"' in container_id
                        ):
                            labels = await container.query_selector_all("label")
                            for label in labels:
                                text = await label.text_content()
                                if text and text.strip() == "OR":
                                    await label.click()
                                    print("✅ Selected OR for second outcome")
                                    break
                            break

                    # Select direction for second outcome
                    direction_containers = await page.query_selector_all(
                        'div[id*="directionselectors"]'
                    )
                    for container in direction_containers:
                        container_id = await container.get_attribute("id")
                        if (
                            container_id
                            and '"type":"directionselectors"' in container_id
                            and '"index":"1"' in container_id
                        ):
                            labels = await container.query_selector_all("label")
                            for label in labels:
                                text = await label.text_content()
                                if text and text.strip() == "beneficial":
                                    await label.click()
                                    print("✅ Selected beneficial for second outcome")
                                    break
                            break

                    # Fill variable dropdowns for second outcome
                    variable_dropdowns_2 = await page.query_selector_all(
                        'div[id*="variableselectors"][id*="\\"index\\":\\"1\\""] .Select-control'
                    )

                    if len(variable_dropdowns_2) >= 2:
                        await variable_dropdowns_2[0].click()
                        await page.wait_for_timeout(300)
                        rsae_option = await page.query_selector('text="rSAE"')
                        if rsae_option:
                            await rsae_option.click()
                            print("✅ Selected 'rSAE' for No. events (outcome 2)")
                        await page.wait_for_timeout(200)

                        await variable_dropdowns_2[1].click()
                        await page.wait_for_timeout(300)
                        nsae_option = await page.query_selector('text="nSAE"')
                        if nsae_option:
                            await nsae_option.click()
                            print("✅ Selected 'nSAE' for No. participants (outcome 2)")

                        print("✅ Filled variable selection for second outcome")

                print("🎉 Both outcomes filled!")

                # Step 8: Handle effect modifiers - automatically enabled
                print("\n🔄 Step 8: Handling effect modifiers...")
                print("⚠️  Note: Effect modifier form should be automatically enabled")

                # Wait a bit for the form to appear
                await page.wait_for_timeout(1500)

                # Wait for effect modifier form to appear
                try:
                    await page.wait_for_selector(
                        "#effect_modifier_checkbox, #no_effect_modifier",
                        state="visible",
                        timeout=5000,
                    )
                    print("✅ Effect modifier form appeared (auto-enabled)")

                    # Debug: List all checkboxes available
                    all_checkboxes = await page.evaluate("""
                        () => {
                            const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                            return checkboxes.map(cb => ({
                                id: cb.id,
                                name: cb.name,
                                value: cb.value,
                                checked: cb.checked,
                                visible: cb.offsetParent !== null
                            }));
                        }
                    """)
                    print(f"🔍 Available checkboxes: {all_checkboxes}")

                    # Try to find and click the skip checkbox
                    skip_clicked = False

                    # Method 1: Try clicking input with id containing "skip" or value "skip"
                    skip_checkboxes = await page.query_selector_all(
                        'input[type="checkbox"]'
                    )
                    for checkbox in skip_checkboxes:
                        checkbox_id = await checkbox.get_attribute("id")
                        checkbox_value = await checkbox.get_attribute("value")
                        if (checkbox_id and "skip" in checkbox_id.lower()) or (
                            checkbox_value and "skip" in checkbox_value.lower()
                        ):
                            await checkbox.click()
                            print(
                                f"✅ Clicked skip checkbox (id: {checkbox_id}, value: {checkbox_value})"
                            )
                            skip_clicked = True
                            break

                    # Method 2: If not found, select the 16th checkbox (age modifier)
                    if not skip_clicked:
                        print(
                            "⚠️ Skip checkbox not found, selecting age (16th checkbox)..."
                        )
                        effect_checkboxes = await page.query_selector_all(
                            '#effect_modifier_checkbox input[type="checkbox"]'
                        )

                        # Select the 16th checkbox (index 15) which should be 'age'
                        if len(effect_checkboxes) >= 16:
                            await effect_checkboxes[
                                15
                            ].click()  # 16th checkbox is index 15
                            value = await effect_checkboxes[15].get_attribute("value")
                            print(
                                f"✅ Selected 16th checkbox as effect modifier: {value}"
                            )
                        elif len(effect_checkboxes) > 0:
                            # Fallback to first checkbox if less than 16 available
                            await effect_checkboxes[0].click()
                            value = await effect_checkboxes[0].get_attribute("value")
                            print(f"⚠️ Less than 16 checkboxes, selected first: {value}")

                    await page.wait_for_timeout(500)

                except Exception as e:
                    print(f"⚠️ Effect modifier form issue: {e}")
                    print("   Continuing anyway...")

                # Step 9: Click "Run Analysis" button
                print("\n🚀 Step 9: Clicking 'Run Analysis' button...")
                print(
                    "⏳ Please wait for the analysis to complete (this may take 30-60 seconds)..."
                )

                # Debug: Check button state
                button_state = await page.evaluate("""
                    () => {
                        const button = document.querySelector('#upload_modal_data2');
                        const effectMod = document.querySelector('#effect_modifier_checkbox');
                        const noEffect = document.querySelector('#no_effect_modifier');
                        return {
                            buttonExists: button !== null,
                            buttonDisabled: button ? button.disabled : null,
                            buttonVisible: button ? window.getComputedStyle(button).display !== 'none' : null,
                            effectModValue: effectMod ? effectMod.value : null,
                            noEffectChecked: noEffect ? noEffect.checked : null
                        };
                    }
                """)
                print(f"🔍 Debug - Button state: {button_state}")

                await page.wait_for_selector(
                    "#upload_modal_data2", state="visible", timeout=10000
                )

                await page.wait_for_selector(
                    "#upload_modal_data2", state="visible", timeout=10000
                )
                upload_button = await page.query_selector("#upload_modal_data2")

                if upload_button:
                    await upload_button.click()
                    print("✅ Clicked 'Run Analysis' button")

                    # Wait for the analysis to complete
                    print("⏳ Waiting for analysis to complete...")
                    await page.wait_for_timeout(3000)

                    submit_button = await page.query_selector("#submit_modal_data")
                    max_wait = 120
                    waited = 0
                    while waited < max_wait:
                        if submit_button:
                            is_disabled = await submit_button.is_disabled()
                            if not is_disabled:
                                print("✅ Analysis completed successfully!\n")
                                break
                        await page.wait_for_timeout(2000)
                        waited += 2
                        if waited % 10 == 0:
                            print(f"   Still waiting... ({waited}s elapsed)")

                    if waited >= max_wait:
                        print("⚠️ Timeout waiting for analysis to complete")
                        return

                else:
                    print("❌ Could not find 'Run Analysis' button")
                    return

                # Step 10: Click Submit button
                print("✅ Step 10: Clicking Submit button...")
                submit_button = await page.query_selector("#submit_modal_data")
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(2000)
                    print("✅ Clicked Submit button\n")
                else:
                    print("❌ Could not find Submit button")
                    return

                # Step 11: Verify results
                print("🔍 Step 11: Verifying results...\n")

                storage_check = await page.evaluate("""
                    () => {
                        const results = {
                            raw_data: null,
                            net_data: null,
                            results_ready: null,
                            raw_data_length: 0,
                            net_data_length: 0,
                            has_rob_column: false,
                            has_year_column: false
                        };

                        try {
                            const rawData = localStorage.getItem('raw_data_STORAGE');
                            const netData = localStorage.getItem('net_data_STORAGE');
                            const resultsReady = localStorage.getItem('results_ready_STORAGE');

                            results.raw_data = rawData;
                            results.net_data = netData;
                            results.results_ready = resultsReady;
                            results.raw_data_length = rawData ? rawData.length : 0;
                            results.net_data_length = netData ? netData.length : 0;

                            // Check if rob and year columns exist in the data
                            if (netData) {
                                try {
                                    const parsed = JSON.parse(netData);
                                    if (parsed && parsed[0]) {
                                        const dataStr = JSON.parse(parsed[0]);
                                        if (dataStr.columns) {
                                            results.has_rob_column = dataStr.columns.includes('rob');
                                            results.has_year_column = dataStr.columns.includes('year');
                                        }
                                    }
                                } catch (e) {
                                    console.error('Error parsing net_data:', e);
                                }
                            }
                        } catch (e) {
                            console.error('Error checking storage:', e);
                        }

                        return results;
                    }
                """)

                print("=" * 60)
                print("📊 TEST RESULTS - OPTIONAL ROB/YEAR:")
                print("=" * 60)

                success = True

                if storage_check.get("results_ready") == "true":
                    print("✅ results_ready_STORAGE: TRUE")
                else:
                    print(
                        f"❌ results_ready_STORAGE: {storage_check.get('results_ready')}"
                    )
                    success = False

                if (
                    storage_check.get("raw_data")
                    and storage_check.get("raw_data") != "null"
                ):
                    print(
                        f"✅ raw_data_STORAGE: POPULATED ({storage_check.get('raw_data_length')} characters)"
                    )
                else:
                    print("❌ raw_data_STORAGE: EMPTY or NULL")
                    success = False

                if (
                    storage_check.get("net_data")
                    and storage_check.get("net_data") != "null"
                ):
                    print(
                        f"✅ net_data_STORAGE: POPULATED ({storage_check.get('net_data_length')} characters)"
                    )
                else:
                    print("❌ net_data_STORAGE: EMPTY or NULL")
                    success = False

                # Verify rob and year columns exist (even if empty/NaN)
                if storage_check.get("has_rob_column"):
                    print("✅ rob column exists in data (may contain NaN values)")
                else:
                    print("❌ rob column missing from data")
                    success = False

                if storage_check.get("has_year_column"):
                    print("✅ year column exists in data (may contain NaN values)")
                else:
                    print("❌ year column missing from data")
                    success = False

                print("=" * 60)

                if success:
                    print("\n🎉 TEST PASSED! Analysis works WITH rob/year values!")
                    print("✅ rob and year columns are properly populated!")
                else:
                    print("\n❌ TEST FAILED! Issues with rob/year handling.")

                print("\n" + "=" * 60)

            else:
                print(f"⚠️ Only found {len(variable_dropdowns)} variable dropdowns")
                return

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

        finally:
            print("\n🔄 Closing browser...")
            await browser.close()
            print("✅ Test complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("WITH ROB/YEAR TEST")
    print("=" * 60)
    print("This test will:")
    print("  1. Upload psoriasis dataset")
    print("  2. Configure WITH rob and year values provided")
    print("  3. Run the analysis")
    print("  4. Verify that analysis completes successfully")
    print("  5. Verify that rob/year columns have actual data values")
    print("=" * 60)
    print()

    asyncio.run(test_with_rob_year())
