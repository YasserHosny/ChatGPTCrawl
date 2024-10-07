import googlehandle.google_search as google_search
from openai import OpenAI
import os
import base64
import asyncio
import sys
import os

class ComponentDetection:
    def image_b64(image_path):
        """Convert the image at the given path to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def detect_component_info(image_file, logos_image_file):
        if image_file:
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode("utf-8")
        else:
            print("No component image was uploaded.")
            return None

        if logos_image_file:
            logos_image_data = logos_image_file.read()
            b64_logos_image = base64.b64encode(logos_image_data).decode("utf-8")
        else:
            print("No manufacturers' logos image was uploaded.")
            return None

        model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Step 1: Analyze the component image
        image_urls = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
        ]

        instructions = """Analyze the component image with the following instructions:
        1. Detect all symbols that seem to be logos, text in rows, and any identifying marks in the image. NOTE: Ignore the watermarks (CONVERGE) and (AN ARROW COMPANY).
        2. Symbols and text may contain Part Number, Part family or series, marking code, Manufacture name or logo.
        3. Identify supplier package type and accurately count the number of pins.
        4. Provide a detailed description of each logo, text, and any other identifiable feature on the component."""

        analysis_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": image_urls + [{"type": "text", "text": instructions}]
                }
            ]
        )

        image_analysis = analysis_response.choices[0].message.content

        # Step 2: Match logos and text against "Manufacturers' Logos"
        matching_instructions = f"""Based on the analysis provided:
        |
        {image_analysis}
        |
        Find the match for the logos and text extracted from the image against the attached image named 'Manufacturers' Logos'. 
        This image contains logos of various manufacturers. Identify the manufacturer(s) of the component in the provided image."""

        logos_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_logos_image}"}},
                        {"type": "text", "text": matching_instructions}
                    ]
                }
            ]
        )

        logos_match = logos_response.choices[0].message.content

        # Return the full analysis and matching information
        return image_analysis + "\n\n\nLogos Match:\n" + logos_match    

    def image_b64(image_path):
        """Convert the image at the given path to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    @staticmethod
    def detect_component_info2(image_file, logos_image_file):
        if image_file:
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode("utf-8")
        else:
            print("No component image was uploaded.")
            return None

        if logos_image_file:
            logos_image_data = logos_image_file.read()
            b64_logos_image = base64.b64encode(logos_image_data).decode("utf-8")
        else:
            print("No manufacturers' logos image was uploaded.")
            return None

        model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Step 1: Analyze the component image
        image_urls = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
        ]

        instructions = """Analyze the component image with the following instructions:
        1. Detect all symbols that seem to be logos, text in rows, and any identifying marks in the image. NOTE: Ignore the watermarks (CONVERGE) and (AN ARROW COMPANY).
        2. Symbols and text may contain Part Number, Part family or series, marking code, Manufacture name or logo.
        3. Identify supplier package type and accurately count the number of pins.
        4. Provide a detailed description of each logo, text, and any other identifiable feature on the component."""

        analysis_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": image_urls + [{"type": "text", "text": instructions}]
                }
            ]
        )

        image_analysis = analysis_response.choices[0].message.content

        # Step 2: Match logos and text against "Manufacturers' Logos"
        matching_instructions = f"""Based on the analysis provided:
        |
        {image_analysis}
        |
        Find the match for the logos and text extracted from the image against the attached image named 'Manufacturers' Logos'. 
        This image contains logos of various manufacturers. Identify all possible manufacturer(s) of the component in the provided image.
        Result format is:
        Possible manufacturers: []"""

        logos_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_logos_image}"}},
                        {"type": "text", "text": matching_instructions}
                    ]
                }
            ]
        )

        logos_match = logos_response.choices[0].message.content

        # Extract possible manufacturers and text for Google search
        possible_manufacturers = [line.strip() for line in logos_match.split("Possible manufacturers:")[1].strip('[]').split(',')]
        search_queries = [f"{manufacturer} {image_analysis}" for manufacturer in possible_manufacturers]

        # Step 3: Search Google for extracted data and capture screenshots
        for query in search_queries:
            asyncio.run(google_search.search_google_and_capture_screenshots(query))

        # Step 4: Analyze Google search results to determine the best match
        google_result_images = []
        for i in range(1, 4):
            screenshot_path = os.path.join('GoogleSearchResults', f'result_{i}.png')
            if os.path.exists(screenshot_path):
                google_result_images.append(ComponentDetection.image_b64(screenshot_path))

        google_analysis_instructions = f"""Analyze the Google search results screenshots provided and determine the most accurate match for the manufacturer and part number based on the information extracted from the component image.
        Result format:
        Manufacturer: <manufacturer_name>
        Part Number: <part_number>"""

        google_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                        {"type": "text", "text": image_analysis}
                    ] + [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in google_result_images] +
                    [{"type": "text", "text": google_analysis_instructions}]
                }
            ]
        )

        google_analysis = google_response.choices[0].message.content

        # Return the full analysis, logos match, and Google search analysis
        return f"{image_analysis}\n\n\nLogos Match:\n{logos_match}\n\n\nGoogle Search Analysis:\n{google_analysis}"


    # Example usage
    image_path = "BGA _.JPG"
    logos_image_path = 'Manufacturers Logos.png'

    with open(image_path, "rb") as image_file:
        with open(logos_image_path, "rb") as logos_image_file:
            print('Component Info:\n', detect_component_info2(image_file, logos_image_file))