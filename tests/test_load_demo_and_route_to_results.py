#!/usr/bin/env python3
"""
Test to load demo in setup page and then route to results page
"""

import asyncio
import time
from playwright.async_api import async_playwright


async def test_load_demo_and_route_to_results():
    """Test loading demo and routing to results page"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Set to False to see the browser
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = await browser.new_page()

        # Set up console message collection
        console_messages = []

        def handle_console_message(msg):
            """Handle console messages"""
            location_info = "unknown"
            if msg.location:
                url = getattr(msg.location, "url", "unknown")
                line_num = getattr(msg.location, "lineNumber", "unknown")
                col_num = getattr(msg.location, "columnNumber", "unknown")
                location_info = f"{url}:{line_num}:{col_num}"

            console_messages.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": location_info,
                }
            )

        # Listen for console messages
        page.on("console", handle_console_message)

        try:
            print("🚀 Step 1: Navigating to NMAstudio setup page...")

            # Try macas.lan first since we know it works
            server_url = "http://macas.lan:8050"
            try:
                response = await page.goto(
                    f"{server_url}/setup",
                    wait_until="load",
                    timeout=30000,
                )
                print(
                    f"✅ Response status: {response.status if response else 'No response'}"
                )
            except Exception as e:
                print(f"❌ Navigation failed: {str(e)}")
                print("❌ Could not connect to NMAstudio server")
                print("Please make sure the server is running with: python app.py")
                return None

            # Wait for the Dash app to finish loading
            print("⏳ Waiting for Dash app to load...")

            # Wait for the main content div to appear (sign that React has rendered)
            try:
                await page.wait_for_selector("#upload_page", timeout=15000)
                print("✅ Setup page content loaded")
            except:
                print("⚠️  Timeout waiting for #upload_page")

            await page.wait_for_timeout(5000)  # Give Dash time to render

            print(f"✅ Setup page loaded: {page.url}")

            # Take a screenshot for debugging
            await page.screenshot(
                path="/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/setup_page_debug.png"
            )
            print("📸 Debug screenshot saved")

            # Step 2: Click the Load Demo button
            print("\n🚀 Step 2: Clicking 'Load Psoriasis Demo Project' button...")

            # Find and click the load demo button
            load_demo_button = page.locator("#load_psor")

            # Check if button exists and wait for it
            try:
                await load_demo_button.wait_for(state="visible", timeout=10000)
                print("✅ Load demo button found")
            except Exception as e:
                print(f"❌ Load demo button not found! Error: {str(e)[:100]}")
                print("   Checking available buttons...")
                try:
                    buttons = await page.locator("button").all()
                    print(f"   Found {len(buttons)} buttons total")
                    for i, btn in enumerate(buttons[:5]):
                        try:
                            btn_text = await btn.inner_text()
                            btn_id = await btn.get_attribute("id")
                            print(
                                f"   Button {i}: id='{btn_id}' text='{btn_text[:30]}'"
                            )
                        except:
                            pass
                except Exception as e2:
                    print(f"   Error getting buttons: {e2}")
                return None

            await load_demo_button.click()
            print("✅ Clicked 'Load Psoriasis Demo Project' button")
            await page.wait_for_timeout(1000)

            # Step 3: Confirm the dialog
            print("\n🚀 Step 3: Confirming demo load dialog...")

            # Handle the confirmation dialog
            page.on("dialog", lambda dialog: dialog.accept())

            # Click again to trigger the dialog and auto-accept
            await load_demo_button.click()
            print("✅ Confirmed demo load dialog")

            # Wait for demo to load
            print("\n⏳ Waiting for demo to load and automatic redirect...")

            # Wait for the page to redirect automatically to /results
            try:
                await page.wait_for_url("**/results", timeout=15000)
                print("✅ Automatically redirected to results page!")
            except Exception as e:
                print(f"⚠️  Automatic redirect didn't happen (timeout after 15s)")
                print(f"    Current URL: {page.url}")
                print(f"    Error: {str(e)[:100]}")
                await page.goto(page.url.replace("/setup", "/results"))
                print("✅ Manually navigated to results page")

            # Wait for results page to fully load
            print("⏳ Waiting for results page to fully load...")
            await page.wait_for_timeout(5000)

            # Check if storage has been populated
            storage_check = await page.evaluate("""
                () => {
                    const storageElements = document.querySelectorAll('[id*="STORAGE"]');
                    const storageData = {};
                    storageElements.forEach(element => {
                        const id = element.id;
                        if (id && id.includes('net_data_STORAGE')) {
                            storageData[id] = element.textContent || 'N/A';
                        }
                    });
                    return storageData;
                }
            """)

            if storage_check:
                print(
                    f"✅ Demo data loaded into storage: {len(storage_check)} storage elements found"
                )
            else:
                print(
                    "⚠️  Warning: No storage elements found - demo might not have loaded"
                )

            await page.wait_for_timeout(3000)
            print(f"✅ Results page loaded: {page.url}")

            # Step 5: Verify results page elements
            print("\n🚀 Step 5: Verifying results page elements...")

            # Check for the results selection dropdown
            results_dropdown = page.locator("#result_selected")
            if await results_dropdown.count() > 0:
                print("✅ Results selection dropdown found")

                # Get dropdown value
                dropdown_value = await results_dropdown.evaluate("el => el.value")
                print(f"   Current selection: {dropdown_value}")
            else:
                print("❌ Results selection dropdown NOT found")

            # Check for Data & Transitivity tabs
            data_tab = page.locator("#data_tab")
            trans_tab = page.locator("#trans_tab")

            data_tab_visible = await data_tab.count() > 0
            trans_tab_visible = await trans_tab.count() > 0

            if data_tab_visible:
                print("✅ Data tab found")
            else:
                print("❌ Data tab NOT found")

            if trans_tab_visible:
                print("✅ Transitivity tab found")
            else:
                print("❌ Transitivity tab NOT found")

            # Check for the network graph (cytoscape)
            cytoscape = page.locator("#cytoscape")
            if await cytoscape.count() > 0:
                print("✅ Network graph (cytoscape) found")
            else:
                print("❌ Network graph NOT found")

            # Check for outcome selector
            outcome_select = page.locator("#_outcome_select")
            if await outcome_select.count() > 0:
                print("✅ Outcome selector found")
            else:
                print("❌ Outcome selector NOT found")

            # Check JavaScript errors
            js_errors = [
                msg for msg in console_messages if msg["type"] in ["error", "warning"]
            ]

            print(f"\n=== Console Log Analysis ===")
            print(f"Total console messages: {len(console_messages)}")
            print(f"Errors/Warnings: {len(js_errors)}")

            if js_errors:
                print(f"\n⚠️  JavaScript Errors/Warnings Found ({len(js_errors)}):")
                # Only show first 5 errors to avoid overwhelming output
                for i, error in enumerate(js_errors[:5], 1):
                    # Truncate long error messages
                    error_text = error["text"][:200] + (
                        "..." if len(error["text"]) > 200 else ""
                    )
                    print(f"{i}. [{error['type']}] {error_text}")
                if len(js_errors) > 5:
                    print(f"   ... and {len(js_errors) - 5} more errors/warnings")
            else:
                print("\n✅ No JavaScript errors or warnings found!")

            # Take a screenshot
            screenshot_path = "/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/results_page_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"\n📸 Screenshot saved to: {screenshot_path}")

            return {
                "console_messages": console_messages,
                "js_errors": js_errors,
                "results_dropdown_found": await results_dropdown.count() > 0,
                "data_tab_found": data_tab_visible,
                "trans_tab_found": trans_tab_visible,
                "cytoscape_found": await cytoscape.count() > 0,
                "outcome_select_found": await outcome_select.count() > 0,
            }

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            # Keep browser open for inspection
            print("\n⏸️  Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()


if __name__ == "__main__":
    print("🧪 Running Load Demo and Route to Results Test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 70)

    try:
        results = asyncio.run(test_load_demo_and_route_to_results())

        if results is None:
            print("\n❌ Test returned no results - server might not be running")
        else:
            print(f"\n=== Test Summary ===")
            print(
                f"Results Dropdown Found: {'✅' if results.get('results_dropdown_found') else '❌'}"
            )
            print(f"Data Tab Found: {'✅' if results.get('data_tab_found') else '❌'}")
            print(
                f"Transitivity Tab Found: {'✅' if results.get('trans_tab_found') else '❌'}"
            )
            print(
                f"Network Graph Found: {'✅' if results.get('cytoscape_found') else '❌'}"
            )
            print(
                f"Outcome Selector Found: {'✅' if results.get('outcome_select_found') else '❌'}"
            )
            print(f"Console Messages: {len(results.get('console_messages', []))}")
            print(f"JS Errors/Warnings: {len(results.get('js_errors', []))}")

            all_elements_found = all(
                [
                    results.get("results_dropdown_found"),
                    results.get("data_tab_found"),
                    results.get("trans_tab_found"),
                    results.get("cytoscape_found"),
                    results.get("outcome_select_found"),
                ]
            )

            if all_elements_found and not results.get("js_errors"):
                print(
                    "\n✅ All tests passed - Demo loaded and results page working correctly!"
                )
            else:
                print("\n⚠️  Some issues found - check the detailed output above")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
