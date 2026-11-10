
import asyncio
from pathlib import Path
import edge_tts

VOICE = "ru-RU-DmitryNeural"
TEXT_FILE = "script.txt"
OUTPUT_FILE = "radio_novosti.mp3"

async def main():
    text = Path(TEXT_FILE).read_text(
        encoding="utf-8"
    ).strip()

    if not text:
        raise RuntimeError("Текст новостей пуст")

    audio = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="-5%"
    )

    await audio.save(OUTPUT_FILE)
    print("MP3 создан:", OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(main())
