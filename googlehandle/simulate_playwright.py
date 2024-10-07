import asyncio
from playwright.async_api import async_playwright
import base64
from io import BytesIO
import os


async def search_image_with_google_lens(b64_image):
    async with async_playwright() as p:
        image_path = base64_to_image(b64_image)
        remove_old_files()

        # Launch the browser and set up context with realistic settings
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            color_scheme="light",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        page = await context.new_page()
        await page.goto('https://www.google.com/imghp?hl=en&tab=ri&ogbl')
        await page.wait_for_timeout(5000)

        # Handle consent screen if it appears
        if await page.query_selector('button[id="L2AGLb"]'):
            await handle_click(page, 'button[id="L2AGLb"]')
            print("Consent button clicked")

        # Upload the image
        await handle_click(page, 'div[jsname="R5mgy"]')
        await page.set_input_files('input[type="file"]', image_path)
        await page.wait_for_timeout(10000)

        await take_screenshot(page, 'GoogleResults/all_results.png')

        # Handle "Exact matches" if it exists
        exact_matches_selector = 'div[jsaction="rcuQ6b:npT2md"] div[jscontroller="MLRnpc"]'
        result_selector = 'ul li a'  # Default first result selector

        if await page.query_selector(exact_matches_selector):
            await handle_click(page, exact_matches_selector)
            await page.wait_for_timeout(10000)
            await take_screenshot(page, 'GoogleResults/exact_matches_screenshot.png')
            result_selector = 'ul li a'  # Default first result selector
            elements = await page.query_selector_all(result_selector)
        else:
            print("'Exact matches' not found, clicking on the first result directly.")
            result_selector = 'div[class="G19kAf ENn9pd"] a'  # Adjust this selector as needed
            elements = await page.query_selector_all(result_selector)

         # Loop over the first 3 results
        for i, element in enumerate(elements[:3], start=1):  # Limit to 3 elements
                try:
                    if element:
                        async with page.context.expect_page() as new_page_info:
                            await element.click()
                        new_page = await new_page_info.value
                        await new_page.wait_for_load_state('load')
                        screenshot_path = f'GoogleResults/Single_result_screenshot_{i}.png'
                        await take_screenshot(new_page, screenshot_path)
                    else:
                        print(f"No result found for selector: {result_selector} (element {i})")
                except Exception as e:
                    print(f"Error occurred while handling result {i} with selector '{result_selector}': {str(e)}")

        await browser.close()

def remove_old_files(directory='GoogleResults'):
    """Removes all files in the specified directory if they exist."""
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
    else:
        os.makedirs(directory)
        print(f"Created directory: {directory}")

async def handle_click(page, selector, timeout=60000):
    """Tries to click a selector on the page."""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.click(selector)
    except Exception as e:
        print(f"Error occurred while interacting with selector '{selector}': {str(e)}")
        raise

async def take_screenshot(page, path):
    """Takes a screenshot and saves it to the given path."""
    try:
        await page.screenshot(path=path)
        print(f"Screenshot saved as '{path}'")
    except Exception as e:
        print(f"Error occurred while taking the screenshot: {str(e)}")

def image_to_base64(image_path):
    """Converts an image file to a base64-encoded string."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def base64_to_image(b64_image):
    # Decode the base64 image
    image_data = base64.b64decode(b64_image)

    # Create the full path to save the image
    image_path = os.path.join(os.getcwd(), 'uploaded_image.png')

    # Write the decoded image to a file
    with open(image_path, 'wb') as image_file:
        image_file.write(image_data)

    # Return the path to the saved image
    return image_path

# Example usage
# image_path = 'BGA _.JPG'
# b64_image = image_to_base64(image_path)

# # Run the search with the base64-encoded image
# asyncio.run(search_image_with_google_lens(b64_image))
