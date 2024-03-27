from telebot import TeleBot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import csv
import schedule
import time
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('TOKEN')

bot = TeleBot(token)

nick = 'name'


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
                                      '\n🎛 /menu - для возвращения в меню \n'
                                      '\n'
                                      'Так же, можешь воспользоваться кнопкой \'меню\' в левом нижнем углу.\n'
                                      '\nP.s: Списки обнуляются по окончанию крайнего игрового вечера, не забывайте записываться на следующие вечера🎩')


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
    if message.text == 'суббота':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм✅✍️')
        bot.register_next_step_handler(message, saturday_nick_func)
    elif message.text == 'воскресенье':
        bot.send_message(message.chat.id, 'Введите ваш ник-нейм✅✍️')
        bot.register_next_step_handler(message, sunday_nick_func)


######################################################################################
def saturday_nick_func(message):
    global nick
    nick = str(message.text)
    bot.send_message(message.chat.id, 'Оставьте ремарку💭')
    bot.register_next_step_handler(message, saturday_remark_func)


def saturday_remark_func(message):

    data_record = str(nick) + ',' + str(message.text) + '\n'
    with open('data_list_1.csv', mode='a') as file:
        file.write(data_record)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть список участников', callback_data='суббота'))
    bot.send_message(message.chat.id, 'Запись прошла успешно!✅', reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def call_back(call):
    show(call.message)


####################################################################################
def sunday_nick_func(message):
    global nick
    nick = str(message.text)
    bot.send_message(message.chat.id, 'Оставьте ремарку💭')
    bot.register_next_step_handler(message, sunday_remark_func)


def sunday_remark_func(message):
    data_record = str(nick) + ',' + str(message.text) + '\n'
    with open('data_list_2.csv', mode='a') as file:
        file.write(data_record)

    bot.send_message(message.chat.id, 'Запись прошла успешно!✅')


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
    if message.text == 'суббота':
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
    bot.send_message(message.chat.id, 'Вы были удалены из списка❎')


def sunday_rm(message):
    with open('data_list_2.csv', 'r') as file:
        reader = csv.reader(file)
        data_rm = list(reader)
        updated_data = [row for row in data_rm if row[0] != message.text]
    with open('data_list_2.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)
    bot.send_message(message.chat.id, 'Вы были удалены из списка❎')


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
    if message.text == 'суббота':
        with open('data_list_1.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                bot.send_message(message.chat.id, str(row))

    elif message.text == 'воскресенье':
        with open('data_list_2.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                bot.send_message(message.chat.id, str(row))


#######################################################################################
@bot.message_handler(commands=['guide'])
def rules(message):
    file = open('image.png', 'rb')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Oбучающие видео по Мафии', url='https://www.youtube.com/playlist?list=PLrDRU9lcDcit1DBV9FDKxTjbh9JRfBLma'))
    bot.send_photo(message.chat.id, file, reply_markup=markup)
#    bot.send_message(message.chat.id, 'Правила клуба:\n'
#                                      '\n'
#                                      'Первое правило клуба: ')
#ToDo


@bot.message_handler(commands=['location'])
def loc(message):

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Вход', url='https://youtu.be/RUqr4jRPN9M?si=RNGVirp03QGiV8y4'))
    markup.add(types.InlineKeyboardButton('Посмотреть на карте', url='https://maps.google.com/maps?q=43.210383,27.907334&ll=43.210383,27.907334&z=16'))
    bot.send_message(message.chat.id, 'Владислав Варненчик 53-55📍', reply_markup=markup)


@bot.message_handler()
def reg_next_step(message):
    bot.send_message(message.chat.id, 'Для грамотной навигации используйте команды из главного меню')


def clear_csv():
    os.remove('data_list_1.csv')
    os.remove('data_list_2.csv')
    init_csv_headers()


schedule.every().monday.at("00:01").do(clear_csv)


def init_csv_headers():
    if not os.path.isfile('data_list_1.csv'):
        with open('data_list_1.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Имя', 'Ремарка'])

    if not os.path.isfile('data_list_2.csv'):
        with open('data_list_2.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Имя', 'Ремарка'])


def job_queue():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    bot.polling()
    init_csv_headers()
    job_queue()


if __name__ == '__main__':
    main()

