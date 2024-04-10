import json
from telebot import TeleBot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import csv
from schedule import every, repeat, run_pending
import time
import os
from dotenv import load_dotenv
import threading
from prettytable import from_csv


load_dotenv()
token = os.getenv('TOKEN')

bot = TeleBot(token)

test = 1
nick = 'name'
REMINDER_LIST_PATH_NAME = 'reminder_list.json'
RESCHEDULE_LIST_PATH_NAME = 'reschedule.json'


def show_saturday(message):
    with open("data_list_1.csv") as fp:
        mytable = from_csv(fp)
    bot.send_message(message.chat.id, mytable.get_string())


def show_sunday(message):
    with open("data_list_2.csv") as fp:
        mytable = from_csv(fp)
    bot.send_message(message.chat.id, mytable.get_string())


def send_sorry_message(message):
    bot.send_message(message.chat.id, "Очень жаль🥺 Ждем на следующей неделе!")


def reschedule(message):
    if os.path.isfile(RESCHEDULE_LIST_PATH_NAME):
        with open(RESCHEDULE_LIST_PATH_NAME, 'r') as file:
            data = json.load(file)
        with open(RESCHEDULE_LIST_PATH_NAME, 'w') as file:
            if message.from_user.id not in data.keys():
                data[str(message.chat.id)] = {
                    'username': message.from_user.first_name,
                    'days_until_notify': 3
                }
                file.write(json.dumps(data))
    else:
        with open(RESCHEDULE_LIST_PATH_NAME, 'w') as file:
            data = {str(message.chat.id): {
                'username': message.from_user.first_name,
                'days_until_notify': 3
            }}
            file.write(json.dumps(data))
    bot.send_message(message.chat.id, "Напоминания установлены✅")


@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    print(message)

    bot.send_message(message.chat.id, 'Добро пожаловать в семью Al Capone!😎\n'
                                      '\n'
                                      'Для навигации используй команды указанные ниже:\n'
                                      '\n✅✍️ /in - для записи на игровую сессию \n'
                                      '\n❎✍️ /out - для отмены записи \n'
                                      '\n📝 /list - для отображения записанных игроков \n'
                                      '\n📃 /guide - для ознакомления с правилами игровых сессий \n'
                                      '\n📍 /location - для отображения места проведения игровых сессий \n'
                                      '\n⏰ /reminder - для установления напоминалки о записи \n'
                                      '\n⏰ /delete_reminder - для удаления напоминалки о записи \n'
                                      '\n'
                                      'Так же, можешь воспользоваться кнопкой \'меню\' в левом нижнем углу.\n'
                                      '\nP.s: Списки обнуляются по окончанию крайнего игрового вечера, не забывайте записываться на следующие вечера🎩')


@bot.message_handler(commands=['reminder'])
def enter_list(message):
    if os.path.isfile(REMINDER_LIST_PATH_NAME):
        with open(REMINDER_LIST_PATH_NAME, 'r') as file:
            data = json.load(file)
        with open(REMINDER_LIST_PATH_NAME, 'w') as file:
            if message.from_user.id not in data.keys():
                data[str(message.chat.id)] = {
                    'username': message.from_user.first_name
                }
                file.write(json.dumps(data))
            else:
                return
    else:
        with open(REMINDER_LIST_PATH_NAME, 'w') as file:
            data = {str(message.chat.id): {
                'username': message.from_user.first_name
            }}
            file.write(json.dumps(data))
    bot.send_message(message.chat.id, 'Напоминания установлены✅')


@bot.message_handler(commands=['delete_reminder'])
def remove_from_list(message):

    if os.path.isfile(REMINDER_LIST_PATH_NAME):
        data = None
        with open(REMINDER_LIST_PATH_NAME, 'r') as file:
            data = json.load(file)
        with open(REMINDER_LIST_PATH_NAME, 'w') as file:
            if str(message.chat.id) in data.keys():
                data.pop(str(message.chat.id))
            if len(data) == 0:
                os.remove(REMINDER_LIST_PATH_NAME)
            else:
                file.write(json.dumps(data))
    bot.send_message(message.chat.id, 'Напоминания удалены❎')


@bot.message_handler(commands=['in'])
def reg(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    item_button = KeyboardButton('суббота')
    item_button2 = KeyboardButton('воскресенье')
    markup.add(item_button)
    markup.add(item_button2)
    bot.send_message(message.chat.id, 'Выберите день', reply_markup=markup)

    bot.register_next_step_handler(message, registr)


def registr(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Запись приостановленна❎')
    elif message.text == 'суббота':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм✅✍️')
        bot.register_next_step_handler(message, saturday_nick_func)
    elif message.text == 'воскресенье':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм✅✍️')
        bot.register_next_step_handler(message, sunday_nick_func)


######################################################################################
def saturday_nick_func(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Запись приостановленна❎')
    else:
        global nick
        nick = str(message.text)
        bot.send_message(message.chat.id, 'Как долго планируете играть?')
        bot.register_next_step_handler(message, saturday_remark_func)


def saturday_remark_func(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Запись приостановленна❎')
    else:
        data_record = str(nick) + ',' + str(message.text) + '\n'
        with open('data_list_1.csv', mode='a') as file:
            file.write(data_record)

        markup_saturday = types.InlineKeyboardMarkup()
        markup_saturday.add(types.InlineKeyboardButton('Посмотреть список на субботу', callback_data='show_saturday'))
        bot.send_message(message.chat.id, 'Запись прошла успешно!✅', reply_markup=markup_saturday)


@bot.callback_query_handler(func=lambda call: True)
def call_back(call):
    match call.data:
        case "show_saturday":
            show_saturday(call.message)
        case 'show_sunday':
            show_sunday(call.message)
        case 'in':
            reg(call.message)
        case 'not':
            send_sorry_message(call.message)
        case 'reschedule':
            reschedule(call.message)


####################################################################################
def sunday_nick_func(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Запись приостановленна❎')
    else:
        global nick
        nick = str(message.text)
        bot.send_message(message.chat.id, 'Как долго планируете играть?')
        bot.register_next_step_handler(message, sunday_remark_func)


def sunday_remark_func(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Запись приостановленна❎')
    else:
        data_record = str(nick) + ',' + str(message.text) + '\n'
        with open('data_list_2.csv', mode='a') as file:
            file.write(data_record)

        markup_sunday = types.InlineKeyboardMarkup()
        markup_sunday.add(types.InlineKeyboardButton('Посмотреть список на воскресенье', callback_data='show_sunday'))
        bot.send_message(message.chat.id, 'Запись прошла успешно!✅', reply_markup=markup_sunday)


#########################################################################################


@bot.message_handler(commands=['out'])
def rm(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    item_button = KeyboardButton('суббота')
    item_button2 = KeyboardButton('воскресенье')
    markup.add(item_button)
    markup.add(item_button2)
    bot.send_message(message.chat.id, 'Выберите день', reply_markup=markup)

    bot.register_next_step_handler(message, rm_func)


def rm_func(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Удаление приостановленно❎')
    elif message.text == 'суббота':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм❎✍️')
        bot.register_next_step_handler(message, saturday_rm)
    elif message.text == 'воскресенье':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм❎✍️')
        bot.register_next_step_handler(message, sunday_rm)


def saturday_rm(message):
    with open('data_list_1.csv', 'r') as file:
        reader = csv.reader(file)
        data_rm = list(reader)
        updated_data = [row for row in data_rm if row[0] != message.text]
    with open('data_list_1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)

    markup_saturday = types.InlineKeyboardMarkup()
    markup_saturday.add(types.InlineKeyboardButton('Посмотреть список на субботу', callback_data='show_saturday'))
    bot.send_message(message.chat.id, 'Вы были удалены из списка❎', reply_markup=markup_saturday)


def sunday_rm(message):
    with open('data_list_2.csv', 'r') as file:
        reader = csv.reader(file)
        data_rm = list(reader)
        updated_data = [row for row in data_rm if row[0] != message.text]
    with open('data_list_2.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)

    markup_sunday = types.InlineKeyboardMarkup()
    markup_sunday.add(types.InlineKeyboardButton('Посмотреть список на воскресенье', callback_data='show_sunday'))
    bot.send_message(message.chat.id, 'Вы были удалены из списка❎', reply_markup=markup_sunday)


#########################################################################################
@bot.message_handler(commands=['list'])
def lst(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    item_button = KeyboardButton('суббота')
    item_button2 = KeyboardButton('воскресенье')
    markup.add(item_button)
    markup.add(item_button2)
    bot.send_message(message.chat.id, 'Выберите день', reply_markup=markup)

    bot.register_next_step_handler(message, show)


def show(message):
    if '/' in message.text:
        bot.send_message(message.chat.id, 'Отмена просмотра списка❎')
    elif message.text == 'суббота':
        with open("data_list_1.csv") as fp:
            mytable = from_csv(fp)
        bot.send_message(message.chat.id, mytable.get_string())
    elif message.text == 'воскресенье':
        with open("data_list_2.csv") as fp:
            mytable = from_csv(fp)
        bot.send_message(message.chat.id, mytable.get_string())


#######################################################################################
@bot.message_handler(commands=['guide'])
def rules(message):
    file = open('image.png', 'rb')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Oбучающие видео по Мафии', url='https://www.youtube.com/playlist?list=PLrDRU9lcDcit1DBV9FDKxTjbh9JRfBLma'))
    bot.send_photo(message.chat.id, file, reply_markup=markup)


@bot.message_handler(commands=['location'])
def loc(message):

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Вход', url='https://youtu.be/RUqr4jRPN9M?si=RNGVirp03QGiV8y4'))
    markup.add(types.InlineKeyboardButton('Посмотреть на карте', url='https://maps.google.com/maps?q=43.210383,27.907334&ll=43.210383,27.907334&z=16'))
    bot.send_message(message.chat.id, 'Владислав Варненчик 53-55📍', reply_markup=markup)


@bot.message_handler()
def reg_next_step(message):
    bot.send_message(message.chat.id, 'Для грамотной навигации используйте команды из главного меню')


@repeat(every().monday.at("00:01"))
def clear_csv():
    os.remove('data_list_1.csv')
    os.remove('data_list_2.csv')
    init_csv_headers()


# @repeat(every(5).seconds)
@repeat(every().monday.at("10:00"))
def notify_users():
    if os.path.isfile(REMINDER_LIST_PATH_NAME):
        with open(REMINDER_LIST_PATH_NAME, 'r') as reminder_list_file:
            reminder_chats = json.load(reminder_list_file)
            for chat_id, user_info in reminder_chats.items():
                markup_sunday = types.InlineKeyboardMarkup()
                markup_sunday.add(
                    types.InlineKeyboardButton('Записаться', callback_data='in'),
                )
                markup_sunday.add(
                    types.InlineKeyboardButton('Не смогу :(', callback_data='not'),
                )
                markup_sunday.add(
                    types.InlineKeyboardButton('Напомнить через 3 дня', callback_data='reschedule'),
                )
                message = f"{user_info['username']}, записывайся на игровые вечера 😄"
                bot.send_message(chat_id, message, reply_markup=markup_sunday)


# @repeat(every(30).seconds)
@repeat(every().day.at("10:00"))
def notify_in_3_days_users():
    ids_to_be_poped = []
    if os.path.isfile(RESCHEDULE_LIST_PATH_NAME):
        reminder_chats = None
        with open(RESCHEDULE_LIST_PATH_NAME, 'r') as reschedule_list_file:
            reminder_chats = json.load(reschedule_list_file)

        for chat_id, user_info in reminder_chats.items():
            reminder_chats[str(chat_id)]['days_until_notify'] -= 1
            user_days_left = int(user_info['days_until_notify'])
            if user_days_left > 0:
                continue
            elif user_days_left == 0:
                ids_to_be_poped.append(str(chat_id))
                message = f"{user_info['username']}, записывайся на игровые вечера 😄"
                bot.send_message(chat_id, message)
        os.remove(RESCHEDULE_LIST_PATH_NAME)
        with open(RESCHEDULE_LIST_PATH_NAME, 'w') as reschedule_list_file:
            for chat_id in ids_to_be_poped:
                reminder_chats.pop(chat_id)
            if len(reminder_chats) > 0:
                reschedule_list_file.write(json.dumps(reminder_chats))
            else:
                os.remove(RESCHEDULE_LIST_PATH_NAME)


def init_csv_headers():
    if not os.path.isfile('data_list_1.csv'):
        with open('data_list_1.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Имя', 'Желаемое время игры'])

    if not os.path.isfile('data_list_2.csv'):
        with open('data_list_2.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Имя', 'Желаемое время игры'])


def job_queue():
    while True:
        run_pending()
        time.sleep(1)


def do_bot_polling():
    print("STARTED")
    bot.infinity_polling(timeout=10, long_polling_timeout = 5)


def main():
    print("Starting the bot...")
    init_csv_headers()
    threads = []
    notification_thread = threading.Thread(target=job_queue)
    bot_polling_thread = threading.Thread(target=do_bot_polling)
    threads.append(notification_thread)
    threads.append(bot_polling_thread)

    for thread in threads:
        thread.start()

    # notification_process = Process(target=job_queue)
    # bot_polling_process = Process(target=do_bot_polling)

    # notification_process.start()
    # bot_polling_process.start()
    #
    # notification_process.join()
    # bot_polling_process.join()


if __name__ == '__main__':
    main()
