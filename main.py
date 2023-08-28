import telebot
import logging
from config import TOKEN, ADMIN_IDS
from GameMaster import GameMaster
from SheetEditor import Editor
import time
import schedule
import threading

# TODO Editor update
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    if gm.add_user(message.chat.id, '@' + message.from_user.username if message.from_user.username is not None else None, message.from_user.id):
        print('new user:', message.from_user.username, message.from_user.id)
    handle_message(message)


@bot.message_handler(commands=['update'])
def update(message):
    if message.from_user.id in ADMIN_IDS:
        ed.update_data()


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_photo(83530498, message.photo[0].file_id, caption=f'от {"@" + message.from_user.username if message.from_user.username is not None else message.from_user.id}')
    message.text = 'pic'
    handle_message(message)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    logging.info(f'rec id:{message.chat.id} [{gm.get_user_data(message.chat.id)}] input:{message.text}')
    output, next = gm.reply(message.chat.id, message.text)
    if output:
        reply(message.chat.id, output, next)


def reply(chat_id, output, next_stage=True):
    def send(msg, markup=None):
        if msg.photo is not None:
            with open(msg.photo, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption=msg.text, reply_markup=markup)
        elif msg.audio is not None:
            with open(msg.audio, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption=msg.text, reply_markup=markup)
        else:
            bot.send_message(chat_id, msg.text, reply_markup=markup, disable_web_page_preview=msg.preview)

    if output.buttons:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, is_persistent=True, one_time_keyboard=True)
        buttons = []
        for btn in output.buttons:
            buttons.append(telebot.types.KeyboardButton(btn))
        markup.add(*buttons)
    else:
        markup = None

    logging.info(f'srt id:{chat_id} [{gm.get_user_data(chat_id)}], output:{output.messages[0].text[:10]}...')
    for msg in output.messages[:-1]:
        send(msg)
        # TODO un/comment
        time.sleep(msg.delay)
    send(output.messages[-1], markup)
    if next_stage:
        gm.end_reply(chat_id, output.ping_stage)
    logging.info(f'ert id:{chat_id} [{gm.get_user_data(chat_id)}]')


def pinging():
    pings = gm.ping_inactive()
    for i in pings:
        try:
            reply(*i, next_stage=False)
        except Exception as e:
            print(e)
            print('got blocked by', i[0])


def schedule_thread():
    while True:
        try:
            schedule.run_pending()
            time.sleep(5)
        except Exception as e:
            print(e)


def polling_thread():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            print('RESUMING polling')


if __name__ == "__main__":
    print('Preparing the editor')
    ed = Editor('user data')
    ed.default()
    print('Preparing the game master')
    gm = GameMaster(ed)
    print('Configuring logging')
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S %d.%m',
        encoding='UTF-8')
    print('Preparing ping thread')
    schedule.every(5).seconds.do(pinging)
    schedule.every(29).minutes.do(ed.update_data)
    schedule_thread = threading.Thread(target=schedule_thread)
    schedule_thread.start()
    print('Starting the bot')
    polling_thread = threading.Thread(target=polling_thread)
    polling_thread.start()
    print('Ready')
