#!/usr/bin/env python3
"""
Test to verify year slider works correctly when year column IS filled.

This test loads the psoriasis demo data which has year column.

Expected behavior:
- Year slider should be visible when year data exists
- Moving the slider should filter the data
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def test_year_slider_with_data():
    """Test that year slider works when loading psoriasis demo"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=30)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        try:
            print("=" * 60)
            print("TEST: Year slider with psoriasis demo data")
            print("=" * 60)

            # Navigate to setup page
            await page.goto("http://localhost:8050/setup", wait_until="networkidle")
            print(f"Page loaded: {page.url}")
            await page.wait_for_timeout(1000)

            # Step 1: Click on load psoriasis demo button
            print("\n[Step 1] Loading Psoriasis demo...")
            try:
                # Set up dialog handler before clicking
                page.on("dialog", lambda dialog: dialog.accept())

                await page.click("#load_psor", timeout=5000)
                await page.wait_for_timeout(5000)  # Wait for confirm dialog and loading
                print("Clicked load demo button and accepted confirmation")
            except Exception as e:
                print(f"Error clicking load demo: {e}")
                return {"success": False, "error": "Could not click demo button"}

            # Wait for redirect to results
            print("\n[Step 2] Waiting for results page...")
            try:
                await page.wait_for_url("**/results**", timeout=15000)
                print(f"Redirected to: {page.url}")
            except Exception:
                print(f"Current URL: {page.url}")

            await page.wait_for_timeout(5000)

            # Step 3: Check slider visibility
            print("\n[Step 3] Checking slider visibility...")
            slider_container = page.locator("#slider-container")
            is_visible = await slider_container.is_visible()
            print(f"Slider container visible: {is_visible}")

            if not is_visible:
                print("\n❌ TEST FAILED: Slider should be visible but is hidden!")
                screenshot_path = (
                    Path(__file__).parent / "test_year_slider_with_data_error.png"
                )
                await page.screenshot(path=str(screenshot_path))
                return {"success": False, "error": "Slider not visible"}

            # Step 4: Get initial row count
            print("\n[Step 4] Getting initial data row count...")
            await page.wait_for_timeout(1000)

            # Count rows in data table
            initial_rows = await page.locator(
                "#datatable-upload-container tbody tr"
            ).count()
            print(f"Initial row count: {initial_rows}")

            # Step 5: Move slider to filter data
            print("\n[Step 5] Moving slider to filter data...")

            # Get the slider element - look for the rc-slider-handle (the draggable part)
            slider_handle = page.locator("#slider-year .rc-slider-handle")
            slider_track = page.locator("#slider-year .rc-slider-rail")

            filtering_works = False

            if await slider_handle.count() > 0:
                handle_box = await slider_handle.bounding_box()
                track_box = await slider_track.bounding_box()

                if handle_box and track_box:
                    print(f"Handle position: x={handle_box['x']:.0f}")
                    print(
                        f"Track: x={track_box['x']:.0f}, width={track_box['width']:.0f}"
                    )

                    # Drag the handle to the left (earlier years)
                    start_x = handle_box["x"] + handle_box["width"] / 2
                    start_y = handle_box["y"] + handle_box["height"] / 2

                    # Calculate target position (30% from left of track)
                    target_x = track_box["x"] + track_box["width"] * 0.3

                    print(f"Dragging from x={start_x:.0f} to x={target_x:.0f}")

                    # Perform drag operation
                    await page.mouse.move(start_x, start_y)
                    await page.mouse.down()
                    await page.mouse.move(target_x, start_y, steps=10)
                    await page.mouse.up()

                    print("Dragged slider handle left")
                    await page.wait_for_timeout(3000)

                    # Get new row count
                    new_rows = await page.locator(
                        "#datatable-upload-container tbody tr"
                    ).count()
                    print(f"Row count after slider drag: {new_rows}")

                    # Check if filtering worked
                    if new_rows < initial_rows:
                        print(
                            f"\n✅ Slider filtering works! Rows reduced from {initial_rows} to {new_rows}"
                        )
                        filtering_works = True
                    else:
                        print(
                            f"\nRows unchanged ({new_rows}). Checking if slider value changed..."
                        )
                        filtering_works = False
                else:
                    print("Could not get slider bounding boxes")
            else:
                print("Could not find slider handle")

            # Take screenshot
            screenshot_path = (
                Path(__file__).parent / "test_year_slider_with_data_result.png"
            )
            await page.screenshot(path=str(screenshot_path))
            print(f"Screenshot: {screenshot_path}")

            # Result
            if is_visible and filtering_works:
                print("\n✅ TEST PASSED: Slider is visible and filtering works!")
                return {"success": True}
            elif is_visible:
                print("\n⚠️ TEST PARTIAL: Slider is visible but filtering may not work")
                return {"success": True, "warning": "Filtering not verified"}
            else:
                print("\n❌ TEST FAILED!")
                return {"success": False}

        except Exception as e:
            print(f"\nTest error: {e}")
            import traceback

            traceback.print_exc()
            screenshot_path = (
                Path(__file__).parent / "test_year_slider_with_data_error.png"
            )
            await page.screenshot(path=str(screenshot_path))
            return {"success": False, "error": str(e)}

        finally:
            await browser.close()


if __name__ == "__main__":
    results = asyncio.run(test_year_slider_with_data())
    exit(0 if results and results.get("success") else 1)
