from openai import OpenAI
import os
import base64


class ChatgptApiTest:
    def image_b64(self, image):
        with open(image, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def testChatgptApi(self, user_input, image_file):
        # Make sure an image file was actually uploaded
        if image_file:
            # Read the file's contents into bytes
            image_data = image_file.read()

            # Encode the bytes-like object using base64
            b64_image = base64.b64encode(image_data).decode("utf-8")
        else:
            # Handle the case where no file was uploaded
            b64_image = None
            print("No file was uploaded.")

        model = OpenAI(api_key=os.getenv("api_key"))
        print("client.api_key:" + model.api_key)
        response = model.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{b64_image}",
                        },
                        {"type": "text", "text": user_input},
                    ],
                }
            ],
        )
        print({"response": response.choices[0].message.content})
        return response.choices[0].message.content
