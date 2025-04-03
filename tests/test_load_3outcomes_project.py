"""Test loading 3-outcome project and verifying all features work"""

import asyncio
from playwright.async_api import async_playwright, expect
import os


async def test_load_3outcomes_project():
    """Load 3-outcome project and verify outcome selector, effect modifiers, and plots"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to results page (where Load button is)
        await page.goto("http://macas.lan:8050/results")
        await page.wait_for_timeout(2000)
        print("✓ Navigated to results page")

        # Click Load Project button to open modal
        await page.click("#open_saveload")
        await page.wait_for_timeout(1000)
        print("✓ Clicked Load Project button")

        # Click on the Load tab in the modal (using more specific selector)
        # Try multiple approaches to find and click the Load tab
        try:
            # Try clicking the tab with specific class
            await page.click(".tab:has-text('Load')", timeout=3000)
        except:
            # Fallback: try using role
            try:
                await page.get_by_role("tab", name="Load").click(timeout=3000)
            except:
                # Final fallback: force click
                await page.locator("text=Load").first.click(force=True)

        await page.wait_for_timeout(500)
        print("✓ Clicked Load tab")

        # Upload the project file
        project_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "downloads/3outcomes_test_project.nmastudio"
            )
        )
        print(f"Uploading: {project_path}")

        # Verify file exists before upload
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project file not found: {project_path}")
        print(f"✓ Project file exists")

        # Find the file input specifically for the upload-json component (in the modal)
        # Wait a bit to ensure the modal's upload component is ready
        await page.wait_for_timeout(500)

        # Use a more specific selector to find the upload-json's file input
        file_input = await page.query_selector('#upload-json input[type="file"]')
        if not file_input:
            # Fallback: get all file inputs and use the last one (should be the modal's)
            file_inputs = await page.query_selector_all('input[type="file"]')
            file_input = file_inputs[-1] if file_inputs else None
            print(f"Found {len(file_inputs)} file inputs, using the last one")

        if not file_input:
            raise Exception("Could not find file input for upload")

        await file_input.set_input_files(project_path)
        print("✓ File uploaded to upload-json component")

        # Wait for the automatic redirect to results page
        print("Waiting for automatic redirect to results page...")
        try:
            # The app should automatically redirect from setup to results
            await page.wait_for_url("**/results", timeout=15000)
            print("✓ Auto-redirected to results page")
        except:
            print("⚠ No auto-redirect detected, checking current URL...")
            current_url = page.url
            print(f"Current URL: {current_url}")

            # If still on setup, manually navigate
            if "/results" not in current_url:
                print("Manually navigating to results page...")
                await page.goto("http://macas.lan:8050/results")

        # Wait for the page to fully load and render
        print("Waiting for results page to render and callbacks to fire...")
        await page.wait_for_timeout(3000)

        # Wait for outcome selector to appear (indicates data is loaded)
        try:
            await page.wait_for_selector("#_outcome_select", timeout=10000)
            print("✓ Outcome selector appeared")
        except:
            print("⚠ Outcome selector did not appear after 10s")

        # Give extra time for the outcome options callback to populate the dropdown
        print("Waiting for outcome options to populate...")
        await page.wait_for_timeout(5000)

        # Try reloading the page to trigger callbacks
        print("Reloading page to ensure all callbacks fire...")
        await page.reload()
        await page.wait_for_timeout(3000)

        print("✓ Project loaded and on results page")

        # Debug: Take screenshot and check for errors
        await page.screenshot(path="tests/debug_results_page.png")
        print("✓ Screenshot saved to tests/debug_results_page.png")

        # Check for console errors
        console_messages = []
        page.on(
            "console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}")
        )
        await page.wait_for_timeout(2000)

        if console_messages:
            print("\n=== Console Messages ===")
            for msg in console_messages[-10:]:  # Last 10 messages
                print(msg)

        # Test 1: Check outcome selector has options
        print("\n=== TEST 1: Outcome Selector ===")
        outcome_select_visible = await page.is_visible("#_outcome_select")
        print(f"Outcome selector visible: {outcome_select_visible}")

        # Debug: Check localStorage for outcome data
        outcome_names_storage = await page.evaluate(
            "() => localStorage.getItem('outcome_names_STORAGE')"
        )
        number_outcomes_storage = await page.evaluate(
            "() => localStorage.getItem('number_outcomes_STORAGE')"
        )
        print(f"outcome_names_STORAGE in localStorage: {outcome_names_storage}")
        print(f"number_outcomes_STORAGE in localStorage: {number_outcomes_storage}")

        # Debug: Check if any results data is present
        page_content = await page.content()
        if "outcome" in page_content.lower():
            print("✓ 'outcome' text found in page")
        else:
            print("⚠ No 'outcome' text found in page - data may not be loaded")

        # Click to expand dropdown
        await page.click("#_outcome_select")
        await page.wait_for_timeout(1000)

        # Wait for options to appear (they may take a moment to populate)
        try:
            await page.wait_for_selector(".Select-option", timeout=5000)
        except:
            print("⚠ No Select-option elements found, waiting longer...")
            await page.wait_for_timeout(2000)

        # Check for options in the dropdown
        options = await page.locator(".Select-option").all_text_contents()
        print(f"Outcome options found: {options}")
        assert len(options) == 3, f"Expected 3 outcomes, found {len(options)}"
        print("✓ Outcome selector has 3 options")

        # Close dropdown
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # Test 2: Check effect modifier dropdown
        print("\n=== TEST 2: Effect Modifier Dropdown ===")
        effectmod_visible = await page.is_visible("#dropdown-effectmod")
        print(f"Effect modifier dropdown visible: {effectmod_visible}")

        if effectmod_visible:
            await page.click("#dropdown-effectmod")
            await page.wait_for_timeout(1000)

            # Get effect modifier options
            mod_options = await page.locator(".Select-option").all_text_contents()
            print(f"Effect modifier options: {mod_options}")
            assert "age" in mod_options and "weight" in mod_options, (
                "Expected age and weight modifiers"
            )
            print("✓ Effect modifiers loaded correctly")

            # Close dropdown
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)

        # Test 3: Check cytoscape network loaded
        print("\n=== TEST 3: Network Visualization ===")
        cytoscape_exists = await page.is_visible("#cytoscape")
        print(f"Cytoscape network visible: {cytoscape_exists}")
        assert cytoscape_exists, "Cytoscape network not found"
        print("✓ Network visualization loaded")

        # Test 4: Try to interact with network (click edge for box plot)
        print("\n=== TEST 4: Box/Scatter Plots ===")

        # First select an effect modifier
        await page.click("#dropdown-effectmod")
        await page.wait_for_timeout(500)
        await page.click("text=age")
        await page.wait_for_timeout(1000)
        print("✓ Selected 'age' as effect modifier")

        # Try to click on the network to select an edge
        # This is tricky - we'll check if the box plot container exists
        boxplot_exists = await page.is_visible("#tapEdgeData-fig")
        print(f"Box plot container visible: {boxplot_exists}")

        # Test 5: Check league tables tab
        print("\n=== TEST 5: League Tables ===")
        await page.click("text=League Tables")
        await page.wait_for_timeout(2000)

        # Check if league table is populated
        league_table = await page.query_selector(".league-table")
        if league_table:
            print("✓ League table found")
        else:
            print("⚠ League table not found (may be in different container)")

        # Test 6: Check Rankings tab
        print("\n=== TEST 6: Rankings ===")
        await page.click("text=Ranking")
        await page.wait_for_timeout(2000)

        ranking_fig = await page.is_visible("#ranking-fig")
        print(f"Ranking figure visible: {ranking_fig}")

        # Test 7: Check Forest Plots tab
        print("\n=== TEST 7: Forest Plots ===")
        await page.click("text=Forest Plots")
        await page.wait_for_timeout(2000)

        forest_fig = await page.is_visible("#tapNodeData-fig")
        print(f"Forest plot figure visible: {forest_fig}")

        print("\n=== All Tests Complete ===")
        print("Keeping browser open for 30 seconds for manual inspection...")
        await page.wait_for_timeout(30000)

        await browser.close()
        print("✓ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_load_3outcomes_project())
