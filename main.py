"""
Telegram bot on PyTelegramBotAPI made to protect groups from spam of specified stickers (sticker-packs).
"""

import telebot
from secret import TOKEN
import sqlite3
import pathlib


# make sure database file exists
pathlib.Path('sticker_packs.db').touch()

bot = telebot.TeleBot(TOKEN)

# Sticker packs to be banned
banned_sticker_packs = []


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'Hello! I am a bot that can help you to protect your group from spam of stickers. \n' +
        'Just add me to your group and make me an admin. \n' +
        'Then I will delete stickers from the sticker-packs you will specify. \n' +
        'To add a sticker-pack to the ban list, send me command /add and a sticker from this pack. \n' +
        'To remove a sticker-pack from the ban list, send me command /remove and a sticker from this pack again. '
    )


def add_sticker_pack(chat_id, sticker_pack):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sticker_packs (chat_id, sticker_pack) VALUES (?, ?)', (chat_id, sticker_pack))
    conn.commit()
    conn.close()


def remove_sticker_pack(chat_id, sticker_pack):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sticker_packs WHERE chat_id = ? AND sticker_pack = ?', (chat_id, sticker_pack))
    conn.commit()
    conn.close()


def get_banned_sticker_packs(chat_id):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sticker_pack FROM sticker_packs WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchall()
    conn.close()
    return [x[0] for x in result]


@bot.message_handler(commands=['add'])
def add_sticker_pack_command(message):
    chat_id = message.chat.id
    sticker_pack = message.sticker.set_name
    if sticker_pack in get_banned_sticker_packs(chat_id):
        bot.send_message(chat_id, 'This sticker-pack is already in the ban list')
    else:
        add_sticker_pack(chat_id, sticker_pack)
        bot.send_message(chat_id, 'Sticker-pack added to the ban list')


@bot.message_handler(commands=['remove'])
def remove_sticker_pack_command(message):
    chat_id = message.chat.id
    sticker_pack = message.sticker.set_name
    if sticker_pack not in get_banned_sticker_packs(chat_id):
        bot.send_message(chat_id, 'This sticker-pack is not in the ban list')
    else:
        remove_sticker_pack(chat_id, sticker_pack)
        bot.send_message(chat_id, 'Sticker-pack removed from the ban list') 


@bot.message_handler(content_types=['sticker'])
def check_sticker(message):
    chat_id = message.chat.id
    sticker_pack = message.sticker.set_name
    if sticker_pack in get_banned_sticker_packs(chat_id):
        bot.delete_message(chat_id, message.message_id)


def create_table():
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS sticker_packs (id primary key autoincrement, chat_id integer, sticker_pack text)')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_table()
    bot.polling()
