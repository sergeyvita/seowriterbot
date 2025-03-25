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

        has_jk_info = any(data.get(k) for k in ["id", "name", "code"])

        if not has_jk_info and custom_input:
            # Режим: Ручной ввод произвольной статьи
            full_prompt = f"""
Ты — профессиональный маркетинговый копирайтер. 

1.На основе предоставленного текста создай качественную, увлекательную переработанную статью. 

Создай **читабельный, цепляющий текст**, структурированный и полезный. Статья должна быть **информационной, живой и убедительно-позитивной**, с эмоционально вовлекающим вступлением, аргументами, примерами и возможными фактами (если они логично дополняют). Отредактируй текст, сохранив суть, усилив аргументацию и добавив стиль. 

Включи в статью **высокочастотные ключевые слова**, связанные с со смыслом стать, **не нарушая естественности повествования**.

Требования:

- **Объём** — не менее 3900 символов.
- Без эмодзи.
- Все **важные мысли выделяй жирным или курсивом** (используя markdown: `**жирный**`, `*курсив*`).
- Статья должна **начинаться с яркого и вовлекающего вступления**.
- Обязательно в конце каждой статьи **размести ссылку на сайт Ассоциации Застройщиков**: https://ap-r.ru  
  (не использовать скобки или текст вроде "официальный сайт", "перейти по ссылке" и т.д. Можно вставлять текст "Официальный сайт" только с названием компании Ассоциация застройщиков, пример: "Официальный сайт Ассоциации застройщиков" и т.п.).

🔴 Важно:
- Не используй markdown-ссылки [текст](ссылка) — только прямые ссылки в виде URL.
- Если ссылок нет — не добавляй выдуманных.

2. ✏️ *Заголовок элемента* — Краткое описание смысла статьи до 200 символов.

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
        else:
            # Режим: Генерация по данным ЖК (чанки)
            prompt_text = "\n\n".join(chunks)
            full_prompt = f"""
Ты — маркетинговый копирайтер. На основе следующей информации о жилом комплексе создай:

1. 🏡 *Полноценную статью* для публикации на сайте не менее 3900 символов. Используй живой, интересный стиль. Добавь подробности об инфраструктуре, строительстве, сроках сдачи, вариантах отделки, способах покупки, преимуществах. Пиши вдохновляюще, структурированно, но без эмодзи. Важные моменты — выделяй жирным или курсивом. В конце вставь ссылку на жилой комплекс, если она указана. Никаких скобок. Не используй фразы `Официальный сайт ЖК`, не указывай застройщика. В статье должно быть ясно, что **приобретение через Ассоциацию застройщиков — это без комиссий и переплат**, с **актуальными ценами и планировками по ссылке внизу статьи**.

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

