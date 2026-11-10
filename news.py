
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json

SOURCES = {
    "Германия — Tagesschau":
        "https://www.tagesschau.de/xml/rss2",
    "Украина — Укринформ":
        "https://www.ukrinform.ua/rss/block-lastnews"
}

news = []

for source, url in SOURCES.items():
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            request, timeout=20
        ) as response:
            data = response.read()

        root = ET.fromstring(data)

        for item in root.findall(".//item")[:10]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            date = item.findtext("pubDate", "")

            if title and link:
                news.append({
                    "source": source,
                    "title": title,
                    "url": link,
                    "published": date
                })

        print(source, "— получено")

    except Exception as error:
        print(source, "— ошибка:", error)

result = {
    "updated": datetime.now(
        timezone.utc
    ).isoformat(),
    "articles": news
}

with open(
    "news.json", "w", encoding="utf-8"
) as file:
    json.dump(
        result, file,
        ensure_ascii=False,
        indent=2
    )

print("Всего новостей:", len(news))
