from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env file")

def call_ai(prompt: str) -> str:
    """Call OpenAI API and return the response content"""
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Raise error for bad status codes
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        raise Exception("Failed to connect to AI service. Please try again later.")
    except (KeyError, IndexError, TypeError) as e:
        print(f"API Response Error: {e}")
        raise Exception("Received invalid response from AI service.")

# ====================== ROUTES ======================

@app.route("/hint", methods=["POST"])
def hint():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    prompt = f"""
You are a helpful coding tutor.
Here is the student's code:

{code}

There is a mistake in this code.
Give ONLY a short, helpful hint. 
Do NOT give the solution or corrected code.
Keep your hint concise.
"""
    try:
        ai_response = call_ai(prompt)
        return jsonify({"hint": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fix", methods=["POST"])
def fix():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    prompt = f"""
Find the error(s) in the following code and fix it.
Explain what was wrong and provide the corrected code.

Code:
{code}
"""
    try:
        ai_response = call_ai(prompt)
        return jsonify({"fixed_code": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/explain", methods=["POST"])
def explain():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    prompt = f"""
Explain the following code clearly.
Also suggest improvements if any.

Code:
{code}
"""
    try:
        ai_response = call_ai(prompt)
        return jsonify({"explanation": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/example", methods=["POST"])
def example():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    prompt = f"""
Give a real-world example using this code snippet.
Include sample input and expected output.

Code:
{code}
"""
    try:
        ai_response = call_ai(prompt)
        return jsonify({"example": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)