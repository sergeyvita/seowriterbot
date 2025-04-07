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

        # Формируем список сообщений
        messages = [
            {"role": "system", "content": "Ты — профессиональный копирайтер, создающий статьи о жилых комплексах для публикации на сайте и в Яндекс.Дзене."},
            {"role": "user", "content": "Сейчас я передам тебе данные о жилом комплексе. Не отвечай, пока не получишь все чанки."}
        ]    

        for chunk in cleaned_chunks:
            messages.append({"role": "user", "content": chunk})

        final_prompt = """
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
"""
        instructions = """  
Ты — профессиональный копирайтер, создающий статьи о жилых комплексах для публикации на сайте и в Яндекс.Дзене. Напиши статью о жилом комплексе только на основе переданных данных, не предумывай и не фантазируй. Пиши статью **исключительно на основе переданных данных**. Если чего-то нет в данных — **не упоминай это вообще**. Не придумывай названия, технологии или факты. Любая информация должна быть подтверждена в тексте входных данных.
1. Цель статьи: рассказать потенциальным покупателям о жилом комплексе, заинтересовать, вызвать доверие, передать эмоции от будущей жизни в этом ЖК и мягко подтолкнуть к действию (перейти на сайт или связаться с отделом продаж).
2. Тон: тёплый, профессиональный, дружелюбный.
3. Стиль: разговорный, простой, легко читается на любом устройстве.
4. Обращение: от второго лица (ты, вы), с вовлечением читателя, без официоза.
5. Длина: не менее 4000 символов, старайся приблизиться к 8000 символам. Не сокращай текст. Раскрывай каждый раздел полностью — минимум по 3 абзаца, если есть данные.
6. Избегай клише и общих фраз. Пиши детально, с атмосферой. Представь, что ты пишешь статью для журнала — не торопись.
7. Не бойся писать развёрнуто — статья должна быть насыщенной и подробной, чтобы читатель почувствовал атмосферу места.
8. Расписывай каждый раздел подробно — минимум по 2-3 абзаца. Чем больше деталей — тем лучше. Не сокращай текст.


9.  Структура статьи:
- Заголовок: цепляющий, конкретный, с названием ЖК.
- Вступление: образная подача, погружение в атмосферу (например: «Представьте, как…»).
- Преимущества расположения: центр, инфраструктура, транспорт, улицы поблизости.
- Архитектура и дизайн: фасады, остекление, балконы, внешний стиль.
- Инфраструктура и удобства: школы, детсады, коворкинги, паркинг, охрана, видеонаблюдение, зоны отдыха, двор-парк.
- Планировки: количество, уникальные решения, мастер-спальни, пентхаусы.
- Технологии и безопасность: опиши только то, что упоминается во входных данных. Никаких домыслов или добавления информации от себя.
- Отделка и ремонт: предчистовая, варианты отделки от застройщика.
- Надёжность: упоминание 214-ФЗ, эскроу-счета.
- Призыв к действию мягкий и дружелюбный (ссылка, телефон, онлайн-чат).

10. Дополнительные требования:
- Используй заголовки h2  и h3: h2 - для ключевых разделов, р3 - для подпунктов внутри разделов.
- Делай абзацы с четким разделением текста по смыслу
- Используй списки, для преимуществ, пунктов и шагов.
- Выделяй жирным - важные мысли, курсивом- акценты или уточнения.
- Не делай стаью сплошной "простыней", используй блоки и воздух. 
- Если в данных указан район, используй информацию о нём для раскрытия преимуществ ЖК: упоминай улицы, атмосферу района, его характер, плюсы и минусы, инфраструктуру и близость ключевых объектов. Вплетай это в контекст статьи — как часть жизни в жилом комплексе, а не как отдельный блок.
- Статьи должны быть визуально "сканируемыми" - лнгко просматриваемые глазами.
- Не указывать стоимость квартир.
- Не писать о скидках, акциях, ипотеке и маткапитале.
- Упомянуть улицу, район, количество этажей, квартир, парковочных мест, садиков и пр. в живой форме.
- Подчёркивай эмоции: комфорт, спокойствие, удобство, безопасность, гордость за жильё.
- Используй образные фразы: «здесь начинается день с улыбки», «ваши дети растут в безопасности», «дом, который говорит за вас» и т.п.
- Не использовать штампы: «квартиры на любой вкус», «отличная транспортная доступность», «развитая инфраструктура».
- Не использовать emoji.
- Убрать вопросительные знаки, которы не относятся к статье, а являются ошибкой передачи данных или остатком програмного кода.
- Вставить ссылку на страницу комплекса без каких-либо скобок, например: https://ap-r.ru/zhilye-kompleksy/kvartiry-v-novostroykakh/zhk-vse-svoi-vip/, где zhk-vse-svoi-vip это переменная и у каждого жк своя переменная.

11. В конце вставить контакты Ассоциации застройщиков:
8-800-550-23-93
Необходимо вставить ссылку на телеграм канал, в зависимости от города. Статья имеет привязку по городу, если в статье тот или иной город, то сопоставляй с сылкой, которые указаны нижеи в ставляй в самый низ статьи.
Ссылки для сопоставления и вставки в статью:
Ссылка на телеграм канал Краснодар - https://t.me/associationdevelopers
Ссылка на телеграм канал Новороссийск, Анапа, Сочи, Архыз, Туапсе, Темрюк, Тамань - https://t.me/associationdevelopers
Ссылка на телеграм канал не должна в конце иметь точки или других символов, пример правильной ссылки "https://t.me/associationdevelopers"

*Заголовок элемента* — до 120 символов.

*META TITLE* — до 120 символов.

*META KEYWORDS* — не менее 25 ключевых фраз через запятую.

*META DESCRIPTION* — ёмкое описание статьи до 300 символов, не должно обрываться.
"""

        messages.append({"role": "user", "content": "Готово. На основе этих данных сгенерируй статью строго по правилам:"})
        messages.append({"role": "user", "content": instructions})
        messages.append({"role": "user", "content": final_prompt})

        print("=== SEO BOT | ОТПРАВКА В OPENAI ===")
        for i, msg in enumerate(messages, start=1):
            print(f"--- Сообщение {i} | роль: {msg['role']} ---")
            print(msg['content'][:3000])  # Ограничим вывод до 3000 символов, чтобы не захламить лог
            print("---------------")
        print("=== КОНЕЦ ОТПРАВКИ В OPENAI ===")    
        
        
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
