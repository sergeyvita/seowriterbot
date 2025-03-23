import os
from flask import Flask, request, jsonify
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

app = Flask(__name__)

# Настройка клиента OpenAI с API-ключом из переменных окружения
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        chunks = data.get("chunks", [])

        # Собираем весь текст из чанков
        full_text = "\n\n".join(chunks)

        # Строим запрос к ChatGPT
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "Ты пишешь маркетинговую статью для сайта о жилом комплексе."},
            {"role": "user", "content": full_text}
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        article_text = response.choices[0].message.content
        return jsonify({"article": article_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
