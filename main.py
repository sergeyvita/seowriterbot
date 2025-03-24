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
        custom_input = data.get("custom_input", "").strip()

        # --- Prompt для ручного текста ---
        if custom_input:
            full_prompt = f"""
Ты — маркетинговый копирайтер. На основе следующего текста создай:

1. 🏡 *Полноценную статью* для публикации на сайте не менее 3900 символов. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, очередях, вариантах отделки, способах покупки, выгодах для покупателя. Текст должен быть привлекательным, вдохновляющим, структурированным, без эмодзи с выделением важных моментов в тексте жирным или курсивным шрифтом. В конце обязательно вставь ссылку на ЖК, если она есть в тексте, ссылка не должна повторяться и быть без каких либо скобок. Нельзя в описании писать фразы `Официальный сайт ЖК` или в подобном роде, а так же название застройщика Обязательно нужно дать людям понять в тексте статьи, что квартиры приобретают в компании Ассоциация застройщиков без комиссий и переплат, все самые актуальные цены, остатки и планировки по квартирам находятся по ссылке внизу статьи.

2. ✏️ *Заголовок элемента* — Краткое рассуждение по материалу статьи до 150 символов.

3. 📈 *META TITLE* — до 60 символов.

4. 🔑 *META KEYWORDS* — не менее 25 ключевых фраз через запятую.

5. 📝 *META DESCRIPTION* — ёмкое описание статьи (до 500 символов), не должно обрываться.

Исходный текст:
{custom_input}

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
        # --- Prompt для чанков ЖК ---
        else:
            prompt_text = "\n\n".join(chunks)
            full_prompt = f"""
Ты — маркетинговый копирайтер. На основе следующей информации о жилом комплексе создай:

1. 🏡 *Полноценную статью* для публикации на сайте не менее 3900 символов. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, очередях, вариантах отделки, способах покупки, выгодах для покупателя. Текст должен быть привлекательным, вдохновляющим, структурированным, без эмодзи с выделением важных моментов в тексте жирным или курсивным шрифтом. В конце обязательно вставь ссылку на ЖК, если она есть в тексте, ссылка не должна повторяться и быть без скобок. Нельзя в описании писать фразы `Официальный сайт ЖК` или в подобном роде. Обязательно нужно дать людям понять в тексте статьи, что квартиры приобретают без комиссий и переплат, все самые актуальные цены, остатки и планировки по квартирам находятся по ссылке внизу статьи.

2. ✏️ *Заголовок элемента* — до 100 символов.

3. 📈 *META TITLE* — до 60 символов.

4. 🔑 *META KEYWORDS* — не менее 25 ключевых фраз через запятую.

5. 📝 *META DESCRIPTION* — краткое, ёмкое описание (до 300 символов), которое не обрывается.

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
