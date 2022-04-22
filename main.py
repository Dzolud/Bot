import telebot
from telebot import types
import math
import pymorphy2
import wikipedia, re
from data import db_session
from data.profils import Profile
from data.search_history import History
from data.bookmark import Bookmarks
import requests
from werkzeug.security import generate_password_hash, check_password_hash



morph = pymorphy2.MorphAnalyzer()
wikipedia.set_lang("ru")


db_session.global_init("db/users.db")


bot = telebot.TeleBot('5385406247:AAGCPE_X1JOqoh0k6PbhAcHXR-NOkuFyO7c')


@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup_registration = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_r = types.KeyboardButton("Начать регистрацию")
    markup_registration.add(btn_r)

    print(message.chat.id)
    bot.send_message(message.chat.id, 'Я на связи. Напиши мне что-нибудь )', reply_markup=markup_registration)



markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Цифры")
btn2 = types.KeyboardButton("Слова")
btn3 = types.KeyboardButton("Фильмы")
btn4 = types.KeyboardButton("Добавить в закладки")
markup.add(btn1, btn2, btn3,
           btn4)

@bot.message_handler(content_types=["text"])
def func(message):
    if message.text == "Начать регистрацию":
        db_sess = db_session.create_session()
        if db_sess.query(Profile).filter(Profile.chat_id == message.chat.id).first():
            bot.send_message(message.chat.id, 'Вы уже зарегистрированны', reply_markup=markup)
        else:
            profil = Profile()
            profil.chat_id = message.chat.id
            r = bot.send_message(message.chat.id, text="Придумайте логин")
            bot.register_next_step_handler(r, login_check, profil)

    if message.text == "Цифры":
        r = bot.send_message(message.chat.id, text="Напиши цифру", reply_markup=None)
        bot.register_next_step_handler(r, answer_number)
    if message.text == "Слова":
        r = bot.send_message(message.chat.id, text="Напиши слово", reply_markup=None)
        bot.register_next_step_handler(r, string_answer)
    if message.text == "Фильмы":
        r = bot.send_message(message.chat.id, text="Напиши фильм", reply_markup=None)
        bot.register_next_step_handler(r, film_answer)




def login_check(message, p):
    db_sess = db_session.create_session()
    if db_sess.query(Profile).filter(Profile.login == message.text).first():
        bot.send_message(message.chat.id, 'Такой логин уже существует')
        r = bot.send_message(message.chat.id, text="Попоробуйте другой")
        bot.register_next_step_handler(r, login_check)
    else:
        p.login = message.text
        r = bot.send_message(message.chat.id, 'Придумайте пароль')
        bot.register_next_step_handler(r, end_authorization, p)


def end_authorization(message, p):
    db_sess = db_session.create_session()
    p.set_password(message.text)
    db_sess.add(p)
    db_sess.commit()
    bot.send_message(message.chat.id, 'Спасибо за регестрацию! тепер в можете пользоваться нашим сайтом и ботом!', reply_markup=markup)







def answer_number(message):
    q = message.text
    history = History()
    history.chat_id = message.chat.id
    history.request = message.text
    db_sess = db_session.create_session()
    db_sess.add(history)
    db_sess.commit()



    if q.isdigit():
        r = bot.send_message(message.chat.id, text=f"Квадрат числа: {int(q) ** 2}\n"
                                               f"Сумма чисел: {sum([int(i) for i in q])}\n"
                                               f"Корень числа: {math.sqrt(int(q))}\n"
                                               f"Факториал числа: {math.factorial(int(q))}\n"
                                               f"произведение чисел: {eval(' * '.join([i for i in q]))}\n"
                                               f"Простое или составное: {is_prime(int(q))}\n"
                                               f"Чётное или не особо: {'Чётное' if int(q) % 2 == 0 else 'Не чётное'}\n"
                                               f""
                                               f""
                                               f""
                                               f""
                         , reply_markup=markup)
        bot.register_next_step_handler(r, is_bookmark, message)
    else:
        r = bot.send_message(message.chat.id, text='Неправильный формат ввода', reply_markup=markup)
        bot.register_next_step_handler(r, is_bookmark, message)


def string_answer(message):

    history = History()
    history.chat_id = message.chat.id
    history.request = message.text
    db_sess = db_session.create_session()
    db_sess.add(history)
    db_sess.commit()

    p = morph.parse(message.text)[0]
    print(p.tag.POS, p.tag.animacy, p.tag.aspect, p.tag.case, p.tag.gender, p.tag.involvement, p.tag.mood, p.tag.number, p.tag.person, p.tag.tense, p.tag.transitivity, p.tag.voice)
    r = bot.send_message(message.chat.id, text=f"Часть речи:{p.tag.POS}\n"
                                           f"Одушевленность:{p.tag.animacy}\n"
                                           f"Вид:{p.tag.aspect}\n"
                                           f"Падеж:{p.tag.case}\n"
                                           f"Род:{p.tag.gender}\n"
                                           f"Включенность:{p.tag.involvement}\n"
                                           f"Наклонение:{p.tag.mood}\n"
                                           f"Число:{p.tag.number}\n"
                                           f"Лицо:{p.tag.person}\n"
                                           f"Время:{p.tag.tense}\n"
                                           f"Переходность:{p.tag.transitivity}\n"
                                           f"Залог:{p.tag.voice}\n"
                                           f"\n"
                                           f"\n"
                                           f"{rr(message)}", reply_markup=markup)

    bot.register_next_step_handler(r, is_bookmark, message)

#adcshcuisjic
def rr(message):
    try:
        ny = wikipedia.page(message.text)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if (len((x.strip())) > 3):
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'

def is_bookmark(message, content):
    if message.text == "Добавить в закладки":
        bm = Bookmarks()
        bm.chat_id = message.chat.id
        bm.request = content.text
        db_sess = db_session.create_session()
        db_sess.add(bm)
        db_sess.commit()
        bot.send_message(message.chat.id, 'Успешно добавленно в закладки')
    else:
        func(message)

def film_answer(message):


    history = History()
    history.chat_id = message.chat.id
    history.request = message.text
    db_sess = db_session.create_session()
    db_sess.add(history)
    db_sess.commit()


    response = requests.get(
        f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={message.text}&page=1',
        headers={'X-API-KEY': "7f118a01-f5a2-4b10-b7ea-85463dff50e2"
                 }

    )
    re = response.json()
    p = requests.get(re['films'][0]['posterUrl'])
    out = open("img.jpg", "wb")
    out.write(p.content)
    out.close()
    q = open("img.jpg", "rb")
    f = ", ".join(i['genre'].capitalize() for i in re['films'][0]['genres'])
    ff = ", ".join(i['country'] for i in re['films'][0]['countries'])
    r = bot.send_photo(message.chat.id, q, caption=f"Название: {re['films'][0]['nameRu']}\n"
                                               f"Название на Аглийском: {re['films'][0]['nameEn']}\n"
                                               f"Описание: {re['films'][0]['description']}\n"
                                               f"Длина фильма: {re['films'][0]['filmLength']}\n"
                                               f"Страна Производства: {ff}\n"
                                               f"Жанр: {f}\n"
                                               f"Рэйтинг: {re['films'][0]['rating']}\n", reply_markup=markup)
    bot.register_next_step_handler(r, is_bookmark, message)


def is_prime(n):
    if n < 2:
        return 'Составное'
    if n == 2:
        return 'Простое'
    limit = math.sqrt(n)
    i = 2
    while i <= limit:
        if n % i == 0:
            return 'Составное'
        i += 1
    return 'Простое'


def check_profils(login, password):
    db_sess = db_session.create_session()
    if login in [prof.login for prof in db_sess.query(Profile).all()]:
        if check_password_hash(db_sess.query(Profile).filter(Profile.login == login).first().hashed_password, password):
            return True
        return False
    return False


bot.polling(none_stop=True, interval=0)