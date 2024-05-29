from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json as jsn
from chatgptapi.test_chatgpt_api import ChatgptApiTest


app = Flask(__name__)
# CORS(app, resources={r"/qa": {"origins": "http://localhost:4200"}})
CORS(app)


@app.route('/api/testChatgptApi', methods=['POST'])
def testChatgptApi():
    user_input = request.form.get('user_input')
    image_file = request.files.get('image_file')
    print("user_input:" + user_input)
    chatgpt = ChatgptApiTest()
    bot_response = chatgpt.testChatgptApi(user_input, image_file)
    response = bot_response
    return response
    

if __name__ == '__main__':
    app.run(debug=True, port = 5001)