import telebot
import psycopg2
from telebot import types
from config_tg import host, user, password, database, tg_bot_token, author_tg

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
connection.autocommit = True
cursor = connection.cursor()

bot = telebot.TeleBot(tg_bot_token)

@bot.message_handler(commands=['start'])
def greeetings(message):
    startMessage = f'Привет, <b><u>{message.from_user.first_name}</u></b>. Я - бот управляющий ассортиментом мерча.'
    secMes = f'Для того, что бы вывести список всего мерча введи <u><b>/allmerch</b></u>'
    thMes = f'Для выведения списка мерча <u>в наличии</u> введи команду <u><b>/avmerch</b></u>'
    finally1 = f'Если хочешь посмотреть все доступные команды, то набери <u><b>/help</b></u>'
    fouMes = f'Если есть какие-то вопросы можешь спросить его -> {author_tg}'
    bot.send_message(message.chat.id, startMessage, parse_mode='html')
    bot.send_message(message.chat.id, secMes, parse_mode='html')
    bot.send_message(message.chat.id, thMes, parse_mode='html')
    bot.send_message(message.chat.id, finally1, parse_mode='html')
    bot.send_message(message.chat.id, fouMes, parse_mode='html')


@bot.message_handler(commands=['allmerch'])
def allmerch(message):
    cursor.execute(f'SELECT merch_id, title, price, isavailable FROM merch')
    allMerchCursor = cursor.fetchall()
    if len(allMerchCursor) != 0:
        text = '\n\n'.join(['   '.join(map(str, x)) for x in allMerchCursor])
        text = text.replace("True", "В наличии")
        text = text.replace("False", "Нет в наличии")
        bot.send_message(message.chat.id, (str(text)))

@bot.message_handler(commands=['avmerch'])
def availablemerch(message):
    cursor.execute(f'SELECT merch_id, title, price, isavailable FROM merch WHERE isavailable = True')
    availableMerchCursor = cursor.fetchall()
    if len(availableMerchCursor) != 0:
        text = '\n\n'.join(['   '.join(map(str, x)) for x in availableMerchCursor])
        text = text.replace("True", "В наличии")
        text = text.replace("False", "Нет в наличии")
        bot.send_message(message.chat.id, (str(text)))

@bot.message_handler(commands=['changeavail'])
def changemes(message):
    bot.send_message(message.chat.id, "Отправь ID товара, статус которого необходимо заменить")
    bot.register_next_step_handler(message, change)
def change(message):
    cursor.execute(f'SELECT isavailable FROM merch WHERE merch_id = {message.text}')
    merchstatus = cursor.fetchone()[0]
    if merchstatus == False:
        cursor.execute(f'UPDATE merch SET isavailable = True WHERE merch_id = {message.text}')
        bot.send_message(message.chat.id, "Статус изменен на 'В наличии'")
    else:
        cursor.execute(f'UPDATE merch SET isavailable = False WHERE merch_id = {message.text}')
        bot.send_message(message.chat.id, "Статус изменен на 'Нет в наличии'")


@bot.message_handler(commands=['changeprice'])
def pricemsg(message):
    bot.send_message(message.chat.id, "Отправь ID товара и цену которую необходимо задать в формате ID_ТОВАРА:ЦЕНА")
    bot.register_next_step_handler(message, pricechng)

def pricechng(message):
    try:
        (id, price) = message.text.split(':')
        cursor.execute(f'UPDATE merch SET price = {price} WHERE merch_id = {id}')
        bot.send_message(message.chat.id, f'Цена для товара {id} успешно обновлена на {price}')
    except:
        bot.send_message(message.chat.id, f'Неправильный формат данных, проверь еще разок')
        return pricemsg(message)


@bot.message_handler(commands=['help'])
def help(message):
    mes = f'Посмотреть все доступные товары <u><b>/allmerch</b></u> \n Посмотреть все, что есть в наличии <u><b>/avmerch</b></u>'
    mes_edit = f'Изменить доступность товара <u><b>/changeavail</b></u> \n Изменить цену товара <u><b>/changeprice</b></u>'
    bot.send_message(message.chat.id, mes, parse_mode='html')
    bot.send_message(message.chat.id, mes_edit, parse_mode='html')


bot.polling(none_stop=True)