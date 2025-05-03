from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# 🔍 Diagnostikas rindiņa
print("🔐 OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

# Atslēgas ielāde un aizsardzība
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ ERROR: OPENAI_API_KEY is missing.")
    openai_api_key = None  # ļaus sistēmai turpināt, bet atteiks pieprasījumu

openai.api_key = openai_api_key

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ DailySpark backend is running."})

@app.route("/generate", methods=["POST"])
def generate():
    if not openai.api_key:
        return jsonify({"error": "API key is missing"}), 403

    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        print("🔥 Error during generation:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
