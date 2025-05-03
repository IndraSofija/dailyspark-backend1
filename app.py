from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Ielādē OpenAI API atslēgu no vides mainīgā
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DailySpark backend is running."})

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()

        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in request body."}), 400

        prompt = data["prompt"]

        # Iegūst rezultātu no OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )

        generated_text = response.choices[0].text.strip()
        return jsonify({"result": generated_text})

    except openai.error.OpenAIError as e:
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
