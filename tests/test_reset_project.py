#!/usr/bin/env python3
"""
Test to verify reset_project clears localStorage properly
"""

import asyncio
from playwright.async_api import async_playwright


async def test_reset_project():
    """Test that reset_project clears all data including localStorage"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("=" * 70)
            print("🧪 RESET PROJECT TEST")
            print("=" * 70)

            # Step 1: Navigate to setup page
            print("\n🚀 Step 1: Navigating to NMAstudio setup page...")
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
            await page.wait_for_timeout(2000)

            # Step 2: Load psoriasis demo
            print("\n⏳ Step 2: Loading Psoriasis Demo Project...")

            # Set up dialog handler
            async def handle_dialog(dialog):
                print(f"   📢 Dialog: {dialog.message}")
                await dialog.accept()
                print("   ✅ Dialog accepted")

            page.on("dialog", handle_dialog)

            # Click load button
            await page.click("#load_psor")
            await page.wait_for_timeout(3000)  # Wait for data to load

            print("✅ Psoriasis demo loaded")

            # Step 3: Verify data is loaded
            print("\n📊 Step 3: Verifying data is loaded in localStorage...")
            after_load_storage = await page.evaluate(
                """() => {
                const keys = [
                    'nmastudio-version',
                    'raw_data_STORAGE',
                    'net_data_STORAGE',
                    'results_ready_STORAGE'
                ];
                
                const result = {};
                keys.forEach(key => {
                    const value = localStorage.getItem(key);
                    result[key] = value ? JSON.parse(value) : null;
                });
                
                return result;
            }"""
            )

            raw_has_data = after_load_storage.get("raw_data_STORAGE") not in [None, {}]
            net_has_data = after_load_storage.get("net_data_STORAGE") not in [None, {}]

            print(
                f"   nmastudio-version: {after_load_storage.get('nmastudio-version')}"
            )
            print(
                f"   raw_data_STORAGE: {'HAS DATA ✅' if raw_has_data else 'EMPTY ❌'}"
            )
            print(
                f"   net_data_STORAGE: {'HAS DATA ✅' if net_has_data else 'EMPTY ❌'}"
            )
            print(
                f"   results_ready_STORAGE: {after_load_storage.get('results_ready_STORAGE')}"
            )

            # Take screenshot
            await page.screenshot(path="tests/psoriasis_workflow/05_before_reset.png")
            print("📸 Screenshot saved: 05_before_reset.png")

            # Step 4: Click reset project button
            print("\n⏳ Step 4: Clicking 'Reset Project' button...")

            # Check if button exists
            reset_button_exists = await page.locator("#reset_project").count() > 0
            if not reset_button_exists:
                print("❌ 'Reset Project' button not found!")
                print("Available buttons with IDs:")
                buttons = await page.evaluate(
                    """() => {
                    const btns = Array.from(document.querySelectorAll('button[id]'));
                    return btns.map(b => ({ id: b.id, text: b.textContent }));
                }"""
                )
                for btn in buttons:
                    print(f"  - #{btn['id']}: {btn['text']}")
                return None

            print("✅ Found 'Reset Project' button")

            # Click reset button (will trigger confirm dialog)
            await page.click("#reset_project")
            print("   ⏳ Waiting for confirmation dialog...")

            # Wait for dialog and callback to complete
            await page.wait_for_timeout(2000)

            # Take screenshot after reset
            await page.screenshot(path="tests/psoriasis_workflow/06_after_reset.png")
            print("📸 Screenshot saved: 06_after_reset.png")

            # Step 5: Verify data is cleared
            print("\n📊 Step 5: Verifying data is cleared from localStorage...")
            after_reset_storage = await page.evaluate(
                """() => {
                const keys = [
                    'nmastudio-version',
                    'raw_data_STORAGE',
                    'net_data_STORAGE',
                    'results_ready_STORAGE'
                ];
                
                const result = {};
                keys.forEach(key => {
                    const value = localStorage.getItem(key);
                    result[key] = value ? JSON.parse(value) : null;
                });
                
                return result;
            }"""
            )

            raw_is_empty = after_reset_storage.get("raw_data_STORAGE") in [None, {}]
            net_is_empty = after_reset_storage.get("net_data_STORAGE") in [None, {}]
            results_cleared = not after_reset_storage.get(
                "results_ready_STORAGE", False
            )

            print(
                f"   nmastudio-version: {after_reset_storage.get('nmastudio-version')}"
            )
            print(
                f"   raw_data_STORAGE: {'CLEARED ✅' if raw_is_empty else 'STILL HAS DATA ❌'}"
            )
            print(
                f"   net_data_STORAGE: {'CLEARED ✅' if net_is_empty else 'STILL HAS DATA ❌'}"
            )
            print(
                f"   results_ready_STORAGE: {after_reset_storage.get('results_ready_STORAGE')} {'✅' if results_cleared else '❌'}"
            )

            # Step 6: Refresh page to verify reset persists
            print("\n🔄 Step 6: Refreshing page to verify reset persists...")
            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(2000)
            print("✅ Page refreshed")

            # Step 7: Check localStorage after refresh
            print("\n📊 Step 7: Checking localStorage after refresh...")
            after_refresh_storage = await page.evaluate(
                """() => {
                const keys = [
                    'nmastudio-version',
                    'raw_data_STORAGE',
                    'net_data_STORAGE',
                    'results_ready_STORAGE'
                ];
                
                const result = {};
                keys.forEach(key => {
                    const value = localStorage.getItem(key);
                    result[key] = value ? JSON.parse(value) : null;
                });
                
                return result;
            }"""
            )

            raw_still_empty = after_refresh_storage.get("raw_data_STORAGE") in [
                None,
                {},
            ]
            net_still_empty = after_refresh_storage.get("net_data_STORAGE") in [
                None,
                {},
            ]
            results_still_cleared = not after_refresh_storage.get(
                "results_ready_STORAGE", False
            )

            print(
                f"   nmastudio-version: {after_refresh_storage.get('nmastudio-version')}"
            )
            print(
                f"   raw_data_STORAGE: {'STILL EMPTY ✅' if raw_still_empty else 'DATA RETURNED ❌'}"
            )
            print(
                f"   net_data_STORAGE: {'STILL EMPTY ✅' if net_still_empty else 'DATA RETURNED ❌'}"
            )
            print(
                f"   results_ready_STORAGE: {after_refresh_storage.get('results_ready_STORAGE')} {'✅' if results_still_cleared else '❌'}"
            )

            # Take final screenshot
            await page.screenshot(
                path="tests/psoriasis_workflow/07_after_refresh_post_reset.png"
            )
            print("📸 Screenshot saved: 07_after_refresh_post_reset.png")

            # Final summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            success_criteria = {
                "Demo loaded successfully": raw_has_data and net_has_data,
                "Reset button found": reset_button_exists,
                "Data cleared after reset": raw_is_empty
                and net_is_empty
                and results_cleared,
                "Reset persists after refresh": raw_still_empty
                and net_still_empty
                and results_still_cleared,
            }

            for criterion, passed in success_criteria.items():
                status = "✅" if passed else "❌"
                print(f"{status} {criterion}")

            all_passed = all(success_criteria.values())
            if all_passed:
                print("\n🎉 RESET PROJECT TEST PASSED!")
                print("   → Reset button works correctly")
                print("   → localStorage is properly cleared")
                print("   → Reset persists across page refreshes")
            else:
                print("\n⚠️  RESET PROJECT TEST FAILED!")
                if not success_criteria["Demo loaded successfully"]:
                    print("   → Demo did not load properly")
                if not success_criteria["Reset button found"]:
                    print("   → Reset button not found")
                if not success_criteria["Data cleared after reset"]:
                    print("   → Data was not cleared after reset")
                if not success_criteria["Reset persists after refresh"]:
                    print("   → Reset did not persist after page refresh")

            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for 5 seconds...")
            await page.wait_for_timeout(5000)

            await browser.close()

            return {
                "success": all_passed,
                "criteria": success_criteria,
                "after_load_storage": after_load_storage,
                "after_reset_storage": after_reset_storage,
                "after_refresh_storage": after_refresh_storage,
            }

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            try:
                await page.screenshot(
                    path="tests/psoriasis_workflow/ERROR_reset_test.png"
                )
                print("📸 Error screenshot saved: ERROR_reset_test.png")
            except:
                pass

            await browser.close()
            raise


if __name__ == "__main__":
    print("🧪 Running Reset Project Test...")
    print("This test will:")
    print("  1. Load the psoriasis demo")
    print("  2. Click 'Reset Project' button")
    print("  3. Verify localStorage is cleared")
    print("  4. Refresh and verify reset persists")
    print("=" * 70)

    try:
        results = asyncio.run(test_reset_project())

        if results and results.get("success"):
            print("\n✅ Test completed successfully!")
        elif results:
            print("\n⚠️  Test completed with failures")
        else:
            print("\n❌ Test returned no results")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
