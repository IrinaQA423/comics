import os
import random
import time

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


def download_image(comic_number, save_dir='images'):
    comics_url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(comics_url)
    response.raise_for_status()
    comics = response.json()

    image_url = comics['img']
    image_title = comics['title']
    alt_text = comics['alt']

    image_filename = f"{comic_number}_{image_title.replace(' ', '_')}.png"
    alt_filename = f"{comic_number}_{image_title.replace(' ', '_')}.txt"

    os.makedirs(save_dir, exist_ok=True)

    image_response = requests.get(image_url)
    image_response.raise_for_status()

    image_path = os.path.join(save_dir, image_filename)
    with open(image_path, 'wb') as file:
        file.write(image_response.content)

    alt_path = os.path.join(save_dir, alt_filename)
    with open(alt_path, 'w', encoding='utf-8') as alt_file:
        alt_file.write(alt_text)
    return image_path, alt_path


def load_config():
    load_dotenv()
    tg_token_comics_bot = os.getenv('TG_TOKEN_COMICS_BOT')
    tg_channel_id = os.getenv('TG_CHANNEL_ID')
    return tg_token_comics_bot, tg_channel_id


def publish_image_and_text(bot, tg_channel_id, image_path, alt_path):

    with open(image_path, 'rb') as photo_file:
        with open(alt_path, 'r', encoding='utf-8') as text_file:
            text_content = text_file.read()
            bot.send_photo(
                chat_id=tg_channel_id,
                photo=InputFile(photo_file),
                caption=text_content
            )


def main():
    tg_token_comics_bot, tg_channel_id = load_config()
    bot = Bot(token=tg_token_comics_bot)
    image_folder = "./images"

    max_comic = get_max_comic_num()

    while True:
        image_path = None
        alt_path = None
        try:
            random_comic_num = random.randint(1, max_comic)

            image_path, alt_path = download_image(random_comic_num, image_folder)
            publish_image_and_text(bot, tg_channel_id, image_path, alt_path)
        except BadRequest as e:
            print(f"Ошибка публикации:{e}")
        finally:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            if alt_path and os.path.exists(alt_path):
                os.remove(alt_path)
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
