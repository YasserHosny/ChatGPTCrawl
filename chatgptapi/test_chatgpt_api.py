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
        image_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            },
                        },
                        {"type": "text", "text": "Describe image in detail"},
                    ],
                }
            ],
        )
        image_description = image_response.choices[0].message.content
        print({"image_description": image_description})
        
        question_response = model.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 
                            """Upon component description between | seperator: 
                            |
                            {} 
                            |
                            Answer the following question: {}""".format(image_description, user_input)},
                    ],
                }
            ],
        )
        answer = question_response.choices[0].message.content
        print({"answer": answer})
        
        return answer
