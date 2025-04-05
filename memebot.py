#import PIL.Image
from telebot import types
import random
import datetime
from datetime import date
import os
import pandas as pd
import fnmatch
#from ascii_converter import convert_to_ascii, save_ascii_to_jpeg
from randjoke_generator import get_randomjoke
from token_for_bot import bot
from mongodata import  mongo_collections

def find(pattern, path):
    result = []
    for root, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def create_usertask_file(path_to_user_data):
    usertask_file = open(path_to_user_data, 'w+')
    usertask_file.write('')
    usertask_file.close

def init_userdata(message):
    path_to_user_data = f'usertasks//{message.from_user.id}.csv'
    find_result = find(f'{message.chat.id}.csv', 'usertasks')
    if find_result == []:
        create_usertask_file(path_to_user_data)
    return path_to_user_data

@bot.message_handler(commands=['start', 'hello', 'привет'])
def send_greets(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_help = types.KeyboardButton('Меню действий')
    button_greet = types.KeyboardButton('Поздороваться')
    markup.add(button_greet, button_help)

    user = mongo_collections.find_one({'_id' : message.from_user.id})
    if user:
        print(f'id пользователя найден: {message.from_user.id}')
    else:
        mongo_collections.insert_one({"_id" : message.from_user.id, "name":message.from_user.username, 'first_name':message.from_user.first_name, 'last_name':message.from_user.last_name})
        print("Пользователь с таким ID не найден, добавляю")

    bot.reply_to(message, f'Привет, {message.from_user.first_name}!\n')
    bot.reply_to(message, 'Давай взаимодействовать?\n'
    '\nЧтобы узнать мой список команд, напиши в чат /help\n', reply_markup = markup)

#Обработчики reply-кнопок
@bot.message_handler(content_types = ['text'])
def reply_buttons_handler(message):
    greet_tokens = ['привет', 'Привет', 'прив', 'Прив', 'Ку', 'ку', 'Здарова', 'здарова', 'Здаров', 'здаров', 'q', 'Q']
    if (message.text in greet_tokens) : send_greets(message)
    elif (message.text == 'Вернуться в предыдущее меню') : send_greets(message)
    #main menu
    elif(message.text == 'Поздороваться') : send_greets(message)
    elif(message.text == 'Меню действий' or message.text == '/help') : send_help(message)
    #actions menu
    elif(message.text == 'Случайное число' or message.text == '/rand') : send_rand(message)
    elif(message.text == 'ASCII-арты' or message.text == '/ascii' or message.text == 'Вернуться в меню ascii-артов') : send_ascii_art(message)
    elif(message.text == 'Случайный мем' or message.text == '/mem') : send_meme(message)
    elif(message.text == 'Посмотеть видос' or message.text == '/dunk') : send_dunk(message)
    elif(message.text == 'Менеджер задач' or message.text == '/task') : send_taskmgmt(message)
    #device manager main menu
    elif(message.text == 'Создать задачу') : add_task(message)
    elif(message.text == 'Посмотреть мои задачи') : view_alltasks(message)
    elif(message.text == 'Отменить задачу') : delete_tasks_menu(message)
    elif(message.text == 'Вернуться в меню действий') : send_help(message)
    #remove tasks
    elif(message.text == 'Удалить задачу по номеру') : remove_task_byid(message)
    elif(message.text == 'Очистить список задач') : remove_alltasks(message)
    elif(message.text == 'Вернуться в меню управления задачами') : send_taskmgmt(message)
    #ascii-arts-generator
    elif(message.text == 'UwU') : print_basic_ascii(message)
    #elif(message.text == 'ASCII-генератор') : init_ascii_generator(message)

def remove_alltasks(message):
    path_to_user_data = init_userdata(message)
    if os.path.getsize(path_to_user_data) == 0 : 
        bot.send_message(message.chat.id, 'Вам нечего удалять, т.к. список дел пуст.')
    else :
        csvfile = open(path_to_user_data, 'w+')
        csvfile.close()
        bot.send_message(message.chat.id, 'Ваш список дел очищен!')
    send_taskmgmt(message)
    
def get_taskid_to_remove(message):
    user_input = message.text

    try :
        user_input = int(user_input)
    except :
        bot.send_message(message.chat.id, 'Введите корректный номер задачи!') 
        send_taskmgmt(message)
        return
    
    path_to_userdata = init_userdata(message)
    print(path_to_userdata)

    df = pd.read_csv(path_to_userdata, encoding = 'utf-8', sep = ',', header = None) 
    if user_input <= len(df) and user_input > 0:
        df.drop(df.index[user_input - 1], inplace = True)
        df.to_csv(path_to_userdata, encoding = 'utf-8', sep = ',', header = None, index = False)
        bot.send_message(message.chat.id, f'Задача "{user_input}" была удалена!')
    elif user_input > len(df) or user_input <= 0:
        bot.send_message(message.chat.id, 'Введите корректный номер задачи из списка!')
    else:
        bot.send_message(message.chat.id, 'Ой, что-то пошло не так =С')
    send_taskmgmt(message)

    

@bot.message_handler(content_types = ['text'])
def remove_task_byid(message):

    path_to_userdata = init_userdata(message)
    print(path_to_userdata)

    if os.path.getsize(path_to_userdata) == 0 : 
        bot.send_message(message.chat.id, 'Список задач пуст, нечего удалять.')
        send_taskmgmt(message)
    user_message = bot.send_message(message.chat.id, 'Введите номер задачи для ее удаления')
    bot.register_next_step_handler(user_message, get_taskid_to_remove)


@bot.message_handler(content_types = ['text'])
def delete_tasks_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_remove_task_byid = types.KeyboardButton('Удалить задачу по номеру')
    button_remove_alltasks = types.KeyboardButton('Очистить список задач')
    button_upto_taskmenu = types.KeyboardButton('Вернуться в меню управления задачами')
    markup.add(button_remove_task_byid, button_remove_alltasks, button_upto_taskmenu)
    bot.send_message(message.chat.id, 'Выберите, что будем делать с задачами:', reply_markup = markup)

@bot.message_handler(content_types = ['text'])
def view_alltasks(message):
    path_to_userdata = init_userdata(message)
    print(path_to_userdata)
    with open(path_to_userdata, 'r', encoding = 'utf-8') as csvfile:
        listed = tuple(csvfile)
        if os.path.getsize(path_to_userdata) != 0:
            index = 0
            for row in listed : 
                index += 1
                bot.send_message(message.chat.id, f'{index}. {row}')
        else : 
            bot.send_message(message.chat.id, 'Ваш список задач пуст.')
            bot.send_message(message.chat.id, 'Создайте задачу, чтобы внести ее в список')


#Добавление задачи в список
def push_task(message):
    unformatted_current_time = datetime.datetime.now().time()
    unformatted_current_date = datetime.datetime.now().date()
    ftime = unformatted_current_time.strftime("%H:%M:%S")
    fdate = unformatted_current_date.strftime("%d-%m-%Y")

    user_input = message.text
    bot.send_message(message.chat.id, user_input)

    path_to_user_data = init_userdata(message)
    print(path_to_user_data)

    with open(path_to_user_data, 'a', encoding = 'utf-8') as csvfile:
        csvfile.write(f'{user_input}, создано {fdate} {ftime}\n')
    bot.send_message(message.chat.id, f'Ваша задача "{user_input}" была записана!')
    send_taskmgmt(message)

@bot.message_handler(content_types = ['text'])
def add_task(message):
    markup = types.ReplyKeyboardRemove()
    user_message = bot.send_message(message.chat.id, 'Отправьте, что вы хотите сделать', reply_markup = markup)
    bot.register_next_step_handler(user_message, push_task)

@bot.message_handler(content_types= ['text'])
def send_taskmgmt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_add_task = types.KeyboardButton('Создать задачу')
    button_view_alltasks = types.KeyboardButton('Посмотреть мои задачи')
    button_remove_task = types.KeyboardButton('Отменить задачу')
    button_goto_help = types.KeyboardButton('Вернуться в меню действий')
    markup.add(button_add_task, button_view_alltasks, button_remove_task, button_goto_help)
    bot.reply_to(message,'Добро пожаловать в диспетчер задач! Что хотите сделать?', reply_markup = markup)

@bot.message_handler(func = lambda message : True, commands = ['rand'])
def send_rand(message):
    randint = random.randint(0, 100)
    bot.reply_to(message, randint)

@bot.message_handler(func = lambda message : True, commands = ['help'])
def send_help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_rand = types.KeyboardButton('Случайное число')
    button_ascii = types.KeyboardButton('ASCII-арты')
    button_mem = types.KeyboardButton('Случайный мем')
    button_dunk = types.KeyboardButton('Посмотеть видос')
    button_up = types.KeyboardButton('Вернуться в предыдущее меню')
    button_task_manager = types.KeyboardButton('Менеджер задач')
    markup.add(button_rand, button_ascii, button_mem, button_dunk, button_up, button_task_manager)
    bot.reply_to(message, 
                 '\n Вот список моих доступных команд:\n'
                 '/start - Приветсвие\n'
                 '/rand - Рандомное число\n'
                 '/ascii - Показать человекам исскусство!\n'
                 '/mem - Показать рандомную смешную картинку\n'
                 '/dunk - Прикольный видос\n'
                 '/task - Менеджер задач\n',
                 reply_markup = markup)
    
def print_basic_ascii(message):
    bot.send_message(message.chat.id, '\n'
    '⡆⣐⢕⢕⢕⢕⢕⢕⢕⢕⠅⢗⢕⢕⢕⢕⢕⢕⢕⠕⠕⢕⢕⢕⢕⢕⢕⢕⢕⢕\n'
    '⢐⢕⢕⢕⢕⢕⣕⢕⢕⠕⠁⢕⢕⢕⢕⢕⢕⢕⢕⠅⡄⢕⢕⢕⢕⢕⢕⢕⢕⢕\n'
    '⢕⢕⢕⢕⢕⠅⢗⢕⠕⣠⠄⣗⢕⢕⠕⢕⢕⢕⠕⢠⣿⠐⢕⢕⢕⠑⢕⢕⠵⢕\n'
    '⢕⢕⢕⢕⠁⢜⠕⢁⣴⣿⡇⢓⢕⢵⢐⢕⢕⠕⢁⣾⢿⣧⠑⢕⢕⠄⢑⢕⠅⢕\n'
    '⢕⢕⠵⢁⠔⢁⣤⣤⣶⣶⣶⡐⣕⢽⠐⢕⠕⣡⣾⣶⣶⣶⣤⡁⢓⢕⠄⢑⢅⢑\n'
    '⠍⣧⠄⣶⣾⣿⣿⣿⣿⣿⣿⣷⣔⢕⢄⢡⣾⣿⣿⣿⣿⣿⣿⣿⣦⡑⢕⢤⠱⢐\n'
    '⢠⢕⠅⣾⣿⠋⢿⣿⣿⣿⠉⣿⣿⣷⣦⣶⣽⣿⣿⠈⣿⣿⣿⣿⠏⢹⣷⣷⡅⢐\n'
    '⣔⢕⢥⢻⣿⡀⠈⠛⠛⠁⢠⣿⣿⣿⣿⣿⣿⣿⣿⡀⠈⠛⠛⠁⠄⣼⣿⣿⡇⢔\n'
    '⢕⢕⢽⢸⢟⢟⢖⢖⢤⣶⡟⢻⣿⡿⠻⣿⣿⡟⢀⣿⣦⢤⢤⢔⢞⢿⢿⣿⠁⢕\n'
    '⢕⢕⠅⣐⢕⢕⢕⢕⢕⣿⣿⡄⠛⢀⣦⠈⠛⢁⣼⣿⢗⢕⢕⢕⢕⢕⢕⡏⣘⢕\n'
    '⢕⢕⠅⢓⣕⣕⣕⣕⣵⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣷⣕⢕⢕⢕⢕⡵⢀⢕⢕\n'
    '⢑⢕⠃⡈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⢕⢕⢕\n'
    '⣆⢕⠄⢱⣄⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢁⢕⢕⠕⢁\n'
    '⣿⣦⡀⣿⣿⣷⣶⣬⣍⣛⣛⣛⡛⠿⠿⠿⠛⠛⢛⣛⣉⣭⣤⣂⢜⠕⢑⣡⣴⣿\n')
    bot.send_message(message.chat.id, 'Вот, что я называю исскусство =)')


# @bot.message_handler(content_types = ['photo', 'text'])
# def get_image_from_chat(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     button_up_to_ascii_menu = types.KeyboardButton('Вернуться в меню ascii-артов')
#     markup.add(button_up_to_ascii_menu)
#     #get file
#     file_info = bot.get_file(message.photo[-1].file_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#     #saving file
#     image_file = str(file_info.file_path)
#     ascii_txt_path = 'ascii_txt/' + image_file.split('/')[1].split('.')[0] + str('.txt')
#     with open(image_file, 'wb') as new_file:
#         new_file.write(downloaded_file)
#         if os.path.getsize(image_file) != 0 : 
#             bot.send_message(message.chat.id, 'Файл успешно сохранен!')
#             ascii_image = convert_to_ascii(PIL.Image.open(image_file))
#             print(str(ascii_image))
#             with open(ascii_txt_path, 'w') as ascii_txt_file:
#                 ascii_txt_file.write(ascii_image)
#             bot.send_message(message.chat.id, 'Вот ваш файл с артом :')
#             bot.send_document(message.chat.id, open(ascii_txt_path))
#             save_ascii_to_jpeg(ascii_text = ascii_image)
#         else :
#             bot.send_message(message.chat.id, 'Не удалось обработать изображение, попробуйте другую картинку')
#     send_greets(message)
#     return

# @bot.message_handler(content_types = ['text'])
# def init_ascii_generator(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     button_up_to_ascii_menu = types.KeyboardButton('Вернуться в меню ascii-артов')
#     markup.add(button_up_to_ascii_menu)
#     bot.send_message(message.chat.id, 'Отправтьте мне картинку, чтобы сделать из нее ASCII-арт', reply_markup = markup)
    

@bot.message_handler(content_types = ['text'])
def send_ascii_art(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_send_basic_ascii = types.KeyboardButton('UwU')
    #button_convert_jpeg_to_ascii = types.KeyboardButton('ASCII-генератор')
    button_up = types.KeyboardButton('Вернуться в меню действий')
    markup.add(button_send_basic_ascii, button_up)
    bot.send_message(message.chat.id, 'Выберите желаемое действие', reply_markup = markup)

@bot.message_handler(func = lambda message : True, commands = ['mem'])
def send_meme(message):
    bot.send_photo(message.chat.id, f'https://picsum.photos/1920/1080?random={random.randint(0, 50000000000)}')
    bot.send_message(message.chat.id, get_randomjoke())

@bot.message_handler(func = lambda message : True, commands = ['dunk'])
def send_dunk(message):
    bot.send_message(message.chat.id, 'https://www.youtube.com/watch?v=zecnwqXe850')

bot.infinity_polling()