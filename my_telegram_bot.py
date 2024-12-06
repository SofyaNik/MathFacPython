import telebot
import pandas as pd

bot = telebot.TeleBot('7725395067:AAG9kVmxkS86xIw-oS1xJDgImwFCdtsN4yw')

user_data = {}


def load_data(department):
    sheet_name = 'Чистмат' if department == 'Чистмат' else 'Совбак'
    return pd.read_excel('Ведомость (Python, матфак).xlsx', sheet_name=sheet_name)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Если хочешь узнать оценки по Питону, напиши пожалуйста, ты Чистмат или Совбак?")
    user_data[message.chat.id] = {}

@bot.message_handler(func=lambda message: message.text.lower() in ['чистмат', 'совбак'])
def get_department(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}

    department = message.text.lower().capitalize()
    user_data[message.chat.id]['department'] = department
    # Это так мы листочек нужный выбираем
    user_data[message.chat.id]['data'] = load_data(department)
    bot.reply_to(message, "Отлично, напиши пожалуйста фамилию и имя.")

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'data' in user_data[message.chat.id])
def get_grades(message):
    fio = message.text.strip()
    data = user_data[message.chat.id]['data']
    
    try:
        student_data = data[data['ФИО'].str.contains(fio, case=False, na=False)]
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
        return

    if not student_data.empty:
        response = ""
        for index, row in student_data.iterrows():
            response += (
                f"ФИО: {row['ФИО']}\n"
                f"Средняя за ДЗ: {round(row['Средняя ДЗ'], 2) if not pd.isna(row['Средняя ДЗ']) else 'балл пока не стоит'}\n"
                f"Средняя за СР: {round(row['Средняя СР'], 2) if not pd.isna(row['Средняя СР']) else 'балл пока не стоит'}\n"
                f"Контрольная: {round(row['КР'], 2) if not pd.isna(row['КР']) else 'балл пока не стоит'}\n"
                f"Проект: {round(row['Проект'], 2) if not pd.isna(row['Проект']) else 'балл пока не стоит'}\n"
                f"Экзамен: {round(row['Экзамен'], 2) if not pd.isna(row['Экзамен']) else 'балл пока не стоит'}\n"
                f"Итоговая: {round(row['Итоговая'], 2) if not pd.isna(row['Итоговая']) else 'балл пока не стоит'}\n\n"
            )
            if not pd.isna(row['Итоговая']) and row['Итоговая'] == 8.0:
                response += "Курс был перезачтён\n\n"
        bot.reply_to(message, response.strip())
        
        bot.reply_to(message, "Желаю тебе отлично сдать проект, экзамен и просто выучить Питон!")
        bot.reply_to(message, "Если узнать еще чьи-то оценки, то напиши, этот человек Чистмат или Совбак?")
    else:
        bot.reply_to(message, "Студент с такой фамилией не найден.")

@bot.message_handler(func=lambda message: True)
def handle_unexpected_message(message):
    if message.chat.id not in user_data:
        bot.reply_to(message, "Привет! Если хочешь узнать оценки по Питону, напиши пожалуйста, ты Чистмат или Совбак?")
    else:
        bot.reply_to(message, "Пожалуйста, напиши фамилию и имя.")

if __name__ == '__main__':
    bot.polling()
