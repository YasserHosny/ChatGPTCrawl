from playwright.async_api import async_playwright
import os

async def search_google_and_capture_screenshots(query, result_dir='GoogleSearchResults'):
        """Search Google for the query and capture screenshots of the first few results."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()

            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            page = await context.new_page()
            await page.goto('https://www.google.com')

            # Search Google for the query
            await page.fill('input[name="q"]', query)
            await page.press('input[name="q"]', 'Enter')
            await page.wait_for_load_state('networkidle')

            # Capture screenshots of the first few results
            for i in range(1, 4):
                result_selector = f'#search .g:nth-child({i})'
                if await page.query_selector(result_selector):
                    screenshot_path = os.path.join(result_dir, f'result_{i}.png')
                    await page.screenshot(path=screenshot_path, clip=await page.locator(result_selector).bounding_box())
                    print(f"Screenshot saved as '{screenshot_path}'")

            await browser.close()