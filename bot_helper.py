import telebot
import json
from config import CONTROL_BOT_API
import time
import asyncio
# from python_socks.async_.asyncio import ProxyType
from telethon import TelegramClient, errors, functions, types, events, utils


bot = telebot.TeleBot(CONTROL_BOT_API)
JSON_BD = 'subs.json'
CHANNEL_DB = 'channel.json'


# async def client_connect():
#     try:
#         client = TelegramClient(session='./accounts/account' + str(i) + '.session',
#                                 api_id=apps['api_id'],
#                                 api_hash=apps['api_hash'],
#                                 device_model=random.choice(MODEL),
#                                 app_version=random.choice(VERSION),
#                                 lang_code=random.choice(LANG_CODE),
#                                 system_lang_code=random.choice(LANG),
#                                 proxy=proxxy)
#         await client.connect()
#         return client
#     except errors.UserDeactivatedBanError as e:
#         print(f"аккаунт {i} забанен")
#     except BaseException as e:
#         print(e)
#         print("Ошибка на аккаунте" + str(i) + ", proxy", proxxy)

def updating_script():
    one_day_subs = []
    two_day_subs = []
    deleted_subs = []
    deleted_subs_id = []

    try:
        with (open(CHANNEL_DB, mode='r', encoding='utf-8') as CHANNEL_D):
            data = json.load(CHANNEL_D)
            CHANNEL_TO_CHECK = data["sub_channel"]

        with (open(CHANNEL_DB, mode='r', encoding='utf-8') as CHANNEL_D):
            data = json.load(CHANNEL_D)
            CHANNEL_TO_CONTROL = data["control_channel"]

        try:
            with (open(JSON_BD, mode='r', encoding='utf-8') as JSON_B):
                data = json.load(JSON_B)
                for el in data:
                    updated_name = "@" + bot.get_chat_member(CHANNEL_TO_CHECK, el).user.username
                    data[el]['tg_name'] = updated_name

                    if data[el]['days_left'] > 0:
                        data[el]['days_left'] -= 1
                        if data[el]['days_left'] == 1:
                            two_day_subs.append(data[el]["tg_name"])
                        elif data[el]['days_left'] == 0:
                            one_day_subs.append(data[el]["tg_name"])
                    else:
                        deleted_subs.append(data[el]["tg_name"])
                        deleted_subs_id.append(el)
                        try:
                            bot.kick_chat_member(CHANNEL_TO_CHECK, el)
                        except BaseException:
                            a = 1
                        try:
                            bot.decline_chat_join_request(CHANNEL_TO_CHECK, el)
                        except BaseException:
                            a = 1

            for el in deleted_subs_id:
                del data[el]

            two_day_sub_text = "Подписчики, у которых осталось 2 дней до конца подписки:\n"
            for sub in two_day_subs:
                two_day_sub_text += sub + "\n"
            one_day_sub_text = "Подписчики, у которых осталось 1 день до конца подписки:\n"
            for sub in one_day_subs:
                one_day_sub_text += sub + "\n"

            deleted_sub_text = "Подписчики, которые были исключены из канала:\n"
            for sub in deleted_subs:
                deleted_sub_text += sub + "\n"

            spares = '-----------------------------------\n'
            bot.send_message(CHANNEL_TO_CONTROL, text=spares + two_day_sub_text + one_day_sub_text + deleted_sub_text)

            # client = client_connect()
            # client.send_message()

            with open(JSON_BD, mode='w', encoding='utf-8') as JSON_D:
                json.dump(data, JSON_D)
        except BaseException as e:
            bot.send_message(CHANNEL_TO_CONTROL, text=f'При обновлении произошла ошибка {e}')
    except BaseException as e:
        bot.send_message(CHANNEL_TO_CONTROL, text=f'При обновлении произошла ошибка {e}')


if __name__ == "__main__":
    # schedule.every().day.at("midnight").do(updating_script())

    while True:
        #schedule.run_pending()
        try:
            updating_script()
            time.sleep(10)
            # time.sleep(86400)
        except:
            print('YAHOO')
