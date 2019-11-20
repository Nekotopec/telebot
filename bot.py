# Import token and data base url.
from settings_vars import DBURL, TOKEN

import telebot
import re
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from models import User, Ad, Base
from collections import defaultdict
engine = create_engine(DBURL, echo=True, encoding='utf-8',)


bot = telebot.TeleBot(TOKEN)
STOP = 500
START = 0
FIRST_NAME, LAST_NAME, TELEPHONE_NUMBER, REINTRODUSING = range(1, 5)
OBJ, DESCRIPTION, PRICE, REPLACING, CHOICE = range(1, 6)
DELETING = 1
cash_dict = dict()
introdusing_pos = defaultdict(lambda: START)
ad_creating_pos = defaultdict(lambda: START)
delete_pos = defaultdict(lambda: START)
flag = defaultdict(lambda: False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)


def validate_first_name(message):
    """ Validate First name."""
    if len([mes for mes in message.text.split(' ')]) > 1:
        bot.send_message(message.chat.id, 'First name cannot contain spaces')
        return False
    if re.search(r'\d+', message.text):
        bot.send_message(message.chat.id, 'First name cannot contain numbers')
        return False
    return True


def validate_last_name(message):
    """ Validate Last name."""
    if len([mes for mes in message.text.split(' ')]) > 1:
        bot.send_message(message.chat.id, 'Last name cannot contain spaces')
        return False
    if re.search(r'\d+', message.text):
        bot.send_message(message.chat.id, 'Lust name cannot contain numbers')
        return False
    return True


def validate_telephone_number(message):
    """ Validate telephone number."""
    if len([mes for mes in message.text.split(' ')]) > 11 and len([mes for mes in message.text.split(' ')]) < 9:
        bot.send_message(message.chat.id, 'Your number is not formated')
        return False
    if re.search(r'[^\d ]+', message.text):
        bot.send_message(message.chat.id, 'Number cannot contain letters')
        return False
    return True


def introdusing(message):
    u = User(message.chat.id, cash_dict[message.chat.id]['FIRST_NAME'],
             cash_dict[message.chat.id]['LAST_NAME'], cash_dict[message.chat.id]['TELEPHONE_NUMBER'])
    introdusing_pos[message.chat.id] = STOP
    session.add(u)
    session.commit()
    bot.send_message(message.chat.id, 'You introdused yourself.')


def reintrodusing(message):
    u = session.query(User).filter(User.chat_id == int(message.chat.id)).one()
    u.first_name = cash_dict[message.chat.id]['FIRST_NAME']
    u.last_name = cash_dict[message.chat.id]['LAST_NAME']
    u.telephone_number = cash_dict[message.chat.id]['TELEPHONE_NUMBER']
    introdusing_pos[message.chat.id] = STOP
    session.add(u)
    session.commit()
    bot.send_message(message.chat.id, 'You introdused yourself.')


def validate_obj(message):
    """ Validate object name."""
    if len([mes for mes in message.text.split(' ')]) > 5:
        bot.send_message(message.chat.id, 'Use 5 words to name the object')
        return False
    return True


def validate_description(message):
    """ Validate description."""
    length = len(message.text)
    if length > 255:
        bot.send_message(
            message.chat.id, 'Too long description. Maximum number of symbols is 255. You typed{}'.format(length))
        return False
    return True


def validate_price(message):
    """ Validate price"""
    if len([mes for mes in message.text.split(' ')]) > 1:
        bot.send_message(message.chat.id, 'Dont use spaces while seting price')
        return False
    if re.search(r'[^\d ]+', message.text):
        bot.send_message(message.chat.id, 'Price cannot contain letters')
        return False
    return True


def look_for_similar_ad(message):
    """ Looking for similar ads of current user"""
    names_list = message.text.lower().split()
    regexp = '(' + '|'.join(names_list) + ')'
    ads = session.query(Ad).filter(Ad.obj.op('regexp')(regexp)).all()
    if ads:
        bot.send_message(message.chat.id, 'Your similar ads')
        for ad in ads:
            bot.send_message(message.chat.id, 'Ad\'s id:\t{}.\nObject:\t{}.\nDescription:\t{}.\nPrice:\t{}.'.format(
                ad.id, ad.obj.title(), ad.description, ad.price))
        return ads
    return None


def replacing_ad(message, ad_id):
    """ Replace the ad."""

    ad = session.query(Ad).filter(Ad.id == ad_id).one()
    ad.obj = cash_dict[message.chat.id]['OBJ'].lower()
    ad.description = cash_dict[message.chat.id]['DESCRIPTION']
    ad.price = cash_dict[message.chat.id]['PRICE']
    bot.send_message(message.chat.id, 'Ad was replaced.')
    session.commit()


def place_ad(chat_id):
    """ Place the ad"""
    u = session.query(User).filter(User.chat_id == int(chat_id)).one()
    ad = Ad(cash_dict[chat_id]['OBJ'].lower(), cash_dict[chat_id]
            ['DESCRIPTION'], cash_dict[chat_id]['PRICE'])
    ad.user = u
    session.add(ad)
    session.commit()
    bot.send_message(chat_id, 'Your ad was created.')


def is_introdused(chat_id):
    if session.query(User.chat_id).filter(User.chat_id == int(chat_id)).all():
        return True
    else:
        return False


def delete_ad(message):
    """ Delete selected ads of current user"""
    reg_ids = re.findall(r'^\d+$')
    ads = session.query(Ad).filter(Ad.id.in_(reg_ids)).all().delete()
    session.commit()
    bot.send_message(message.chat.id, 'Ads were deleted')


@bot.message_handler(commands=['start', 'help'])
def help(message):
    mes = """
    Hello. I am bot to creating ads. You must introduce yourself before adding an ad.
    To introdusing use /iam.
    To create an ad type /ad
    To remove ad use /del or /remove
    To view the list of your ads type /myads
    """
    bot.send_message(message.chat.id, mes)


@bot.message_handler(commands=['iam'])
def introdusing_start(message):
    bot.send_message(message.chat.id, 'What is your first name?')
    cash_dict[message.chat.id] = dict()
    introdusing_pos[message.chat.id] = FIRST_NAME


@bot.message_handler(func=lambda message: introdusing_pos[message.chat.id] == FIRST_NAME)
def introdusing_first_name(message):
    if validate_first_name(message):
        bot.send_message(message.chat.id, 'What is your last name?')
        cash_dict[message.chat.id]['FIRST_NAME'] = message.text
        introdusing_pos[message.chat.id] = LAST_NAME


@bot.message_handler(func=lambda message: introdusing_pos[message.chat.id] == LAST_NAME)
def introdusing_first_name(message):
    if validate_last_name(message):
        bot.send_message(message.chat.id, 'What is your telephone number?')
        cash_dict[message.chat.id]['LAST_NAME'] = message.text
        introdusing_pos[message.chat.id] = TELEPHONE_NUMBER


@bot.message_handler(func=lambda message: introdusing_pos[message.chat.id] == TELEPHONE_NUMBER)
def introdusing_first_name(message):
    if validate_telephone_number(message):
        cash_dict[message.chat.id]['TELEPHONE_NUMBER'] = message.text
        if session.query(User.chat_id).filter(User.chat_id == int(message.chat.id)).all():
            bot.send_message(
                message.chat.id, 'You have introdused already. Would you like to reintroduse (Yes/No)')
            introdusing_pos[message.chat.id] = REINTRODUSING
        else:
            introdusing(message)


@bot.message_handler(func=lambda message: introdusing_pos[message.chat.id] == REINTRODUSING)
def reintrodusing_message(message):
    if re.search(r'yes', message.text.lower()):
        reintrodusing(message)
    else:
        introdusing_pos[message.chat.id] = STOP
        bot.send_message(message.chat.id, 'You didn\'t reintroduse.')


@bot.message_handler(commands=['ad'])
def start_ad(message):
    if is_introdused(message.chat.id):
        bot.send_message(message.chat.id, 'What do you want to sale')
        cash_dict[message.chat.id] = dict()
        ad_creating_pos[message.chat.id] = OBJ
    else:
        bot.send_message(message.chat.id, 'You must introduse before creating ad')
        introdusing_start(message)


@bot.message_handler(func=lambda message: ad_creating_pos[message.chat.id] == OBJ)
def obj_ad(message):
    if validate_obj(message):
        if not look_for_similar_ad(message):
            bot.send_message(message.chat.id, 'Describe the object')
            cash_dict[message.chat.id]['OBJ'] = message.text
            ad_creating_pos[message.chat.id] = DESCRIPTION
        else:
            cash_dict[message.chat.id]['OBJ'] = message.text
            bot.send_message(
                message.chat.id, 'You have placed a similar ad already. Would you like to replace it? (Yes/No)')
            ad_creating_pos[message.chat.id] = REPLACING


@bot.message_handler(func=lambda message: ad_creating_pos[message.chat.id] == REPLACING)
def description_ad(message):
    if re.search(r'yes', message.text.lower()):
        ad_creating_pos[message.chat.id] = CHOICE
        bot.send_message(message.chat.id, 'Ok. I will replace ad.')
        bot.send_message(message.chat.id, 'Choice the ad that you want to replace (type ad\'s id).')
    else:
        ad_creating_pos[message.chat.id] = DESCRIPTION
        bot.send_message(message.chat.id, 'Ok. I will create a new ad')
        bot.send_message(message.chat.id, 'Describe the object')


@bot.message_handler(func=lambda message: ad_creating_pos[message.chat.id] == CHOICE)
def choicing_ad(message):
    if validate_price(message):
        flag[message.chat.id] = int(message.text)
        ad_creating_pos[message.chat.id] = DESCRIPTION
        bot.send_message(message.chat.id, 'Describe the object')


@bot.message_handler(func=lambda message: ad_creating_pos[message.chat.id] == DESCRIPTION)
def description_ad(message):
    if validate_description(message):
        bot.send_message(message.chat.id, 'Set your price')
        cash_dict[message.chat.id]['DESCRIPTION'] = message.text
        ad_creating_pos[message.chat.id] = PRICE


@bot.message_handler(func=lambda message: ad_creating_pos[message.chat.id] == PRICE)
def description_ad(message):
    if validate_price(message):
        cash_dict[message.chat.id]['PRICE'] = message.text
        ad_creating_pos[message.chat.id] = STOP
        if flag[message.chat.id]:
            replacing_ad(message, flag[message.chat.id])
        else:
            place_ad(message.chat.id)
        flag[message.chat.id] = None


@bot.message_handler(commands=['del', 'remove'])
def delete_start(message):
    ads = session.query(Ad).filter(Ad.made_by == message.chat.id)
    if ads:
        for ad in ads:
            bot.send_message(message.chat.id, 'Ad\'s id:\t{}.\nObject:\t{}.\nDescription:\t{}.\nPrice:\t{}.'.format(
                ad.id, ad.obj, ad.description, ad.price))
        bot.send_message(
            message.chat.id, 'What ad do u want to delete. Use Ad\'s id(example:\'125 321 124\')')
        delete_pos = DELETING

    else:
        bot.send_message(message.chat.id, 'You have no ads.')


@bot.message_handler(func=lambda message: delete_pos[message.chat.id] == DELETING)
def deleting_message(message):
    delete_ad(message)
    delete_pos = STOP


@bot.message_handler(commands=['myads'])
def my_ads(message):
    ads = session.query(Ad).filter(Ad.made_by == message.chat.id)
    if ads:
        for ad in ads:
            bot.send_message(message.chat.id, 'Ad\'s id:\t{}.\nObject:\t{}.\nDescription:\t{}.\nPrice:\t{}.'.format(
                ad.id, ad.obj, ad.description, ad.price))
    else:
        bot.send_message(message.chat.id, 'You have no ads.')


@bot.message_handler()
def hello_message(message):
    bot.send_message(
        message.chat.id, 'You can get my help. Jast use command /help.\n')


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=123)
