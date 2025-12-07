#!/usr/bin/env python3
"""
Test ranking plots functionality using the demo data.
This test loads the demo, navigates to results, and verifies ranking plots display correctly.
"""

import asyncio
from playwright.async_api import async_playwright


async def test_ranking_plots():
    """Test that ranking plots display correctly after loading demo"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Set to False to see the browser
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = await browser.new_page()

        # Set up console message collection
        console_messages = []
        console_errors = []

        def handle_console_message(msg):
            """Handle console messages"""
            console_messages.append({"type": msg.type, "text": msg.text})
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console_message)

        # Handle dialogs automatically
        page.on("dialog", lambda dialog: dialog.accept())

        try:
            server_url = "http://macas.lan:8050"

            # Step 1: Load the demo project
            print("🚀 Step 1: Navigating to setup page...")
            try:
                await page.goto(f"{server_url}/setup", wait_until="load", timeout=30000)
                print("✅ Setup page loaded")
            except Exception as e:
                print(f"❌ Could not connect to server: {e}")
                print("Please make sure the server is running with: python app.py")
                return None

            # Wait for page to render
            await page.wait_for_timeout(5000)

            # Take debug screenshot
            await page.screenshot(
                path="/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/setup_debug.png"
            )
            print("📸 Setup page screenshot saved")

            # Step 2: Click Load Demo button
            print("\n🚀 Step 2: Loading demo project...")

            # Try to find the button with different methods
            load_demo_button = page.locator("#load_psor")
            button_count = await load_demo_button.count()
            print(f"   Found {button_count} buttons with #load_psor")

            if button_count == 0:
                # Try alternative selectors
                print("   Trying alternative selectors...")
                alt_button = page.locator("button:has-text('Demo')")
                alt_count = await alt_button.count()
                print(f"   Found {alt_count} buttons with text 'Demo'")

                if alt_count > 0:
                    load_demo_button = alt_button.first
                else:
                    # List all buttons
                    all_buttons = await page.locator("button").all()
                    print(f"   Total buttons on page: {len(all_buttons)}")
                    for i, btn in enumerate(all_buttons[:10]):
                        try:
                            btn_text = await btn.inner_text()
                            btn_id = await btn.get_attribute("id")
                            print(
                                f"   Button {i}: id='{btn_id}' text='{btn_text[:50] if btn_text else 'N/A'}'"
                            )
                        except:
                            pass
                    return None

            try:
                # Check if button is visible
                is_visible = await load_demo_button.is_visible()
                print(f"   Button is_visible: {is_visible}")

                # Get button bounding box
                bbox = await load_demo_button.bounding_box()
                print(f"   Button bounding box: {bbox}")

                # Use JavaScript to click the button - the dialog handler will auto-accept
                await page.evaluate("document.querySelector('#load_psor').click()")
                print("✅ Demo load initiated (dialog will be auto-accepted)")

                # Wait for the confirm dialog to be handled and data to load
                await page.wait_for_timeout(3000)

            except Exception as e:
                print(f"❌ Failed to click load demo button: {e}")
                return None

            # Step 3: Wait for redirect to results page
            print("\n🚀 Step 3: Waiting for redirect to results page...")
            try:
                await page.wait_for_url("**/results", timeout=20000)
                print("✅ Redirected to results page")
            except:
                print("⚠️  Auto-redirect didn't happen, navigating manually...")
                await page.goto(f"{server_url}/results", wait_until="load")

            # Wait for results page to load
            await page.wait_for_timeout(5000)

            # Step 4: Select "Ranking" from the results dropdown
            print("\n🚀 Step 4: Selecting 'Ranking' from results dropdown...")

            # Dash dropdowns are div-based, not select elements
            # We need to click the dropdown, then click the option
            results_dropdown = page.locator("#result_selected")
            try:
                await results_dropdown.wait_for(state="visible", timeout=10000)
                print("   Dropdown found")

                # Click to open the dropdown
                await results_dropdown.click()
                await page.wait_for_timeout(500)
                print("   Dropdown clicked (opened)")

                # Look for the Ranking option in the dropdown menu
                ranking_option = page.locator(
                    "div.VirtualizedSelectOption:has-text('Ranking')"
                )
                option_count = await ranking_option.count()
                print(f"   Found {option_count} Ranking options")

                if option_count > 0:
                    await ranking_option.first.click()
                    print("✅ Selected 'Ranking' option")
                else:
                    # Try alternative: find any option with text "Ranking"
                    alt_option = page.locator("[class*='option']:has-text('Ranking')")
                    alt_count = await alt_option.count()
                    print(f"   Alternative search found {alt_count} options")

                    if alt_count > 0:
                        await alt_option.first.click()
                        print("✅ Selected 'Ranking' option (alternative)")
                    else:
                        # List all visible options
                        all_options = await page.locator("[class*='option']").all()
                        print(f"   Total options visible: {len(all_options)}")
                        for i, opt in enumerate(all_options[:10]):
                            try:
                                text = await opt.inner_text()
                                print(f"   Option {i}: '{text}'")
                            except:
                                pass
                        raise Exception("Could not find Ranking option")

            except Exception as e:
                print(f"❌ Failed to select ranking: {e}")
                return None

            # Wait for ranking tab to load and callbacks to complete
            print("   Waiting for ranking data to load...")
            await page.wait_for_timeout(8000)  # Give more time for callbacks

            # Step 5: Verify ranking tab is visible
            print("\n🚀 Step 5: Verifying ranking tab and plots...")

            ranking_tab = page.locator("#ranking_tab")
            ranking_tab_visible = await ranking_tab.is_visible()
            print(f"   Ranking tab visible: {'✅' if ranking_tab_visible else '❌'}")

            # Check for the ranking subtabs container
            subtabs_rank = page.locator("#subtabs-rank1")
            subtabs_visible = await subtabs_rank.is_visible()
            print(f"   Ranking subtabs visible: {'✅' if subtabs_visible else '❌'}")

            # Debug: List all graph elements in the page
            all_graphs = await page.locator(".js-plotly-plot").all()
            print(f"   Total plotly graphs on page: {len(all_graphs)}")

            # Debug: Check for any element with id containing "rank"
            rank_elements = await page.locator("[id*='rank']").all()
            print(f"   Elements with 'rank' in id: {len(rank_elements)}")
            for i, el in enumerate(rank_elements[:15]):
                try:
                    el_id = await el.get_attribute("id")
                    el_tag = await el.evaluate("el => el.tagName")
                    print(f"      {i}: {el_tag} id='{el_id}'")
                except:
                    pass

            # Check for the heatmap graph
            graph_rank1 = page.locator("#graph-rank1")
            graph_rank1_exists = await graph_rank1.count() > 0
            print(
                f"   Heatmap graph (graph-rank1) exists: {'✅' if graph_rank1_exists else '❌'}"
            )

            # Check for the scatter plot graph
            graph_rank2 = page.locator("#graph-rank2")
            graph_rank2_exists = await graph_rank2.count() > 0
            print(
                f"   Scatter plot (graph-rank2) exists: {'✅' if graph_rank2_exists else '❌'}"
            )

            # Check if graphs have actual content (not empty)
            if graph_rank1_exists:
                # Check if the graph has any plotly traces
                graph1_has_content = await page.evaluate("""
                    () => {
                        const graph = document.querySelector('#graph-rank1 .js-plotly-plot');
                        if (graph && graph._fullData) {
                            return graph._fullData.length > 0;
                        }
                        return false;
                    }
                """)
                print(f"   Heatmap has content: {'✅' if graph1_has_content else '❌'}")
            else:
                graph1_has_content = False

            if graph_rank2_exists:
                graph2_has_content = await page.evaluate("""
                    () => {
                        const graph = document.querySelector('#graph-rank2 .js-plotly-plot');
                        if (graph && graph._fullData) {
                            return graph._fullData.length > 0;
                        }
                        return false;
                    }
                """)
                print(
                    f"   Scatter plot has content: {'✅' if graph2_has_content else '❌'}"
                )
            else:
                graph2_has_content = False

            # Step 6: Check that forest plot panel is hidden
            print("\n🚀 Step 6: Verifying bottom panel (forest plots) is hidden...")

            tab2 = page.locator("#tab2")
            tab2_style = (
                await tab2.get_attribute("style") if await tab2.count() > 0 else ""
            )
            tab2_hidden = (
                "display: none" in (tab2_style or "").lower()
                or "none" in (tab2_style or "").lower()
            )
            print(f"   Pairwise tab (tab2) hidden: {'✅' if tab2_hidden else '❌'}")

            # Step 7: Click on "P-scores Scatter plot" subtab
            print("\n🚀 Step 7: Testing scatter plot subtab...")

            scatter_tab = page.locator("#tab-rank2")
            if await scatter_tab.count() > 0:
                try:
                    await scatter_tab.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Clicked scatter plot subtab")

                    # Verify scatter plot is now visible
                    scatter_visible = await graph_rank2.is_visible()
                    print(
                        f"   Scatter plot visible after click: {'✅' if scatter_visible else '❌'}"
                    )
                except Exception as e:
                    print(f"⚠️  Could not click scatter tab: {e}")

            # Take screenshots
            print("\n📸 Taking screenshots...")
            await page.screenshot(
                path="/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/ranking_heatmap_screenshot.png"
            )

            # Click back to heatmap tab
            heatmap_tab = page.locator("#tab-rank1")
            if await heatmap_tab.count() > 0:
                await heatmap_tab.click()
                await page.wait_for_timeout(500)

            await page.screenshot(
                path="/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/ranking_scatter_screenshot.png"
            )
            print("✅ Screenshots saved")

            # Report console errors
            if console_errors:
                print(f"\n⚠️  Console errors found ({len(console_errors)}):")
                for i, error in enumerate(console_errors[:5], 1):
                    print(f"   {i}. {error[:150]}...")
            else:
                print("\n✅ No console errors")

            # Summary
            results = {
                "ranking_tab_visible": ranking_tab_visible,
                "subtabs_visible": subtabs_visible,
                "graph_rank1_exists": graph_rank1_exists,
                "graph_rank2_exists": graph_rank2_exists,
                "graph1_has_content": graph1_has_content,
                "graph2_has_content": graph2_has_content,
                "tab2_hidden": tab2_hidden,
                "console_errors": console_errors,
            }

            return results

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            await page.screenshot(
                path="/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/ranking_error_screenshot.png"
            )
            raise
        finally:
            print("\n⏸️  Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()


if __name__ == "__main__":
    print("🧪 Running Ranking Plots Test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 70)

    try:
        results = asyncio.run(test_ranking_plots())

        if results is None:
            print("\n❌ Test returned no results - server might not be running")
        else:
            print(f"\n{'=' * 70}")
            print("=== Test Summary ===")
            print(f"{'=' * 70}")
            print(
                f"Ranking tab visible:     {'✅ PASS' if results.get('ranking_tab_visible') else '❌ FAIL'}"
            )
            print(
                f"Subtabs visible:         {'✅ PASS' if results.get('subtabs_visible') else '❌ FAIL'}"
            )
            print(
                f"Heatmap graph exists:    {'✅ PASS' if results.get('graph_rank1_exists') else '❌ FAIL'}"
            )
            print(
                f"Scatter graph exists:    {'✅ PASS' if results.get('graph_rank2_exists') else '❌ FAIL'}"
            )
            print(
                f"Heatmap has content:     {'✅ PASS' if results.get('graph1_has_content') else '❌ FAIL'}"
            )
            print(
                f"Scatter has content:     {'✅ PASS' if results.get('graph2_has_content') else '❌ FAIL'}"
            )
            print(
                f"Forest panel hidden:     {'✅ PASS' if results.get('tab2_hidden') else '❌ FAIL'}"
            )
            print(
                f"No console errors:       {'✅ PASS' if not results.get('console_errors') else '❌ FAIL'}"
            )

            all_passed = all(
                [
                    results.get("ranking_tab_visible"),
                    results.get("subtabs_visible"),
                    results.get("graph_rank1_exists"),
                    results.get("graph_rank2_exists"),
                    results.get("graph1_has_content"),
                    results.get("graph2_has_content"),
                    results.get("tab2_hidden"),
                    not results.get("console_errors"),
                ]
            )

            if all_passed:
                print(f"\n{'=' * 70}")
                print("✅ ALL TESTS PASSED - Ranking plots working correctly!")
                print(f"{'=' * 70}")
            else:
                print(f"\n{'=' * 70}")
                print("⚠️  SOME TESTS FAILED - Check detailed output above")
                print(f"{'=' * 70}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
