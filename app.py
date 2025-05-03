from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Ielasa API atslēgu no Railway vidē definētajiem mainīgajiem
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ja nav atslēgas, uzreiz pārtrauc darbu
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

openai.api_key = openai_api_key

# Veselības pārbaude (Railway saprot, ka serveris strādā)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DailySpark backend is running."})

# Galvenais ģenerēšanas maršruts
@app.route("/generate", methods=["POST"])
def generate():
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
        # Šeit rāda kļūdas, piemēram, ja API atslēga neder vai ir cits izņēmums
        return jsonify({"error": str(e)}), 500

# OBJEKTĪVI SVARĪGĀ RINDA:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
