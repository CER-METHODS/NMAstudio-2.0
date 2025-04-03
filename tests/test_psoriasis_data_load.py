#!/usr/bin/env python3
"""
Test that loads the psoriasis demo data and verifies that the entire CSV file
@db/psoriasis_long_complete.csv matches exactly with raw_data_STORAGE
"""

import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright


async def test_psoriasis_data_complete_comparison():
    """Load demo data and verify the entire CSV matches raw_data_STORAGE exactly"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("🚀 Navigating to NMAstudio setup page...")

            # Load the setup page
            try:
                await page.goto(
                    "http://macas.lan:8050/setup",
                    wait_until="networkidle",
                    timeout=10000,
                )
            except:
                await page.goto(
                    "http://localhost:8050/setup",
                    wait_until="networkidle",
                    timeout=10000,
                )

            print(f"✅ Page loaded: {page.url}")

            # Inject auto-accept for any confirm dialog
            await page.evaluate("""window.confirm = () => true;""")

            # Clear storage to force fresh load
            await page.evaluate("""localStorage.setItem('raw_data_STORAGE', '');""")

            # Click "Load Psoriasis Demo Project"
            print("🖱️  Clicking demo-load button...")
            await page.click('button[id="load_psor"]')

            # Accept any confirm dialog
            await page.wait_for_timeout(1000)
            await page.evaluate("""window.confirm = () => true;""")
            await page.keyboard.press("Enter")

            # Wait for data to load
            await page.wait_for_timeout(2000)

            # Get the raw_data_STORAGE from localStorage
            raw_data_str = await page.evaluate("""
                () => localStorage.getItem('raw_data_STORAGE')
            """)

            if raw_data_str is None:
                print("❌ raw_data_STORAGE not found in localStorage")
                return False

            # Parse the JSON string (it is double-stringified)
            try:
                raw_data = json.loads(json.loads(raw_data_str))
            except Exception as e:
                print(f"❌ Failed to parse raw_data_STORAGE JSON: {e}")
                return False

            print("✅ raw_data_STORAGE retrieved from localStorage")

            # Load the ground-truth CSV
            csv_path = "db/psoriasis_long_complete.csv"
            # csv_path = "tests/psoriasis_long_complete_wrong.csv"
            try:
                ground_truth = pd.read_csv(csv_path)
                print(
                    f"✅ Ground-truth CSV loaded: {len(ground_truth)} rows, {len(ground_truth.columns)} columns"
                )
            except Exception as e:
                print(f"❌ Failed to load ground-truth CSV: {e}")
                return False

            # Convert CSV to the same format as the JSON data
            # The JSON has: columns, index, data
            csv_columns = list(ground_truth.columns)
            csv_data = ground_truth.values.tolist()

            print(f"📊 CSV structure: {len(csv_columns)} columns, {len(csv_data)} rows")
            print(
                f"📊 JSON structure: {len(raw_data.get('columns', []))} columns, {len(raw_data.get('data', []))} rows"
            )

            # Compare column names exactly
            json_columns = raw_data.get("columns", [])
            if csv_columns != json_columns:
                print("❌ Column names don't match exactly")
                print(f"   CSV columns: {csv_columns}")
                print(f"   JSON columns: {json_columns}")

                # Show detailed differences
                if len(csv_columns) == len(json_columns):
                    for i, (csv_col, json_col) in enumerate(
                        zip(csv_columns, json_columns)
                    ):
                        if csv_col != json_col:
                            print(
                                f"   Column {i}: CSV='{csv_col}' vs JSON='{json_col}'"
                            )
                return False

            print("✅ Column names match exactly")

            # Compare data row by row and column by column
            json_data = raw_data.get("data", [])

            if len(csv_data) != len(json_data):
                print(
                    f"❌ Row count mismatch: CSV has {len(csv_data)} rows, JSON has {len(json_data)} rows"
                )
                return False

            print("✅ Row count matches")

            # Compare each cell
            mismatches = []
            for row_idx, (csv_row, json_row) in enumerate(zip(csv_data, json_data)):
                if len(csv_row) != len(json_row):
                    mismatches.append(
                        f"Row {row_idx}: Column count mismatch ({len(csv_row)} vs {len(json_row)})"
                    )
                    continue

                for col_idx, (csv_val, json_val) in enumerate(zip(csv_row, json_row)):
                    # Handle NaN/null comparisons
                    csv_is_null = pd.isna(csv_val)
                    json_is_null = json_val is None or (
                        isinstance(json_val, float) and pd.isna(json_val)
                    )

                    if csv_is_null and json_is_null:
                        continue
                    elif csv_is_null != json_is_null:
                        col_name = csv_columns[col_idx]
                        mismatches.append(
                            f"Row {row_idx}, Col '{col_name}': CSV={csv_val} vs JSON={json_val} (null mismatch)"
                        )
                    elif str(csv_val) != str(json_val):
                        col_name = csv_columns[col_idx]
                        mismatches.append(
                            f"Row {row_idx}, Col '{col_name}': CSV={csv_val} vs JSON={json_val}"
                        )

                        # Limit error messages to avoid spam
                        if len(mismatches) >= 10:
                            mismatches.append("... (more mismatches found)")
                            break

                if len(mismatches) >= 10:
                    break

            if mismatches:
                print("❌ Data mismatches found:")
                for mismatch in mismatches:
                    print(f"   {mismatch}")
                return False

            print("✅ All data values match exactly")

            # Show sample comparison for verification
            print("\n=== Sample data comparison (first 3 rows) ===")
            for i in range(min(3, len(csv_data))):
                print(f"Row {i}:")
                for j, col_name in enumerate(csv_columns):
                    csv_val = csv_data[i][j]
                    json_val = json_data[i][j]
                    print(f"  {col_name}: CSV={csv_val} | JSON={json_val}")
                print()

            print("🎉 SUCCESS: Complete CSV data matches raw_data_STORAGE exactly!")
            print(f"   ✓ All {len(csv_data)} rows match")
            print(f"   ✓ All {len(csv_columns)} columns match")
            print(f"   ✓ All data values are identical")

            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    print("🧪 Testing complete psoriasis data comparison...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 70)

    try:
        success = asyncio.run(test_psoriasis_data_complete_comparison())
        if success:
            print("\n✅ COMPLETE DATA COMPARISON TEST PASSED!")
            print("   The entire CSV file matches the localStorage data exactly.")
        else:
            print("\n❌ COMPLETE DATA COMPARISON TEST FAILED!")
            print("   There are differences between the CSV and localStorage data.")
    except Exception as e:
        print(f"\n❌ Test crashed: {e}")
        exit(1)
