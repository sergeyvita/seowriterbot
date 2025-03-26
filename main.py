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

1. 🏡 *Полноценную статью* для публикации на сайте не менее 3900 символов. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, сроках сдачи, вариантах отделки, способах покупки, преимуществах. Пиши вдохновляюще, структурированно, но без эмодзи. Важные моменты — выделяй жирным или курсивом. В конце статьи вставь ссылку на страницу жилого комплекса, ссылки начинаются с адреса ap-r.ru, если она указана, пример: "https://ap-r.ru/zhilye-kompleksy/kvartiry-v-novostroykakh/zhk-narodnye-kvartaly-krasnodar/", всегда в ссылке должно быть https://, если https:// нет до добавляй перед https://ap-r.ru, ни какие другие ссылки на посторонние сайты ты не вставлешь. Ссылка не должна быть в скобках или кавычках. Не используй фразы `Официальный сайт ЖК`, не указывай застройщика. В статье должно быть ясно, что **приобретение через Ассоциацию застройщиков — это без комиссий и переплат**, с **актуальными ценами и планировками по ссылке внизу статьи**.

2. ✏️ *Заголовок элемента* — до 100 символов.

3. 📈 *META TITLE* — до 60 символов.

4. 🔑 *META KEYWORDS* — не менее 25 ключевых фраз через запятую.

5. 📝 *META DESCRIPTION* — краткое, ёмкое описание (до 300 символов), не должно обрываться.

Исходные данные:
{prompt_text}

Ответ верни строго в формате:

===ELEMENT_NAME===
{{заголовок элемента}}

===META_TITLE===
{{мета тайтл}}

===META_KEYWORDS===
{{ключевые слова}}

===META_DESCRIPTION===
{{мета описание}}

===ARTICLE===
{{полный текст статьи}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=1
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
