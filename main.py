from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Получаем ключ из переменных окружения Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    chunks = data.get("chunks", [])

    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500

    if not chunks:
        return jsonify({"error": "No chunks provided"}), 400

    messages = [
        {
            "role": "system",
            "content": "Ты опытный копирайтер. Получи данные о жилом комплексе по частям. Не пиши статью, пока не получишь команду."
        }
    ]

    for index, chunk in enumerate(chunks):
        messages.append({
            "role": "user",
            "content": f"Часть данных №{index + 1}:\n{chunk}"
        })
        messages.append({
            "role": "assistant",
            "content": f"Принял часть №{index + 1}"
        })

    messages.append({
        "role": "user",
        "content": "Теперь напиши статью на основе всей информации. Сделай её структурированной, понятной, с подзаголовками и абзацами. Пиши от лица эксперта. Добавь заголовок."
    })

    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        result = response["choices"][0]["message"]["content"]
        return jsonify({"article": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/healthz", methods=["GET"])
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
