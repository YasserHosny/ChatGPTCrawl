from openai import OpenAI
import os
import base64
from googlehandle.simulate_playwright import search_image_with_google_lens
import asyncio


class ChatgptApiTest:
    def image_b64(self, image_path):
        """Convert the image at the given path to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def testChatgptApi(self, user_input, image_file):
        if image_file:
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode("utf-8")
        else:
            print("No file was uploaded.")
            return None

        # Run the async search_image_with_google_lens function synchronously
        asyncio.run(search_image_with_google_lens(b64_image))

        # Load screenshots from GoogleResults folder
        result_dir = 'GoogleResults'
        all_results_image = self.image_b64(os.path.join(result_dir, "all_results.png"))
        exact_matches_image = None

        if os.path.exists(os.path.join(result_dir, 'exact_matches_screenshot.png')):
            exact_matches_image = self.image_b64(os.path.join(result_dir, "exact_matches_screenshot.png"))

        single_result_images = []
        for i in range(1, 4):
            screenshot_path = os.path.join(result_dir, f"GoogleResults/single_result_screenshot_{i}.png")
            if os.path.exists(screenshot_path):
                single_result_images.append(self.image_b64(screenshot_path))

        model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        image_urls = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{all_results_image}"}}
        ]

        if exact_matches_image is not None:
            image_urls.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{exact_matches_image}"}})

        for img in single_result_images:
            image_urls.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

        instructions = """Analyze the first image with the following instructions:
        1. Detect all symbols that seem to be logos in the first image. NOTE: Ignore the watermarks (CONVERGE) and (AN ARROW COMPANY).
        2. Symbols and text may contain Part Number, Part family or series, marking code, Manufacture name or logo.
        3. Identify supplier package and pin count(count pins accurately).
        4. Use the information from the other images to assist in identifying the manufacturer and part number for the component in first image.
        5. List the logos one by one, including any details or similarities observed in the other images.
        6. Search the web to check if your suggested manufacturer has been acquired by another one, and provide it.
        7. Describe the first image in detail, incorporating any relevant findings from the web search."""

        image_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": image_urls + [{"type": "text", "text": instructions}]
                }
            ]
        )

        image_description = image_response.choices[0].message.content

        question_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text":
                            f"""Based on the component description between | separator: 
                            |
                            {image_description} 
                            |
                            Answer the following question in form of pairs (feature Name: Feature Value): {user_input}"""
                        },
                    ],
                }
            ],
        )
        answer = question_response.choices[0].message.content

        return image_description + "\n\n\n|||" + answer


    def identify_componentImage(self, user_input, image_file):
        if image_file:
            # Convert the image file to base64
            image_data = image_file.read()
            b64_image = base64.b64encode(image_data).decode("utf-8")
            
            # Save the image to a temporary path if needed
            temp_image_path = "temp_image.jpg"
            with open(temp_image_path, "wb") as temp_image_file:
                temp_image_file.write(image_data)
            
        else:
            print("No file was uploaded.")
            return None

        # Prepare the model API
        model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        image_urls = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
        ]

        # Provide instructions for analyzing the image
        instructions = """
        The image provided is a component wireframe with multiple perspectives of the same component. 
        Follow these instructions to analyze the component wireframe and extract key details:

        1. **Identify Perspectives:** Detect the different views of the component in the image (e.g., top, side, front views).
        2. **Dimensions Extraction:** 
        - Extract and label the **Length**, **Height**, and **Depth** from each perspective where they are displayed.
        - Pay special attention to cases where the **Length** varies based on the number of pins in the component. Each pin configuration may have different lengths—please mention all variations clearly.
        3. **Pin Count and Package:** 
        - Identify the **pin count** from the wireframe image, and determine whether it affects the overall length or other dimensions.
        - Identify any specific details about the component's **package type** (e.g., DIP, SOIC, QFP) and how it correlates with the dimensions.
        4. **Component Details:** 
        - Detect all symbols and text in the image that might indicate part numbers, family/series names, marking codes, manufacturer names, or logos.
        5. **Comprehensive Description:**
        - Provide a detailed description of the component based on the wireframe, including dimensions from different views and any other relevant characteristics.
        6. **Accuracy of Dimensions:** 
        - Ensure that extracted dimensions are accurate and labeled correctly, even if multiple sizes or configurations are shown.
        7. **Final Output:**
        - Summarize the dimensions and component features in a structured format (e.g., Length: X mm, Height: Y mm, Depth: Z mm, Pin Count: N).
        """

        # Call GPT-4o with the image URL and instructions
        image_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": image_urls + [{"type": "text", "text": instructions}]
                }
            ]
        )

        # Extract the description from the response
        image_description = image_response.choices[0].message.content

        # Use the image description to answer the user's specific question
        question_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text":
                            f"""Based on the component description between | separator: 
                            |
                            {image_description} 
                            |
                            Answer the following question in form of pairs (Feature Name: Feature Value): {user_input}"""
                        },
                    ],
                }
            ]
        )

        # Extract the answer from the response
        answer = question_response.choices[0].message.content

        # Return the full image description followed by the answer to the user's question
        return image_description + "\n\n\n|||\n" + answer
