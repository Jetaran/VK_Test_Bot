import os
import urllib.request

from PIL import Image
from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard, PhotoMessageUploader
from vkbottle.bot import Bot, Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]  # Совместимо с секретами в Heroku или GitHub Actions

bot = Bot(token=BOT_TOKEN)
photo_uploader = PhotoMessageUploader(bot.api, generate_attachment_strings=True)

KEYBOARD = (
    Keyboard(one_time=False)
    .add(Callback("Пришли картинку", payload={"cmd": "callback"}))
    .get_json()
)

@bot.on.message(text=["Начать", "Привет бот"])
async def hi_handler(message: Message):
    """ Формирует приветствие """
    users_info = await bot.api.users.get(message.from_id)
    await message.answer(f"Привет, {users_info[0].first_name}", keyboard=KEYBOARD)

async def download_picture(url):
    """ Скачивает аватарку пользователя """
    filename = "ava.jpg"
    urllib.request.urlretrieve(url, filename=filename)
    return filename

async def handle_picture_return(filename):
    """ Обрабатывает аватарку пользователя """
    back_img = Image.new(mode="CMYK", size=(750, 500), color=(209, 123, 193, 100))
    user_avatar = Image.open(filename)
    back_img.paste(user_avatar, (350, 225))
    back_img.save("ava.jpg", quality=95)
    return back_img

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_message_event(event: GroupTypes.MessageEvent):
    """ Обрабатывает Message_event от клавиатуры """
    users_info = await bot.api.users.get(event.object.user_id)
    # Обрабатывает возможное отсутствие аватара, т.к. API может возвращать None
    try:
        avatar = await download_picture(users_info[0].photo_50)
    except:
        avatar = await download_picture("https://vk.com/images/camera_50.png")
    await handle_picture_return(avatar)
    collage = await photo_uploader.upload(avatar)
    await bot.api.messages.send(
        attachment=collage,
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        random_id=0)


if __name__ == "__main__":
    bot.run_forever()
