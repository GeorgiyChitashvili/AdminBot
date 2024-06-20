import telebot
import telebot.types as types
import json
from config import BOT_API

bot = telebot.TeleBot(BOT_API)
JSON_BD = 'subs.json'
CHANNEL_DB = 'channel.json'


@bot.chat_join_request_handler()
def join_request_processing(message):
    sub_id = message.from_user.id
    sub_name = message.from_user.username

    # Передача обработанных данных в JSON-БД
    with (open(JSON_BD, mode='r', encoding='utf-8') as JSON_D):
        data = json.load(JSON_D)
        data[sub_id] = {"tg_name": sub_name, "days_left": 1}

    with open(JSON_BD, mode='w', encoding='utf-8') as JSON_D:
        json.dump(data, JSON_D)



@bot.message_handler(commands=['start'])
def main(message: types.Message):
    try:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                             one_time_keyboard=True)
        btn1 = types.KeyboardButton(text="Добавить подписчика(ов)")
        btn2 = types.KeyboardButton(text="Удалить подписчика(ов)")
        btn3 = types.KeyboardButton(text="Смена канала")
        btn4 = types.KeyboardButton(text="Смена контроля")
        keyboard.row(btn1, btn2)
        keyboard.row(btn3, btn4)

        bot.send_message(message.chat.id, "Выберите, действие? ", reply_markup=keyboard)
        bot.register_next_step_handler(callback=callback_check, message=message)
    except BaseException as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка {e}')

def callback_check(message: types.Message):
    try:
        if message.text == "Добавить подписчика(ов)":
            bot.send_message(message.chat.id,
                             "Выбрано: Добавить подписчика(ов). "
                             "Введите данные в следующем формате:\n"
                             "Telegram-ник (Начинается с @) - Кол-во дней подписки/продления подписки. "
                             "Пример:\n"
                             "@artem - 7\n"
                             "@denis - 7\n")



            bot.register_next_step_handler(callback=add_sub, message=message)

        elif message.text == "Удалить подписчика(ов)":
            bot.send_message(message.chat.id,"Выбрано: Удалить подписчика(ов). "
                             "В одном сообщении на разных строках введите данные в следующем формате:\n"
                             "ID подписчика. Используйте @userdatailsbot (https://t.me/userdatailsbot)")
            bot.register_next_step_handler(callback=delete_sub, message=message)

        elif message.text == "Смена канала":
            bot.send_message(message.chat.id,"Выбрано: Сменить канал отслеживания. "
                             "Перешлите любое сообщение из частного канала этому боту")
            bot.register_next_step_handler(callback=change_channel, message=message)

        elif message.text == "Смена контроля":
            bot.send_message(message.chat.id,"Выбрано: Сменить канал отслеживания. "
                             "Перешлите любое сообщение из частного канала этому боту")
            bot.register_next_step_handler(callback=change_control, message=message)

        else:
            bot.send_message(message.chat.id, 'Простите, я вас не понимаю!')
            bot.register_next_step_handler(callback=main, message=message)
            return ''
    except BaseException as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка {e}')

def add_sub(message: types.Message):
    # Sending SKU's from one manager to another
    data = message.text
    subs = data.split('\n')

    with (open(CHANNEL_DB, mode='r', encoding='utf-8') as CHANNEL_D):
        data = json.load(CHANNEL_D)
        channel_id = data["sub_channel"]

    # Передача обработанных данных в JSON-БД
    with (open(JSON_BD, mode='r', encoding='utf-8') as JSON_D):
        data = json.load(JSON_D)
        for sub in subs:
            sub_name = sub.split(' - ')[0]

            if not sub_name.startswith("@"):
                bot.send_message(message.chat.id, text=f"Ошибка в запросе! {sub_name} должен начинаться с @. "
                                                       f"{sub_name} не был добавлен")
                continue

            for el in data:
                try:
                    tg_name = bot.get_chat_member(channel_id, el)
                    data[el]['tg_name'] = "@" + tg_name.user.username
                    if data[el]['tg_name'] == sub_name:
                        sub_id = el
                        break
                except BaseException as e:
                    print("not in chat")
            else:
                bot.send_message(message.chat.id, text=f'Пользователь {sub_name} не присылал заявку')
                continue

            try:
                sub_days = int(sub.split(' - ')[1])
                data[sub_id]['days_left'] += sub_days
                try:
                    bot.approve_chat_join_request(channel_id, sub_id)
                except BaseException as e:
                    bot.send_message(message.chat.id, text='Подписчик уже в канале!')
            except BaseException as e:
                bot.send_message(message.chat.id, text='Некорректный ввод.')


    with open(JSON_BD, mode='w', encoding='utf-8') as JSON_D:
        json.dump(data, JSON_D)

    # SENDING ONE DATA_SHEET TO ANOTHER MANAGER'S WORKBOOK
    bot.send_message(message.chat.id, text='Подписчик добавлен')

def delete_sub(message: types.Message):
    try:
        data = message.text
        subs = data.split('\n')

        with (open(JSON_BD, mode='r', encoding='utf-8') as JSON_D):
            data = json.load(JSON_D)
            for sub in subs:
                if sub in data:
                    del data[sub]

        with open(JSON_BD, mode='w', encoding='utf-8') as JSON_D:
            json.dump(data, JSON_D)

        bot.send_message(message.chat.id, text='Подписчик удален')
    except BaseException as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка {e}')

def change_channel(message: types.Message):
    try:
        info = message.forward_from_chat.id
        print(info)

        with (open(CHANNEL_DB, mode='r', encoding='utf-8') as CHANNEL_D):
            data = json.load(CHANNEL_D)
            data["sub_channel"] = info

        with open(CHANNEL_DB, mode='w', encoding='utf-8') as CHANNEL_D:
            json.dump(data, CHANNEL_D)

        bot.send_message(message.chat.id, text='Активный канал изменен')
    except BaseException as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка {e}')

def change_control(message: types.Message):
    try:
        info = message.forward_from_chat.id
        print(info)

        with (open(CHANNEL_DB, mode='r', encoding='utf-8') as CHANNEL_D):
            data = json.load(CHANNEL_D)
            data["control_channel"] = info

        with open(CHANNEL_DB, mode='w', encoding='utf-8') as CHANNEL_D:
            json.dump(data, CHANNEL_D)

        bot.send_message(message.chat.id, text='Канал контроля изменен')
    except BaseException as e:
        bot.send_message(message.chat.id, text=f'Произошла ошибка {e}')

if __name__ == "__main__":
    bot.infinity_polling()
