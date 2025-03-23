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
        chunks = data.get("chunks", [])
        prompt_text = "\n\n".join(chunks)

        full_prompt = f"""
Ты — маркетинговый копирайтер. На основе следующей информации о жилом комплексе создай:

1. 🏡 *Полноценную статью* для публикации на сайте. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, очередях, вариантах отделки, способах покупки, выгодах для покупателя. Текст должен быть привлекательным, вдохновляющим и структурированным. В конце обязательно вставь ссылку на ЖК, если она есть в тексте.

2. ✏️ *Заголовок элемента* — не более 100 символов, цепляющий.

3. 📈 *META TITLE* — до 60 символов.

4. 🔑 *META KEYWORDS* — 5–10 ключевых фраз, через запятую.

Исходные данные:
{prompt_text}

Ответ верни строго в следующем формате (на русском языке):

===ELEMENT_NAME===
{{заголовок элемента}}

===META_TITLE===
{{мета тайтл}}

===META_KEYWORDS===
{{ключевые слова}}

===ARTICLE===
{{полный текст статьи}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
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
            "article": extract_block("ARTICLE")
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
