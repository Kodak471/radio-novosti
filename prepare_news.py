
import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator

with open("news.json", encoding="utf-8") as f:
    data = json.load(f)

now = datetime.now(timezone.utc)
translator = GoogleTranslator(source="auto", target="ru")

selected = []
seen = []

for article in data["articles"]:
    try:
        published = parsedate_to_datetime(
            article["published"]
        ).astimezone(timezone.utc)
    except (ValueError, TypeError):
        continue

    if not now - timedelta(hours=24) <= published <= now:
        continue

    title = article["title"].strip()

    if any(
        SequenceMatcher(
            None, title.lower(), old.lower()
        ).ratio() > 0.85
        for old in seen
    ):
        continue

    try:
        translated = translator.translate(title)
    except Exception as error:
        print("Ошибка перевода:", error)
        continue

    if not translated:
        continue

    selected.append({
        "source": article["source"],
        "title_ru": translated,
        "url": article["url"],
        "published": article["published"]
    })
    seen.append(title)

    if len(selected) >= 10:
        break

if not selected:
    raise RuntimeError(
        "Нет свежих переведённых новостей"
    )

lines = [
    "Здравствуйте!",
    "В эфире новости Германии и Украины.",
    ""
]

for item in selected:
    lines.append(item["title_ru"] + ".")
    lines.append("")

lines.append("Это были последние новости.")
lines.append("Спасибо за внимание!")

with open("script.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

with open("selected_news.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

print("Подготовлено новостей:", len(selected))
print("Текст сохранён в script.txt")
