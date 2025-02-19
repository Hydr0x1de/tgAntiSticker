"""
Telegram bot on PyTelegramBotAPI made to protect groups from spam of specified stickers (sticker-packs).
"""

import telebot
import sqlite3
import pathlib

# if no secret.py file, create it with TOKEN environment variable
try:
    from secret import TOKEN
except ImportError:
    import os
    TOKEN = os.environ.get('TOKEN')

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
        'To remove a sticker-pack from the ban list, send me command /remove or /rem and a sticker from this pack again. \n' +  # noqa: E501
        'To see the list of banned sticker-packs, send me command /list. \n' +
        'To add a sticker-pack to the ban list on reply, use command /addreply or /addr. \n' +
        'To remove a sticker-pack from the ban list on reply, use command /removereply or /remr. \n' +
        'To close the context, use command /close. \n' +
        '\n**Commands can be used only by the group owner.**'
    )


def add_sticker_pack(chat_id, sticker_pack):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    # if this sticker pack is already in the list, do nothing
    cursor.execute('SELECT * FROM sticker_packs WHERE chat_id = ? AND sticker_pack = ?', (chat_id, sticker_pack))
    if cursor.fetchall():
        return
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


def save_context(chat_id, context):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO context (chat_id, context) VALUES (?, ?)', (chat_id, context))
    conn.commit()
    conn.close()


def get_context(chat_id):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT context FROM context WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return None
    if len(result[0]) == 0:
        return None
    return result[0][0]


def delete_context(chat_id):
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM context WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()


@bot.message_handler(commands=['addr', 'addreply'])
def add_on_reply(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    chat_id = message.chat.id
    try:
        sticker_pack = message.reply_to_message.sticker.set_name
    except AttributeError:
        bot.send_message(chat_id, 'Reply to a sticker to add its pack to the ban list')
        return
    add_sticker_pack(chat_id, sticker_pack)
    bot.send_message(chat_id, f'Sticker-pack {sticker_pack} added to the ban list')
    bot.delete_message(chat_id, message.reply_to_message.message_id)


@bot.message_handler(commands=['remr', 'removereply'])
def remove_on_reply(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    chat_id = message.chat.id
    try:
        sticker_pack = message.reply_to_message.sticker.set_name
    except AttributeError:
        bot.send_message(chat_id, 'Reply to a sticker to add its pack to the ban list')
        return
    sticker_pack = message.reply_to_message.sticker.set_name
    remove_sticker_pack(chat_id, sticker_pack)
    bot.send_message(chat_id, f'Sticker-pack {sticker_pack} removed from the ban list')
    bot.delete_message(chat_id, message.reply_to_message.message_id)


@bot.message_handler(commands=['add'])
def add_sticker_pack_command(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Send me a sticker from the sticker-pack you want to add to the ban list')
    save_context(chat_id, 'add')
    return


@bot.message_handler(commands=['remove', 'rem'])
def remove_sticker_pack_command(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Send me a sticker from the sticker-pack you want to remove from the ban list')
    save_context(chat_id, 'remove')
    return


@bot.message_handler(commands=['list'])
def show_banned_packs(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    chat_id = message.chat.id
    packs = get_banned_sticker_packs(chat_id)
    if len(packs) == 0:
        bot.send_message(chat_id, 'No sticker-packs are banned in this chat')
    else:
        bot.send_message(chat_id, 'Banned sticker-packs: ' + ', '.join(packs))


@bot.message_handler(content_types=['close'])
def close_context(message):
    if not is_group_owner(message):
        bot.send_message(message.chat.id, 'Only the group owner can use this command.')
        return
    delete_context(message.chat.id)


@bot.message_handler(content_types=['sticker'])
def check_sticker(message):
    context = get_context(message.chat.id)
    if context == 'add':
        add_sticker_pack(message.chat.id, message.sticker.set_name)
        bot.send_message(message.chat.id, f'Sticker-pack {message.sticker.set_name} added to the ban list')
        delete_context(message.chat.id)
        bot.delete_message(message.chat.id, message.message_id)
        return
    if context == 'remove':
        remove_sticker_pack(message.chat.id, message.sticker.set_name)
        bot.send_message(message.chat.id, f'Sticker-pack {message.sticker.set_name} removed from the ban list')
        delete_context(message.chat.id)
        return

    chat_id = message.chat.id
    sticker_pack = message.sticker.set_name
    if sticker_pack in get_banned_sticker_packs(chat_id):
        bot.delete_message(chat_id, message.message_id)


def create_table():
    conn = sqlite3.connect('sticker_packs.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS sticker_packs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id integer,
            sticker_pack text
        )
        ''')
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id integer,
            context text
        )
        ''')
    conn.commit()
    conn.close()


def is_group_owner(message):
    chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.status == 'creator'


if __name__ == '__main__':
    create_table()
    bot.polling()
