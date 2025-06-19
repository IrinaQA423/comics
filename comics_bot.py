import os
import random
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from telegram import Bot, InputFile
from telegram.error import BadRequest

SLEEP_TIME = 14400


def get_max_comic_num():

    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def download_image(comic_number, save_dir=Path('images')):
    comics_url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(comics_url)
    response.raise_for_status()
    comics = response.json()

    image_url = comics['img']
    image_title = comics['title']
    alt_text = comics['alt']

    image_filename = f"{comic_number}_{image_title.replace(' ', '_')}.png"
    image_path = save_dir / image_filename

    image_response = requests.get(image_url)
    image_response.raise_for_status()

    with open(image_path, 'wb') as file:
        file.write(image_response.content)

    return image_path, alt_text


def publish_image_and_text(bot, tg_channel_id, image_path, alt_text):

    with open(image_path, 'rb') as photo_file:
        bot.send_photo(
            chat_id=tg_channel_id,
            photo=InputFile(photo_file),
            caption=alt_text
        )


def main():
    load_dotenv()  # Загружаем переменные окружения
    tg_token_comics_bot = os.getenv('TG_TOKEN_COMICS_BOT')
    tg_channel_id = os.getenv('TG_CHANNEL_ID')

    bot = Bot(token=tg_token_comics_bot)
    image_folder = Path('images')

    image_folder.mkdir(exist_ok=True)

    max_comic = get_max_comic_num()

    while True:
        image_path = None

        try:
            random_comic_num = random.randint(1, max_comic)

            image_path, alt_text = download_image(random_comic_num, image_folder)

            publish_image_and_text(bot, tg_channel_id, image_path, alt_text)
        except BadRequest as e:
            print(f"Ошибка публикации:{e}")
        finally:
            if image_path and image_path.exists():
                image_path.unlink()

        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
