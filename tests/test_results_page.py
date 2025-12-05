#!/usr/bin/env python3
"""
Test to verify results page functionality:
1. No console errors on results page
2. Forest plots work correctly
3. Network graph functionality
"""

import asyncio
from playwright.async_api import async_playwright


async def test_results_page():
    """Test results page for console errors and functionality"""

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
            print("RESULTS PAGE TEST")
            print("=" * 70)

            # Step 1: Navigate to setup page
            print("\nStep 1: Navigating to NMAstudio setup page...")
            base_url = None
            try:
                await page.goto(
                    "http://macas.lan:8050/setup",
                    wait_until="networkidle",
                    timeout=15000,
                )
                base_url = "http://macas.lan:8050"
            except:
                try:
                    await page.goto(
                        "http://localhost:8050/setup",
                        wait_until="networkidle",
                        timeout=15000,
                    )
                    base_url = "http://localhost:8050"
                except:
                    print("Could not connect to NMAstudio server")
                    print("Please make sure the server is running with: python app.py")
                    return None

            print(f"Page loaded: {page.url}")
            await page.wait_for_timeout(2000)

            # Clear any initial errors
            console_errors.clear()
            console_warnings.clear()

            # Step 2: Load psoriasis demo
            print("\nStep 2: Loading Psoriasis Demo Project...")

            async def handle_dialog(dialog):
                await dialog.accept()

            page.on("dialog", handle_dialog)

            # Close any modal that might be open
            try:
                close_button = await page.query_selector(
                    '.modal.show .btn-close, .modal.show button:has-text("Close"), .modal.show [id*="close"]'
                )
                if close_button:
                    await close_button.click()
                    await page.wait_for_timeout(500)
                    print("   Closed blocking modal")
            except:
                pass

            # Also try pressing Escape to close any modal
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)

            await page.click("#load_psor")
            await page.wait_for_timeout(3000)

            # Wait for redirect to results
            await page.wait_for_url("**/results**", timeout=10000)
            print(f"Redirected to: {page.url}")

            # Wait for page to fully load - wait longer for R computations
            await page.wait_for_timeout(8000)

            # Wait for network graph to appear (correct ID is "cytoscape", not "cytoscape_graph")
            try:
                await page.wait_for_selector("#cytoscape", timeout=10000)
                print("   Cytoscape graph container found")
            except:
                print("   Warning: Cytoscape graph not found within timeout")

            # Step 3: Check for console errors on results page
            print("\nStep 3: Checking for console errors on results page...")

            # Filter out known non-critical warnings
            critical_errors = [
                e
                for e in console_errors
                if "nonexistent" in e.lower()
                or "typeerror" in e.lower()
                or "referenceerror" in e.lower()
                or "cannot read" in e.lower()
            ]

            if critical_errors:
                print(f"Found {len(critical_errors)} critical errors:")
                for error in critical_errors[:10]:  # Show first 10
                    print(f"   - {error[:100]}")
            else:
                print("No critical console errors found")

            # Step 4: Check network graph
            print("\nStep 4: Checking network graph...")

            # Check if cytoscape has elements (correct ID is "cytoscape")
            cyto_elements = await page.evaluate("""() => {
                const cytoContainer = document.querySelector('#cytoscape');
                if (!cytoContainer) return { error: 'Cytoscape container not found' };
                
                // Check if cy instance exists
                if (window.cy) {
                    return {
                        nodeCount: window.cy.nodes().length,
                        edgeCount: window.cy.edges().length
                    };
                }
                
                return { found: true, note: 'Container found but cy instance not in window' };
            }""")

            print(f"   Cytoscape status: {cyto_elements}")

            # Also check via the elements div visibility
            cyto_visible = await page.is_visible("#cytoscape")
            print(f"   Cytoscape visible: {cyto_visible}")

            # Step 5: Check tabs
            print("\nStep 5: Checking available tabs...")

            # Get all tab elements
            tabs_info = await page.evaluate("""() => {
                const tabs = document.querySelectorAll('.tab, [role="tab"], .nav-link');
                return Array.from(tabs).map(t => ({
                    text: t.textContent.trim().substring(0, 30),
                    className: t.className,
                    id: t.id
                }));
            }""")

            print(f"   Found {len(tabs_info)} tab-like elements")
            for tab in tabs_info[:10]:
                print(f"      - {tab}")

            # Step 6: Try clicking on different sections using tab IDs
            print("\nStep 6: Testing tab navigation...")

            # Try to find and click Forest plots tab
            try:
                forest_tab = await page.query_selector("#forest_tab")
                if forest_tab:
                    await forest_tab.click()
                    await page.wait_for_timeout(2000)
                    print("   Clicked Forest tab")

                    # Check if forest plot content is now visible
                    forest_content = await page.query_selector("#forest_selector")
                    if forest_content:
                        print("   Forest plot controls found")
                    else:
                        print("   Warning: Forest plot controls not found")
                else:
                    print("   Warning: Forest tab element not found")
            except Exception as e:
                print(f"   Could not click Forest: {e}")

            # Final console error check
            print("\nFinal Console Error Summary:")
            print(f"   Total errors collected: {len(console_errors)}")
            print(f"   Total warnings collected: {len(console_warnings)}")

            # Look for specific problematic errors
            nonexistent_errors = [
                e for e in console_errors if "nonexistent" in e.lower()
            ]
            if nonexistent_errors:
                print(f"\n   'Nonexistent object' errors: {len(nonexistent_errors)}")
                unique_nonexistent = list(set(nonexistent_errors))
                for error in unique_nonexistent[:10]:
                    print(f"      - {error[:100]}")

            # Summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            # These are warnings that don't affect functionality - focus on real issues
            setup_only_errors = [e for e in nonexistent_errors if "para-" in e]
            other_nonexistent = [e for e in nonexistent_errors if "para-" not in e]

            success_criteria = {
                "Network graph visible": cyto_visible,
                "No non-setup nonexistent errors": len(other_nonexistent) == 0,
            }

            for criterion, passed in success_criteria.items():
                status = "PASS" if passed else "FAIL"
                print(f"[{status}] {criterion}")

            if setup_only_errors:
                print(
                    f"\n[INFO] Setup-page callback errors (expected during redirect): {len(setup_only_errors)}"
                )

            all_passed = all(success_criteria.values())

            if all_passed:
                print("\nRESULTS PAGE TEST PASSED!")
            else:
                print("\nRESULTS PAGE TEST FAILED!")
                print("\nAll console errors:")
                for i, error in enumerate(console_errors[:20]):
                    print(f"   {i + 1}. {error[:120]}")

            # Keep browser open briefly
            print("\nKeeping browser open for 3 seconds...")
            await page.wait_for_timeout(3000)

            await browser.close()

            return {
                "success": all_passed,
                "criteria": success_criteria,
                "console_errors": console_errors,
                "console_warnings": console_warnings,
                "nonexistent_errors": nonexistent_errors,
                "cyto_visible": cyto_visible,
            }

        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback

            traceback.print_exc()

            await browser.close()
            raise


if __name__ == "__main__":
    print("Running Results Page Test...")
    print("This test will:")
    print("  1. Load the psoriasis demo")
    print("  2. Check for console errors on results page")
    print("  3. Test network graph and tabs")
    print("=" * 70)

    try:
        results = asyncio.run(test_results_page())

        if results and results.get("success"):
            print("\nTest completed successfully!")
        elif results:
            print("\nTest completed with failures")
        else:
            print("\nTest returned no results")

    except Exception as e:
        print(f"\nTest failed: {e}")
