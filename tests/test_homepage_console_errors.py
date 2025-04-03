#!/usr/bin/env python3
"""
Test to visit the NMAstudio homepage and capture console log errors
"""

import asyncio
import time
from playwright.async_api import async_playwright


async def test_homepage_console_errors():
    """Test homepage and capture console log errors"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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
            print("🚀 Navigating to NMAstudio homepage...")

            # Try to start the server if it's not running
            try:
                # First try to navigate to the local server
                await page.goto(
                    "http://macas.lan:8050/", wait_until="networkidle", timeout=10000
                )
            except:
                try:
                    # Fallback to localhost
                    await page.goto(
                        "http://localhost:8050/",
                        wait_until="networkidle",
                        timeout=10000,
                    )
                except:
                    print("❌ Could not connect to NMAstudio server")
                    print("Please make sure the server is running with: python app.py")
                    return

            print(f"✅ Page loaded: {page.url}")

            # Wait for page to fully load
            await page.wait_for_timeout(3000)

            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")

            # Check for JavaScript errors
            js_errors = [
                msg for msg in console_messages if msg["type"] in ["error", "warning"]
            ]

            print(f"\n=== Console Log Analysis ===")
            print(f"Total console messages: {len(console_messages)}")
            print(f"Errors/Warnings: {len(js_errors)}")

            if console_messages:
                print(f"\n--- All Console Messages ({len(console_messages)}) ---")
                for i, msg in enumerate(console_messages, 1):
                    print(f"{i}. [{msg['type']}] {msg['text']}")
                    if msg["location"] != "unknown":
                        print(f"   Location: {msg['location']}")

            if js_errors:
                print(f"\n❌ JavaScript Errors/Warnings Found ({len(js_errors)}):")
                for i, error in enumerate(js_errors, 1):
                    print(f"{i}. [{error['type']}] {error['text']}")
                    if error["location"] != "unknown":
                        print(f"   Location: {error['location']}")
            else:
                print("\n✅ No JavaScript errors or warnings found!")

            # Check for storage elements like the original test
            storage_info = await page.evaluate("""
                () => {
                    const storageState = {
                        dccStores: {},
                        sessionStorage: {},
                        localStorage: {},
                        dashAppData: {}
                    };
                    
                    // Find dcc.Store elements
                    const storeElements = document.querySelectorAll('[id*="STORAGE"]');
                    storeElements.forEach(element => {
                        const id = element.id;
                        if (id) {
                            storageState.dccStores[id] = {
                                id: id,
                                data: element.textContent || 'N/A',
                                storageType: element.getAttribute('storage-type') || 'unknown',
                                elementType: element.tagName
                            };
                        }
                    });
                    
                    // Check sessionStorage
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        if (key && (key.includes('STORAGE') || key.includes('nmastudio'))) {
                            storageState.sessionStorage[key] = {
                                value: sessionStorage.getItem(key),
                                parsed: sessionStorage.getItem(key) || 'empty'
                            };
                        }
                    }
                    
                    // Check localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && (key.includes('STORAGE') || key.includes('nmastudio'))) {
                            storageState.localStorage[key] = {
                                value: localStorage.getItem(key),
                                parsed: localStorage.getItem(key) || 'empty'
                            };
                        }
                    }
                    
                    return storageState;
                }
            """)

            print(f"\n=== Storage State Analysis ===")
            print(f"✓ Found {len(storage_info['dccStores'])} dcc.Store elements")
            print(f"✓ Found {len(storage_info['sessionStorage'])} sessionStorage items")
            print(f"✓ Found {len(storage_info['localStorage'])} localStorage items")

            if storage_info["dccStores"]:
                print(f"\n--- dcc.Store Elements ---")
                for store_id, store_info in storage_info["dccStores"].items():
                    print(f"  - {store_id}: {store_info.get('data', 'N/A')}")

            if storage_info["sessionStorage"]:
                print(f"\n--- SessionStorage ---")
                for key, data in storage_info["sessionStorage"].items():
                    print(f"  - {key}: {data.get('parsed', 'N/A')}")

            # Check for broken images or resources
            failed_requests = []

            def handle_request_failed(request):
                failed_requests.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "failure": request.failure_text
                        if hasattr(request, "failure_text")
                        else "unknown",
                    }
                )

            page.on("requestfailed", handle_request_failed)

            # Reload to capture any failed requests
            await page.reload()
            await page.wait_for_timeout(2000)

            if failed_requests:
                print(f"\n❌ Failed Resource Requests ({len(failed_requests)}):")
                for req in failed_requests:
                    print(f"  - {req['method']} {req['url']}: {req['failure']}")
            else:
                print(f"\n✅ All resource requests successful!")

            return {
                "console_messages": console_messages,
                "js_errors": js_errors,
                "storage_info": storage_info,
                "failed_requests": failed_requests,
                "page_title": title,
            }

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    print("🧪 Running homepage console error test...")
    print("Make sure NMAstudio is running with: python app.py")
    print("=" * 50)

    try:
        results = asyncio.run(test_homepage_console_errors())

        if results is None:
            print("\n❌ Test returned no results - server might not be running")
        else:
            print(f"\n=== Test Summary ===")
            print(f"Page Title: {results.get('page_title', 'Unknown')}")
            print(f"Console Messages: {len(results.get('console_messages', []))}")
            print(f"JS Errors/Warnings: {len(results.get('js_errors', []))}")
            print(
                f"Storage Elements: {len(results.get('storage_info', {}).get('dccStores', []))}"
            )
            print(f"Failed Requests: {len(results.get('failed_requests', []))}")

            if results.get("js_errors") or results.get("failed_requests"):
                print("\n❌ Issues found - check the detailed output above")
            else:
                print(
                    "\n✅ No issues found - homepage appears to be working correctly!"
                )

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
