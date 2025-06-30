from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

TOGETHER_API_KEY = os.getenv("db63dc346c17b87ff29c21afea76c0081f95ce861df92a4f2257912bb8c3f4ab")  # Set this in your Render env vars

def decode_with_together(text):
    prompt = f"""
You are a career coach and resume expert.

Given the job description below, do the following:

1. Extract the top 10 most important resume keywords (skills, responsibilities, tools, or phrases).
2. Write a plain-English summary explaining what this job really expects from a candidate.

Output format:
KEYWORDS:
<comma separated keywords>

SUMMARY:
<clear explanation>

Job Description:
{text}
"""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", json=body, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Failed to generate response: {str(e)}"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/decode', methods=['POST'])
def decode():
    jd = request.form.get('job_description', '')
    if not jd.strip():
        return jsonify({"error": "No job description provided"}), 400

    decoded_output = decode_with_together(jd)

    try:
        keyword_part = decoded_output.split("SUMMARY:")[0].replace("KEYWORDS:", "").strip()
        summary_part = decoded_output.split("SUMMARY:")[1].strip()
        keywords = [k.strip() for k in keyword_part.split(",") if k.strip()]
    except Exception:
        keywords = []
        summary_part = decoded_output

    return jsonify({
        "keywords": keywords,
        "decoded": summary_part.split("\n")
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
