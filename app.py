from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# OpenAI atslēga no Railway vides mainīgā
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DailySpark backend is running."})

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({
            "response": response['choices'][0]['message']['content']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
