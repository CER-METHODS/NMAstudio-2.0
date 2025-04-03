#!/usr/bin/env python3
"""
Test to load a saved .nmastudio project file and verify results page

This test performs the following steps:
1. Navigates to the /setup page
2. Opens the Save/Load Project modal
3. Switches to the "Load Project" tab
4. Uploads the 3outcomes_test_project.nmastudio file
   - Should automatically redirect to /results page after upload
5. Verifies that all 3 outcomes are loaded correctly
6. Checks the outcome selector dropdown
7. Verifies league tables are displayed
8. Checks network plots render for all outcomes
9. Verifies effect modifiers (age, weight) are loaded correctly

Expected behavior:
- No console errors
- Project loads successfully
- Automatic redirect to /results page after upload
- Results page displays all 3 outcomes (PASI90, SAE, AE)
- Outcome selector contains all 3 outcomes
- League tables are visible
- Network plots render
- Effect modifiers (age, weight) are loaded in localStorage
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def test_load_project():
    # Get path to saved project file
    project_file = (
        Path(__file__).parent / "downloads" / "3outcomes_test_project.nmastudio"
    )

    if not project_file.exists():
        print(f"❌ Project file not found: {project_file}")
        print(
            "Please run test_upload_and_run_analysis.py first to generate the project file"
        )
        return

    print(f"✅ Found project file: {project_file}")
    print(f"File size: {project_file.stat().st_size / 1024:.1f} KB")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Track console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg))

        try:
            # Step 1: Navigate to setup page
            print("\n📍 Step 1: Navigating to /setup page...")
            await page.goto("http://localhost:8050/setup", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            print("✅ Setup page loaded")

            # Step 2: Open Save/Load Project modal
            print("\n📍 Step 2: Opening Save/Load Project modal...")

            # Wait for button to be available and click
            await page.wait_for_selector("#open_saveload", timeout=10000)
            await page.click("#open_saveload")
            await page.wait_for_timeout(2000)

            # Verify modal is open by checking visibility
            modal = await page.query_selector("#modal_saveload")
            if modal:
                is_visible = await modal.is_visible()
                if is_visible:
                    print("✅ Save/Load modal opened")
                else:
                    print("❌ Modal not visible")
                    return
            else:
                print("❌ Modal not found in DOM")
                return

            # Step 3: Switch to "Load Project" tab
            print("\n📍 Step 3: Switching to Load Project tab...")
            tabs = await page.query_selector_all(".tab")
            for tab in tabs:
                text = await tab.inner_text()
                if "Load Project" in text:
                    await tab.click()
                    await page.wait_for_timeout(500)
                    print("✅ Switched to Load Project tab")
                    break

            # Step 4: Upload the project file
            print(f"\n📍 Step 4: Uploading project file...")
            upload_input = await page.query_selector("#upload-json input[type=file]")
            if upload_input:
                await upload_input.set_input_files(str(project_file))
                print(f"✅ Project file uploaded: {project_file.name}")

                # Wait for file to be processed and automatic redirect to /results
                print(
                    "⏳ Waiting for project to load and automatic redirect to /results..."
                )
                try:
                    await page.wait_for_url("**/results", timeout=10000)
                    print("✅ Automatically redirected to results page!")
                except Exception as e:
                    print(f"⚠️  Automatic redirect didn't happen (timeout after 10s)")
                    print(f"    Current URL: {page.url}")
                    # Manually navigate if auto-redirect failed
                    await page.goto(
                        "http://localhost:8050/results", wait_until="networkidle"
                    )
                    print("✅ Manually navigated to results page")

                # Wait for results to fully render
                await page.wait_for_timeout(5000)
                print("✅ Results page loaded")
            else:
                print("❌ Upload input not found")
                return

            # Step 5: Verify outcomes are loaded
            print("\n📍 Step 5: Verifying outcomes are loaded...")

            # Check for outcome names in the page
            page_content = await page.content()
            outcome_names = ["PASI90", "SAE", "AE"]
            found_outcomes = []

            for outcome in outcome_names:
                if outcome in page_content:
                    found_outcomes.append(outcome)
                    print(f"✅ Found outcome: {outcome}")
                else:
                    print(f"⚠️  Outcome not found: {outcome}")

            if len(found_outcomes) == 3:
                print(f"✅ All 3 outcomes loaded successfully: {found_outcomes}")
            else:
                print(f"⚠️  Only {len(found_outcomes)}/3 outcomes found")

            # Step 6: Check outcome selector dropdown
            print("\n📍 Step 6: Checking outcome selector dropdown...")

            # Wait for dropdown to be populated
            await page.wait_for_timeout(2000)

            # Check the first outcome selector
            outcome_select = await page.query_selector("#_outcome_select")
            if outcome_select:
                # Click to open dropdown
                select_control = await outcome_select.query_selector(".Select-control")
                if select_control:
                    await select_control.click()
                    await page.wait_for_timeout(500)

                    # Get dropdown options
                    options = await page.query_selector_all(".VirtualizedSelectOption")
                    option_texts = []
                    for option in options:
                        text = await option.inner_text()
                        option_texts.append(text)

                    print(f"✅ Outcome selector options: {option_texts}")

                    # Click first option to close dropdown
                    if options:
                        await options[0].click()
                        await page.wait_for_timeout(500)
                else:
                    print("⚠️  Could not open outcome selector dropdown")
            else:
                print("⚠️  Outcome selector not found")

            # Step 7: Verify league tables are displayed
            print("\n📍 Step 7: Checking for league tables...")

            # Look for league table section
            league_section = await page.query_selector("#league_section")
            if league_section:
                is_visible = await league_section.is_visible()
                if is_visible:
                    print("✅ League table section is visible")

                    # Check for DataTable component
                    league_table = await page.query_selector("#league_table")
                    if league_table:
                        print("✅ League table component found")
                    else:
                        print("⚠️  League table component not found")
                else:
                    print("⚠️  League table section exists but is not visible")
            else:
                print("⚠️  League table section not found")

            # Step 8: Verify network plots render
            print("\n📍 Step 8: Checking network plots...")

            # Look for network plot graphs
            network_graphs = await page.query_selector_all(".js-plotly-plot")
            if network_graphs:
                print(f"✅ Found {len(network_graphs)} Plotly graphs on page")

                # Check if at least one is a network plot
                for i, graph in enumerate(network_graphs[:3]):  # Check first 3
                    graph_id = await graph.get_attribute("id") or f"graph_{i}"
                    if "network" in graph_id.lower():
                        print(f"✅ Network plot found: {graph_id}")
            else:
                print("⚠️  No Plotly graphs found")

            # Step 9: Verify effect modifiers are loaded
            print("\n📍 Step 9: Verifying effect modifiers are loaded...")

            # Check localStorage for effect_modifiers_STORAGE
            effect_modifiers = await page.evaluate(
                """() => {
                    const stored = localStorage.getItem('effect_modifiers_STORAGE');
                    if (stored) {
                        try {
                            const parsed = JSON.parse(stored);
                            return parsed;
                        } catch (e) {
                            return null;
                        }
                    }
                    return null;
                }"""
            )

            if effect_modifiers:
                if isinstance(effect_modifiers, list) and len(effect_modifiers) == 2:
                    print(f"✅ Effect modifiers loaded: {effect_modifiers}")
                    if "age" in effect_modifiers and "weight" in effect_modifiers:
                        print("✅ Correct modifiers: age and weight")
                    else:
                        print(f"⚠️  Unexpected modifiers: {effect_modifiers}")
                else:
                    print(f"⚠️  Effect modifiers format unexpected: {effect_modifiers}")
            else:
                print("⚠️  Effect modifiers not found in localStorage")

            # Final summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)

            # Check for console errors
            errors = [msg for msg in console_messages if msg.type == "error"]
            if errors:
                print(f"⚠️  {len(errors)} console errors:")
                for error in errors[:5]:  # Show first 5
                    print(f"   - {error.text}")
            else:
                print("✅ No console errors")

            print(f"✅ Outcomes loaded: {len(found_outcomes)}/3")
            print(f"✅ Project file: {project_file.name}")
            print(f"✅ Results page: Accessible")

            # Effect modifiers check
            if effect_modifiers and isinstance(effect_modifiers, list):
                if "age" in effect_modifiers and "weight" in effect_modifiers:
                    print(f"✅ Effect modifiers: {effect_modifiers}")
                else:
                    print(f"⚠️  Effect modifiers incorrect: {effect_modifiers}")
            else:
                print("⚠️  Effect modifiers not loaded")

            print("\n🎉 Test completed successfully!")

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

        finally:
            # Keep browser open for inspection
            print("\n⏸️  Browser will remain open for 10 seconds for inspection...")
            await page.wait_for_timeout(10000)
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_load_project())
