# file: app.py

from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

# Use Ollama to handle both keywords + plain explanation

def decode_with_ollama(text, model='mistral'):
    prompt = f"""
You are a career coach and resume expert.

Given the job description below, do the following:

1. Extract the top 10 most important resume keywords (skills, responsibilities, tools, or phrases).
2. Write what this job role really expects from a candidate.

Output format:
KEYWORDS:
<comma separated keywords>

SUMMARY:
<clear explanation>

Job Description:
{text}
"""

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
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

    decoded_output = decode_with_ollama(jd)

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
