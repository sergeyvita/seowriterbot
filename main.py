import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Получаем API-ключ из переменной окружения
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Инициализируем клиента OpenAI без аргумента 'proxies'
client = OpenAI(api_key=openai_api_key)

@app.route("/generate", methods=["POST"])
def generate_article():
    try:
        data = request.get_json()
        chunks = data.get("chunks", [])

        if not chunks:
            return jsonify({"error": "Нет данных для генерации"}), 400

        prompt = "\n".join(chunks)

        # Отправляем запрос в OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты пишешь SEO-оптимизированную статью о жилом комплексе для сайта в формате блога."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )

        article = response.choices[0].message.content
        return jsonify({"article": article})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
