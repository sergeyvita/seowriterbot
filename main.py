from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Получаем ключ API из переменной окружения
api_key = os.environ.get("OPENAI_API_KEY")

# Инициализируем клиента OpenAI
client = OpenAI(api_key=api_key)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        chunks = data.get("chunks", [])
        prompt = "\n\n".join(chunks)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        article = response.choices[0].message.content.strip()
        return jsonify({"article": article})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
