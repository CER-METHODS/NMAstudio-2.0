#!/usr/bin/env python3
"""
Test to verify localStorage persistence across page refreshes
"""

import asyncio
from playwright.async_api import async_playwright


async def test_localstorage_persistence():
    """Test that localStorage persists data across page refreshes"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("=" * 70)
            print("🧪 LOCALSTORAGE PERSISTENCE TEST")
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

            # Step 2: Check initial localStorage state
            print("\n📊 Step 2: Checking initial localStorage state...")
            initial_storage = await page.evaluate(
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

            print(f"   nmastudio-version: {initial_storage.get('nmastudio-version')}")
            print(
                f"   raw_data_STORAGE: {'EMPTY' if not initial_storage.get('raw_data_STORAGE') else 'HAS DATA'}"
            )
            print(
                f"   net_data_STORAGE: {'EMPTY' if not initial_storage.get('net_data_STORAGE') else 'HAS DATA'}"
            )
            print(
                f"   results_ready_STORAGE: {initial_storage.get('results_ready_STORAGE')}"
            )

            # Step 3: Load psoriasis demo
            print("\n⏳ Step 3: Loading Psoriasis Demo Project...")

            # Set up dialog handler
            async def handle_dialog(dialog):
                await dialog.accept()

            page.on("dialog", handle_dialog)

            # Click load button
            await page.click("#load_psor")
            await page.wait_for_timeout(3000)  # Wait for data to load

            print("✅ Psoriasis demo loaded")

            # Step 4: Check localStorage after loading demo
            print("\n📊 Step 4: Checking localStorage after loading demo...")
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

            raw_data_has_content = after_load_storage.get("raw_data_STORAGE") not in [
                None,
                {},
            ]
            net_data_has_content = after_load_storage.get("net_data_STORAGE") not in [
                None,
                {},
            ]

            print(
                f"   nmastudio-version: {after_load_storage.get('nmastudio-version')}"
            )
            print(
                f"   raw_data_STORAGE: {'HAS DATA ✅' if raw_data_has_content else 'EMPTY ❌'}"
            )
            print(
                f"   net_data_STORAGE: {'HAS DATA ✅' if net_data_has_content else 'EMPTY ❌'}"
            )
            print(
                f"   results_ready_STORAGE: {after_load_storage.get('results_ready_STORAGE')}"
            )

            # Take screenshot
            await page.screenshot(
                path="tests/psoriasis_workflow/03_data_loaded_before_refresh.png"
            )
            print("📸 Screenshot saved: 03_data_loaded_before_refresh.png")

            # Step 5: Refresh the page
            print("\n🔄 Step 5: Refreshing the page...")
            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(2000)
            print("✅ Page refreshed")

            # Step 6: Check localStorage after refresh
            print("\n📊 Step 6: Checking localStorage after refresh...")
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

            raw_persisted = after_refresh_storage.get("raw_data_STORAGE") not in [
                None,
                {},
            ]
            net_persisted = after_refresh_storage.get("net_data_STORAGE") not in [
                None,
                {},
            ]

            print(
                f"   nmastudio-version: {after_refresh_storage.get('nmastudio-version')}"
            )
            print(
                f"   raw_data_STORAGE: {'PERSISTED ✅' if raw_persisted else 'LOST ❌'}"
            )
            print(
                f"   net_data_STORAGE: {'PERSISTED ✅' if net_persisted else 'LOST ❌'}"
            )
            print(
                f"   results_ready_STORAGE: {after_refresh_storage.get('results_ready_STORAGE')}"
            )

            # Take screenshot after refresh
            await page.screenshot(
                path="tests/psoriasis_workflow/04_data_after_refresh.png"
            )
            print("📸 Screenshot saved: 04_data_after_refresh.png")

            # Step 7: Verify data matches
            print("\n🔍 Step 7: Verifying data integrity...")

            data_matches = after_load_storage.get(
                "raw_data_STORAGE"
            ) == after_refresh_storage.get("raw_data_STORAGE")

            if data_matches:
                print("✅ Data is identical before and after refresh!")
            else:
                print("❌ Data changed after refresh!")

            # Final summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            success_criteria = {
                "Demo loaded successfully": raw_data_has_content
                and net_data_has_content,
                "Data persisted after refresh": raw_persisted and net_persisted,
                "Data integrity maintained": data_matches,
            }

            for criterion, passed in success_criteria.items():
                status = "✅" if passed else "❌"
                print(f"{status} {criterion}")

            all_passed = all(success_criteria.values())
            if all_passed:
                print("\n🎉 LOCALSTORAGE PERSISTENCE TEST PASSED!")
                print("   → Data survives page refreshes")
                print("   → SESSION_TYPE='local' is working correctly")
            else:
                print("\n⚠️  LOCALSTORAGE PERSISTENCE TEST FAILED!")
                if not success_criteria["Demo loaded successfully"]:
                    print("   → Demo did not load properly")
                if not success_criteria["Data persisted after refresh"]:
                    print("   → Data was lost on refresh (check SESSION_TYPE setting)")
                if not success_criteria["Data integrity maintained"]:
                    print("   → Data changed unexpectedly")

            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for 5 seconds...")
            await page.wait_for_timeout(5000)

            await browser.close()

            return {
                "success": all_passed,
                "criteria": success_criteria,
                "initial_storage": initial_storage,
                "after_load_storage": after_load_storage,
                "after_refresh_storage": after_refresh_storage,
            }

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            try:
                await page.screenshot(
                    path="tests/psoriasis_workflow/ERROR_persistence_test.png"
                )
                print("📸 Error screenshot saved: ERROR_persistence_test.png")
            except:
                pass

            await browser.close()
            raise


if __name__ == "__main__":
    print("🧪 Running localStorage Persistence Test...")
    print("This test will:")
    print("  1. Load the psoriasis demo")
    print("  2. Refresh the page")
    print("  3. Verify data persists")
    print("=" * 70)

    try:
        results = asyncio.run(test_localstorage_persistence())

        if results and results.get("success"):
            print("\n✅ Test completed successfully!")
        elif results:
            print("\n⚠️  Test completed with failures")
        else:
            print("\n❌ Test returned no results")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
