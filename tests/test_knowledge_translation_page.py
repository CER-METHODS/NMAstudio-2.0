#!/usr/bin/env python3
"""
Test Knowledge Translation (SKT) page functionality:
1. Redirect to setup page when results are not ready
2. Page loads correctly after demo is loaded
3. Standard/Advanced toggle works
4. Network graph and comparison grid display correctly
5. Modal interactions work
"""

import asyncio
from playwright.async_api import async_playwright


async def test_knowledge_translation_page():
    """Test Knowledge Translation page functionality"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Collect console errors
        console_errors = []
        console_warnings = []

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
            elif msg.type == "warning":
                console_warnings.append(msg.text)

        page.on("console", handle_console)

        try:
            print("=" * 70)
            print("KNOWLEDGE TRANSLATION PAGE TEST")
            print("=" * 70)

            # Determine server URL
            base_url = None
            try:
                await page.goto(
                    "http://macas.lan:8050/",
                    wait_until="networkidle",
                    timeout=10000,
                )
                base_url = "http://macas.lan:8050"
            except:
                try:
                    await page.goto(
                        "http://localhost:8050/",
                        wait_until="networkidle",
                        timeout=10000,
                    )
                    base_url = "http://localhost:8050"
                except:
                    print("Could not connect to NMAstudio server")
                    print("Please make sure the server is running with: python app.py")
                    return None

            print(f"Connected to: {base_url}")

            # ========================================
            # TEST 1: Redirect when results not ready
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 1: Redirect when results are not ready")
            print("=" * 70)

            # Clear localStorage to ensure clean state
            await page.evaluate("localStorage.clear()")
            await page.wait_for_timeout(500)

            # Try to navigate directly to KT page
            print("Attempting to navigate directly to /knowledge-translation...")
            await page.goto(
                f"{base_url}/knowledge-translation",
                wait_until="networkidle",
                timeout=15000,
            )
            await page.wait_for_timeout(2000)

            # Check if we got redirected to setup
            current_url = page.url
            redirected_to_setup = "/setup" in current_url

            if redirected_to_setup:
                print(f"✅ Correctly redirected to setup page: {current_url}")
            else:
                # Check if placeholder is shown
                placeholder_visible = await page.is_visible("#kt_not_ready_placeholder")
                if placeholder_visible:
                    print("✅ Placeholder message displayed (results not ready)")
                else:
                    print(f"⚠️  Not redirected, current URL: {current_url}")

            # ========================================
            # TEST 2: Load demo and access KT page
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 2: Load demo and access KT page")
            print("=" * 70)

            # Navigate to setup page
            await page.goto(
                f"{base_url}/setup",
                wait_until="networkidle",
                timeout=15000,
            )
            await page.wait_for_timeout(2000)
            print("Navigated to setup page")

            # Handle dialogs
            async def handle_dialog(dialog):
                await dialog.accept()

            page.on("dialog", handle_dialog)

            # Close any modal that might be open
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)

            # Click load demo button
            print("Loading Psoriasis Demo...")
            try:
                await page.click("#load_psor", timeout=5000)
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Error clicking load demo: {e}")
                return None

            # Wait for redirect to results (demo loads and redirects)
            try:
                await page.wait_for_url("**/results**", timeout=15000)
                print(f"✅ Demo loaded, redirected to: {page.url}")
            except:
                print(f"⚠️  Did not redirect to results, current URL: {page.url}")

            # Wait for data to load
            await page.wait_for_timeout(5000)

            # Clear errors from demo loading
            console_errors.clear()
            console_warnings.clear()

            # Now navigate to Knowledge Translation page
            print("\nNavigating to Knowledge Translation page...")
            await page.goto(
                f"{base_url}/knowledge-translation",
                wait_until="networkidle",
                timeout=15000,
            )
            await page.wait_for_timeout(3000)

            # Check if main content is visible (not the placeholder)
            kt_main_visible = await page.is_visible("#kt_main_content")
            placeholder_visible = await page.is_visible("#kt_not_ready_placeholder")

            if kt_main_visible and not placeholder_visible:
                print("✅ KT main content is visible")
            elif placeholder_visible:
                print("❌ Still showing placeholder (results_ready might not be set)")
            else:
                print(
                    f"⚠️  Unexpected state - main: {kt_main_visible}, placeholder: {placeholder_visible}"
                )

            # ========================================
            # TEST 3: Check page elements
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 3: Check KT page elements")
            print("=" * 70)

            elements_found = {}

            # Check for toggle switch (Standard/Advanced)
            toggle = await page.query_selector("#toggle_grid_select")
            elements_found["toggle_switch"] = toggle is not None
            print(f"{'✅' if toggle else '❌'} Toggle switch (Standard/Advanced)")

            # Check for cytoscape network graph (Standard version uses cytoscape_skt2)
            cyto_skt2 = await page.query_selector("#cytoscape_skt2")
            elements_found["cytoscape_skt2"] = cyto_skt2 is not None
            print(f"{'✅' if cyto_skt2 else '❌'} Cytoscape network (Standard)")

            # Check for treatment comparison grid
            grid_treat = await page.query_selector("#grid_treat_compare")
            elements_found["grid_treat_compare"] = grid_treat is not None
            print(f"{'✅' if grid_treat else '❌'} Treatment comparison grid")

            # Check for transitivity button
            trans_button = await page.query_selector("#trans_button")
            elements_found["trans_button"] = trans_button is not None
            print(f"{'✅' if trans_button else '❌'} Transitivity button")

            # Check for FAQ button
            faq_button = await page.query_selector("#faq_button")
            elements_found["faq_button"] = faq_button is not None
            print(f"{'✅' if faq_button else '❌'} FAQ button")

            # ========================================
            # TEST 4: Test toggle to Advanced version
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 4: Toggle to Advanced version")
            print("=" * 70)

            if toggle:
                try:
                    # Click the toggle to switch to Advanced
                    await toggle.click()
                    await page.wait_for_timeout(2000)
                    print("Clicked toggle to switch to Advanced version")

                    # Check for Advanced version elements
                    cyto_skt = await page.query_selector("#cytoscape_skt")
                    quickstart_grid = await page.query_selector("#quickstart-grid")

                    elements_found["cytoscape_skt"] = cyto_skt is not None
                    elements_found["quickstart_grid"] = quickstart_grid is not None

                    print(f"{'✅' if cyto_skt else '❌'} Cytoscape network (Advanced)")
                    print(
                        f"{'✅' if quickstart_grid else '❌'} Quickstart grid (Advanced)"
                    )

                    # Toggle back to Standard
                    await toggle.click()
                    await page.wait_for_timeout(2000)
                    print("Toggled back to Standard version")

                except Exception as e:
                    print(f"Error toggling: {e}")

            # ========================================
            # TEST 5: Test modal interactions
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 5: Test modal interactions")
            print("=" * 70)

            # Test transitivity modal
            if trans_button:
                try:
                    await trans_button.click()
                    await page.wait_for_timeout(1000)

                    modal_trans = await page.query_selector("#modal_transitivity")
                    modal_visible = modal_trans and await page.is_visible(
                        "#modal_transitivity"
                    )

                    if modal_visible:
                        print("✅ Transitivity modal opened")

                        # Check for boxplot
                        boxplot = await page.query_selector("#boxplot_skt")
                        print(
                            f"{'✅' if boxplot else '❌'} Boxplot in transitivity modal"
                        )

                        # Close modal
                        close_btn = await page.query_selector("#close_trans")
                        if close_btn:
                            await close_btn.click()
                            await page.wait_for_timeout(500)
                            print("✅ Closed transitivity modal")
                    else:
                        print("❌ Transitivity modal did not open")
                except Exception as e:
                    print(f"Error testing transitivity modal: {e}")

            # Test FAQ toast
            faq_button = await page.query_selector("#faq_button")
            if faq_button:
                try:
                    await faq_button.click()
                    await page.wait_for_timeout(1000)

                    faq_toast = await page.is_visible("#faq_toast")
                    if faq_toast:
                        print("✅ FAQ toast opened")

                        # Close FAQ
                        close_faq = await page.query_selector("#close_faq")
                        if close_faq:
                            await close_faq.click()
                            await page.wait_for_timeout(500)
                    else:
                        print("⚠️  FAQ toast not visible")
                except Exception as e:
                    print(f"Error testing FAQ: {e}")

            # ========================================
            # TEST 6: Console error check
            # ========================================
            print("\n" + "=" * 70)
            print("TEST 6: Console error analysis")
            print("=" * 70)

            # Filter critical errors
            critical_errors = [
                e
                for e in console_errors
                if "nonexistent" in e.lower()
                or "typeerror" in e.lower()
                or "referenceerror" in e.lower()
                or "cannot read" in e.lower()
            ]

            print(f"Total console errors: {len(console_errors)}")
            print(f"Total console warnings: {len(console_warnings)}")
            print(f"Critical errors: {len(critical_errors)}")

            if critical_errors:
                print("\nCritical errors found:")
                for error in critical_errors[:5]:
                    print(f"   - {error[:100]}")

            # Take screenshot
            screenshot_path = "/Users/tosku/Sync/Documents/nmastudio/opencode/NMAstudio-app/tests/kt_page_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"\n📸 Screenshot saved to: {screenshot_path}")

            # ========================================
            # SUMMARY
            # ========================================
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            success_criteria = {
                "Redirect works (or placeholder shown)": redirected_to_setup
                or placeholder_visible,
                "KT main content visible after demo": kt_main_visible,
                "Toggle switch present": elements_found.get("toggle_switch", False),
                "Cytoscape network (Standard)": elements_found.get(
                    "cytoscape_skt2", False
                ),
                "Treatment comparison grid": elements_found.get(
                    "grid_treat_compare", False
                ),
                "No critical console errors": len(critical_errors) == 0,
            }

            all_passed = True
            for criterion, passed in success_criteria.items():
                status = "PASS" if passed else "FAIL"
                print(f"[{status}] {criterion}")
                if not passed:
                    all_passed = False

            if all_passed:
                print("\n✅ ALL TESTS PASSED!")
            else:
                print("\n❌ SOME TESTS FAILED")

            # Keep browser open briefly
            print("\nKeeping browser open for 3 seconds...")
            await page.wait_for_timeout(3000)

            await browser.close()

            return {
                "success": all_passed,
                "criteria": success_criteria,
                "elements_found": elements_found,
                "console_errors": console_errors,
                "critical_errors": critical_errors,
            }

        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            await browser.close()
            raise


if __name__ == "__main__":
    print("Running Knowledge Translation Page Test...")
    print("This test will:")
    print("  1. Check redirect when results are not ready")
    print("  2. Load psoriasis demo")
    print("  3. Navigate to Knowledge Translation page")
    print("  4. Test Standard/Advanced toggle")
    print("  5. Test modal interactions")
    print("  6. Check for console errors")
    print("=" * 70)

    try:
        results = asyncio.run(test_knowledge_translation_page())

        if results and results.get("success"):
            print("\n✅ Test completed successfully!")
            exit(0)
        elif results:
            print("\n❌ Test completed with failures")
            exit(1)
        else:
            print("\n❌ Test returned no results")
            exit(1)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
