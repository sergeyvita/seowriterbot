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

1. 🏡 *Полноценную статью* для публикации на сайте. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, очередях, вариантах отделки, способах покупки, выгодах для покупателя. Текст должен быть привлекательным, вдохновляющим, структурированным, без эмодзи с выделением важных моментов в тексте жирным или курсивным шрифтом. В конце обязательно вставь ссылку на ЖК, если она есть в тексте, ссылка не должна повторяться и быть без скобок. Нельзя в описании писать фразы `Официальный сайт ЖК` или в подобном роде. Обязательно нужно дать людям понять в тексте статьи, что квартиры приобретают без комиссий и переплат, все самые актуальные цены, остатки и планировки по квартирам находятся по ссылке внизу статьи

2. ✏️ *Заголовок элемента* — не более 100 символов, цепляющий.

3. 📈 *META TITLE* — до 60 символов.

4. 🔑 *META KEYWORDS* — не менее 25 ключевых слов и фраз, через запятую, по высокочастотным запросам конкретного ЖК.

5. 📝 *META DESCRIPTION* — краткое, но ёмкое описание статьи по высокочастотным запросам (до 900 символов), которое будет отображаться в результатах поиска. Не должно обрываться или быть неинформативным.Обязательно в описании должной быть понимание в каком гроде находится ЖК о котором написана статья. Нельзя писать - официальная страница ЖК или подобное. Обязательна должна быть фраза с отсылкой на сайт Ассоциации застройщиков.

Исходные данные:
{prompt_text}

Ответ верни строго в следующем формате (на русском языке):

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
