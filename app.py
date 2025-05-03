from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Ielādē .env mainīgos, ja darbojas lokāli
load_dotenv()

app = Flask(__name__)

# Iegūst OpenAI API atslēgu no vides mainīgā
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DailySpark backend is running."})

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        generated_text = response.choices[0].message["content"].strip()
        return jsonify({"response": generated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
