## Как написать tg-bot, выдающий оценки из ведомости ##

#### Давайте опишем простым языком идею, которую мы хотим реализовать: #
<br>

Есть ведомость с оценками за курс по Питону. На двух листах содержатся оценки, как за отдельные элементы контроля, так и посчитанные по формулам.<br>

Есть две группы студентов, которым бы хотелось быстро и просто узнавать свои баллы (не все, а ключевые - средняя, за Кр, итоговая), не заходя в ведомость.<br>

Мы хотим сделать Бота, который по введенным "Фамилии и имени" выдавал бы оценки.<br>
<br>

Чтобы это реализовать, мы будем использовать библиотеку pandas для работы с данными из Excel и библиотеку telebot для взаимодействия с Telegram API.<br>

<br>
Начнем разбираться по пунктам и увидим, что главное в создании бота понять две вещи:<br>

1. Что мы хотим получить.
2. Как это реализовать.
<br>

### Пункт 1. Импортируем библиотеки

```import telebot<br>
import pandas as pd
```

<br>

telebot: это библиотека для работы с Telegram Bot API, которая позволяет создавать ботов для Telegram.
pandas: это библиотека для работы с данными, которая предоставляет структуры данных и функции для анализа данных. В данном случае мы используем ее для работы с Excel-файлом.
<br>

### Пункт 2. Создаем бота.

Сразу важное отступление!
Чтобы создать собственного бота нам нужен бот.
[@BotFather](https://t.me/BotFather) отлично в этом поможет. Парой команд мы получаем наш Bot API, называем его, выбираем картиночку, добавляем описание и прочее. И вот потом имеем строчку, свяживающую наш последующий код с тем ботом, который оживет и реально начнет работать.
Прописываем нашего бота, где много букв и цифр - этот токен используется для доступа к HTTP API и взаимодействия с телеграмом.
bot = telebot.TeleBot('4834753573-sbjgbygbajgevaarv - и что-то подобное -сюда вы пишете свой токен')
<br>

### Пункт 3. Про данные.<br>

Создаем словарь для хранения данных пользователей.

> user_data = {}
<br>

Поскольку у нас есть таблица в Excel, в которой указаны данные по двум группам, имеются два листа с названиями "Чистмат" и "Совбак".<br>
Мы хотим создать функцию, которая загружает данные из Excel-файла в зависимости от выбранного отделения (Чистмат или Совбак). Она использует pandas.read_excel для чтения данных из указанного листа.<br>

def load_data(department):
    sheet_name = 'Чистмат' if department == 'Чистмат' else 'Совбак'
    return pd.read_excel('Ведомость (Python, матфак).xlsx', sheet_name=sheet_name)
<br>

### Пункт 4. Начинаем.<br>

Пропишем обработчик, который сработает, когда пользователь отправит команду /start. Он отправляет приветственное сообщение и инициализирует словарь для хранения данных пользователя.<br>

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Если хочешь узнать оценки по Питону, напиши пожалуйста, ты Чистмат или Совбак?")
    user_data[message.chat.id] = {}
<br>

### Пункт 5. Выбираем группу - Чистмат или Совбак.<br>

Наш бот узнает, к какой группе относится студент, сохраняет это значение и загружает соответствующие данные, используя функцию load_data. После этого бот просит пользователя ввести фамилию и имя.<br>
@bot.message_handler(func=lambda message: message.text.lower() in ['чистмат', 'совбак'])

def get_department(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}

    department = message.text.lower().capitalize()
    user_data[message.chat.id]['department'] = department
    # Это так мы листочек нужный выбираем
    user_data[message.chat.id]['data'] = load_data(department)
    bot.reply_to(message, "Отлично, напиши пожалуйста фамилию и имя.")
<br>

### Пункт 5. Получаем данные из таблицы.<br>

После ввода Фамилии и имени в загруженной таблице ищем данные студента с помощью метода str.contains, который проверяет, содержится ли введенная строка в столбце 'ФИО'.<br>
Еще пропишем такое: в случае ошибки (например, если данные не загружены) бот отправляет сообщение об ошибке.<br>
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'data' in user_data[message.chat.id])
def get_grades(message):
    fio = message.text.strip()
    data = user_data[message.chat.id]['data']
    
    try:
        student_data = data[data['ФИО'].str.contains(fio, case=False, na=False)]
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
        return
<br>

### Пункт 6. Ответ от бота, делаем его красивым.<br>

Если данные студента найдены, бот формирует ответ, используя цикл for для перебора строк с данными студента. Он проверяет, есть ли оценки, и округляет их до двух знаков после запятой.<br>
Добавим такое условие для автоматов: Если итоговая оценка равна 8.0, добавляется сообщение о перезачете.<br>
И соответственно условие: если данные не найдены, бот отправляет сообщение о том, что студент не найден.<br>

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
<br>

### Пункт*<br>

Мне хотелось, чтобы бот был добрее и дружелюбнее. Кроме данных из таблицы он мог бы выдать что-то хорошее, поэтому я прописала следующие строки.<br>
Они отправляются в отдельных сообщениях сразу после сообщения с результатами.<br>

        bot.reply_to(message, "Желаю тебе отлично сдать проект, экзамен и просто выучить Питон!")
        bot.reply_to(message, "Если узнать еще чьи-то оценки, то напиши, этот человек Чистмат или Совбак?")
    else:
        bot.reply_to(message, "Студент с такой фамилией не найден.")
<br>

### Пункт 7. Для всяких неожиданностей.<br>

Чтобы сработать относительно правильно при не совсем ясном ответе, мы пропишем условие, которое позволит задать первоначальный вопрос в случае путаницы.<br>
@bot.message_handler(func=lambda message: True)
def handle_unexpected_message(message):
    if message.chat.id not in user_data:
        bot.reply_to(message, "Привет! Если хочешь узнать оценки по Питону, напиши пожалуйста, ты Чистмат или Совбак?")
    else:
        bot.reply_to(message, "Пожалуйста, напиши фамилию и имя.")
<br>

### Пункт 8. Две строки или как заставить всё работать.<br>

Эта конструкция запускает бота и позволяет ему обрабатывать входящие сообщения в режиме реального времени, а метод polling постоянно проверяет наличие новых сообщений.
if __name__ == '__main__':
    bot.polling()
<br>
Вот так, в 8 шагов мы создали телеграм бота, который из большой общей таблицы находит нужные данные и отправляет пользователю.<br>

### Пример диалога с ботом:
<br>
MathFacPython_marks:
Привет! Если хочешь узнать оценки по Питону, напиши пожалуйста, ты Чистмат или Совбак?
<br>
Софья:
Чистмат
<br>
MathFacPython_mark:
Отлично, напиши пожалуйста фамилию и имя.
<br>
Софья:
Шатов Савва
<br>
MathFacPython_marks:<br>
ФИО: Шатов Савва Глебович<br>
Средняя за ДЗ: 8.5<br>
Средняя за СР: 8.79<br>
Контрольная: 7.5<br>
Проект: балл пока не стоит<br>
Экзамен: балл пока не стоит<br>
Итоговая: 4.11<br>
<br>
MathFacPython_marks:
Желаю тебе отлично сдать проект, экзамен и просто выучить Питон!
<br>
MathFacPython_marks:
Если узнать еще чьи-то оценки, то напиши, этот человек Чистмат или Совбак?
