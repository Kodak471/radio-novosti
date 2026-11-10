
import json
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher
from deep_translator import MyMemoryTranslator

# Настройки
MAX_NEWS = 5
DELAY = 3

with open("news.json", encoding="utf-8") as f:
    data = json.load(f)

now = datetime.now(timezone.utc)
selected = []
seen = []

def detect_language(text):
    # Украинские буквы
    if any(c in text.lower() for c in "іїєґ"):
        return "uk"

    # Немецкие буквы
    if any(c in text.lower() for c in "äöüß"):
        return "de"

    # Остальные заголовки проверяются
    # с учётом источника отдельно
    return None

def translate_title(title, source):
    language = detect_language(title)

    if language is None:
        name = source.lower()

        if "tagesschau" in name:
            language = "de"
        elif "укринформ" in name or "ukrinform" in name:
            language = "uk"
        else:
            language = "en"

    if language == "ru":
        return title

    translator = MyMemoryTranslator(
        source=language,
        target="ru"
    )

    return translator.translate(title)

articles = []

for article in data.get("articles", []):
    try:
        published = parsedate_to_datetime(
            article["published"]
        ).astimezone(timezone.utc)
    except (ValueError, TypeError, KeyError):
        continue

    if not now - timedelta(hours=24) <= published <= now:
        continue

    title = article.get("title", "").strip()

    if not title:
        continue

    articles.append((published, article, title))

# Сначала самые свежие
articles.sort(key=lambda item: item[0], reverse=True)

for published, article, title in articles:
    if any(
        SequenceMatcher(
            None, title.lower(), old.lower()
        ).ratio() > 0.85
        for old in seen
    ):
        continue

    try:
        translated = translate_title(
            title,
            article.get("source", "")
        )
    except Exception as error:
        print("Ошибка перевода:", error)
        time.sleep(DELAY)
        continue

    if not translated:
        continue

    selected.append({
        "source": article.get("source", ""),
        "title_ru": translated,
        "url": article.get("url", ""),
        "published": article["published"]
    })

    seen.append(title)
    print("Переведено:", len(selected))
    time.sleep(DELAY)

    if len(selected) >= MAX_NEWS:
        break

if not selected:
    raise RuntimeError(
        "Не удалось перевести свежие новости. "
        "Проверьте доступность сервиса MyMemory."
    )

lines = [
    "Здравствуйте!",
    "В эфире новости Германии и Украины.",
    ""
]

for item in selected:
    lines.append(item["title_ru"].rstrip(".") + ".")
    lines.append("")

lines.append("Это были последние новости.")
lines.append("Спасибо за внимание!")

with open("script.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

with open("selected_news.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

print("Подготовлено новостей:", len(selected))
print("Текст сохранён в script.txt")
