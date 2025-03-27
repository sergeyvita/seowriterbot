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
Ты — профессиональный копирайтер, создающий статьи о жилых комплексах для публикации на сайте и в Яндекс.Дзене. Напиши статью о жилом комплексе на основе переданных данных.
1. Цель статьи: рассказать потенциальным покупателям о жилом комплексе, заинтересовать, вызвать доверие, передать эмоции от будущей жизни в этом ЖК и мягко подтолкнуть к действию (перейти на сайт или связаться с отделом продаж).
2. Тон: тёплый, профессиональный, дружелюбный.
3. Стиль: разговорный, простой, легко читается на любом устройстве.
4. Обращение: от второго лица (ты, вы), с вовлечением читателя, без официоза.
5. Длина: до 4000 с расширенным описанием ЖК
6. Статья должна быть написана вручную — без шаблонности и клише.

7.  Структура статьи:
- Заголовок: цепляющий, конкретный, с названием ЖК.
- Вступление: образная подача, погружение в атмосферу (например: «Представьте, как…»).
- Преимущества расположения: центр, инфраструктура, транспорт, улицы поблизости.
- Архитектура и дизайн: фасады, остекление, балконы, внешний стиль.
- Инфраструктура и удобства: школы, детсады, коворкинги, паркинг, охрана, видеонаблюдение, зоны отдыха, двор-парк.
- Планировки: количество, уникальные решения, мастер-спальни, пентхаусы.
- Технологии и безопасность: видеонаблюдение, FACE ID, охрана, лифты, кладовые.
- Отделка и ремонт: предчистовая, варианты отделки от застройщика.
- Надёжность: упоминание 214-ФЗ, эскроу-счета.
- Призыв к действию: мягкий и дружелюбный (ссылка, телефон, онлайн-чат).

8. Дополнительные требования:
- Не указывать стоимость квартир.
- Не писать о скидках, акциях, ипотеке и маткапитале.
- Упомянуть улицу, район, количество этажей, квартир, парковочных мест, садиков и пр. в живой форме.
- Подчёркивай эмоции: комфорт, спокойствие, удобство, безопасность, гордость за жильё.
- Используй образные фразы: «здесь начинается день с улыбки», «ваши дети растут в безопасности», «дом, который говорит за вас» и т.п.
- Не использовать штампы: «квартиры на любой вкус», «отличная транспортная доступность», «развитая инфраструктура».
- Не использовать emoji.
- Вставить ссылку на страницу комплекса без каких-либо скобок, например: https://ap-r.ru/zhilye-kompleksy/kvartiry-v-novostroykakh/zhk-vse-svoi-vip/, где zhk-vse-svoi-vip это переменная и у каждого жк своя переменная.

9. В конце вставить контакты Ассоциации застройщиков:
📞 8-800-550-23-93
🌐 сайт: ap-r.ru


*Заголовок элемента* — до 100 символов.

*META TITLE* — до 60 символов.

*META KEYWORDS* — не менее 25 ключевых фраз через запятую.

*META DESCRIPTION* — краткое, ёмкое описание статьи (до 300 символов), не должно обрываться.

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
