from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re

app = Flask(__name__)

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
                      
        # === Получаем чанки напрямую из запроса ===
        chunks = data.get("chunks", [])

        # === Логируем чанки ===
        print("=== SEO BOT | ПОЛУЧЕНЫ ЧАНКИ ===")
        print(f"Количество чанков: {len(chunks)}")
        for i, chunk in enumerate(chunks, start=1):
            print(f"--- Чанк {i} ---")
            print(chunk)
            print("---------------")
        print("=== КОНЕЦ ЛОГА ЧАНКОВ ===")

        # Удаляем строки с изображениями из чанков
        cleaned_chunks = []
        for chunk in chunks:
            cleaned = re.sub(r'^https?://\S+\.(?:jpg|jpeg|png|gif)\s*$', '', chunk, flags=re.MULTILINE)
            cleaned_chunks.append(cleaned.strip())

        # Краткий system prompt
        messages = [
            {"role": "system", "content": "Ты — профессиональный копирайтер, создающий статьи о жилых комплексах для публикации на сайте и в Яндекс.Дзене."},
            {"role": "user", "content": "Сейчас я передам тебе данные о жилом комплексе. Не отвечай, пока не получишь все чанки."}
        ]

        for i, chunk in enumerate(cleaned_chunks):
            messages.append({"role": "user", "content": chunk})

        # Добавляем промт с правилами в последнем сообщении
        full_prompt = """
На основе этих данных сгенерируй статью строго по правилам:

=== ПРАВИЛА ===
Ответ верни строго в формате:

===ELEMENT_NAME===
{заголовок элемента}

===META_TITLE===
{мета тайтл}

===META_KEYWORDS===
{ключевые слова}

===META_DESCRIPTION===
{мета описание}

===ARTICLE===
{полный текст статьи}

Дополнительно:
1. Пиши на основе данных, не выдумывая.
2. Используй тёплый и живой стиль.
3. Применяй подзаголовки h2/h3, абзацы, списки, выделения.
4. Не используй emoji и рекламные фразы.
5. В конце вставь ссылку на страницу ЖК и контакты: 8-800-550-23-93, https://t.me/associationdevelopers
        """
        messages.append({"role": "user", "content": full_prompt})

        print("=== SEO BOT | ОТПРАВКА В OPENAI ===")
        for i, msg in enumerate(messages, start=1):
            print(f"--- Сообщение {i} | роль: {msg['role']} ---")
            print(msg['content'])
            print("---------------")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()

        def extract_block(tag):
            match = re.search(rf"==={tag}===\s*(.+?)(?=(?:===|$))", content, re.DOTALL)
            return match.group(1).strip() if match else ""

        result = {
            "element_name": extract_block("ELEMENT_NAME"),
            "meta_title": extract_block("META_TITLE"),
            "meta_keywords": extract_block("META_KEYWORDS"),
            "meta_description": extract_block("META_DESCRIPTION"),
            "article": extract_block("ARTICLE")
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
