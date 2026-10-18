import telebot
from config import TOKEN, DATABASE
from logic import PasswordManager

bot = telebot.TeleBot(TOKEN)
manager = PasswordManager(DATABASE)

user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    manager.create_table()
    bot.send_message(
        message.chat.id,
        "Привет. Я твой Менеджер паролей.\n\n"
        "Доступные команды:\n"
        "/add - Добавить новый пароль\n"
        "/list - Показать сохранённые сервисы\n"
        "/delete - Удалить запись"
    )


@bot.message_handler(commands=['add'])
def add_password_start(message):
    msg = bot.send_message(message.chat.id, "Введите название сервиса (например, TELEGRAM):")
    bot.register_next_step_handler(msg, process_service)


def process_service(message):
    user_data[message.chat.id] = {'service': message.text}
    msg = bot.send_message(message.chat.id, "Введите ваш логин:")
    bot.register_next_step_handler(msg, process_login)


def process_login(message):
    user_data[message.chat.id]['login'] = message.text
    msg = bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(msg, process_password)


def process_password(message):
    password = message.text
    data = user_data.get(message.chat.id)

    if data:
        manager.add_password(
            message.chat.id,
            data['service'],
            data['login'],
            password
        )

        bot.send_message(
            message.chat.id,
            f"Пароль для {data['service']} успешно сохранён."
        )

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

        user_data.pop(message.chat.id, None)


@bot.message_handler(commands=['list'])
def list_passwords(message):
    passwords = manager.get_passwords(message.chat.id)

    if not passwords:
        bot.send_message(message.chat.id, 'У вас пока нет сохранённых паролей.')
    else:
        response = 'Ваши сервисы:\n\n'

        for service, login in passwords:
            response += f'{service} (login: {login})\n'

        bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['delete'])
def delete_start(message):
    msg = bot.send_message(
        message.chat.id,
        'Введите название сервиса, который хотите удалить:'
    )
    bot.register_next_step_handler(msg, process_delete)


def process_delete(message):
    service = message.text

    if manager.delete_password(message.chat.id, service):
        bot.send_message(message.chat.id, f'Сервис {service} удалён.')
    else:
        bot.send_message(message.chat.id, 'Такой сервис не найден.')


if __name__ == '__main__':
    print('Бот запущен...')
    bot.polling(non_stop=True)