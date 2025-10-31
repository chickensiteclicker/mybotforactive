import telebot
import json
import random
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация
BOT_TOKEN = '8464828448:AAHGVxbd9EA7h4wqbTdZncWrnLmSPQmaNKI'  # Замените на ваш токен
ADMIN_ID = '8218378618'    # Замените на ваш ID

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл для хранения данных
DB_FILE = 'users.json'

# Загрузка данных пользователей
def load_users():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки данных: {e}")
        return {}

# Сохранение данных пользователей
def save_users(users):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения данных: {e}")

# Получение баланса пользователя
def get_user_balance(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get('balance', 100)

# Обновление баланса пользователя
def update_user_balance(user_id, new_balance, username="", first_name=""):
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            'balance': new_balance,
            'username': username,
            'first_name': first_name,
            'joined_date': datetime.now().isoformat()
        }
    else:
        users[user_id_str]['balance'] = new_balance
        if username:
            users[user_id_str]['username'] = username
        if first_name:
            users[user_id_str]['first_name'] = first_name
    
    save_users(users)

# Получение информации о пользователе
def get_user_info(user_id):
    users = load_users()
    return users.get(str(user_id), {})

# Обработчик команды /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_type = message.chat.type
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    
    # Обновляем информацию о пользователе
    update_user_balance(user_id, get_user_balance(user_id), username, first_name)
    
    if chat_type == 'private':
        welcome_text = (
            "👋 <b>Привет, ты попал в бота для актива!</b>\n\n"
            "🤖 Этот бот работает только в группах и чатах.\n"
            "📲 Добавь меня в свой чат, чтобы я начал работать!\n\n"
            "⚙️ После добавления в чат используй команды:\n"
            "🎲 /kasik - Испытать удачу в казино\n"
            "💼 /work - Работать\n"
            "💰 /pay - Перевести деньги\n"
            "📊 /balance - Проверить баланс"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    else:
        welcome_text = (
            "🎰 <b>Casino Bot активирован!</b> 🎰\n\n"
            "Доступные команды:\n"
            "🎲 /kasik - Испытать удачу в казино\n"
            "💼 /work - Работать (таксист, юрист, завод)\n"
            "💰 /pay @username сумма - Перевести деньги\n"
            "📊 /balance - Проверить баланс\n\n"
            "💸 Начальный баланс: <b>100$</b>"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')

# Обработчик команды /kasik
@bot.message_handler(commands=['kasik'])
def kasino_game(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "❌ Бот работает только в группах! Добавь меня в чат.")
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    balance = get_user_balance(user_id)
    
    # Суммы проигрыша
    bet_amounts = [25, 100, 1000]
    lost_amount = random.choice(bet_amounts)
    
    if balance >= lost_amount:
        new_balance = balance - lost_amount
        update_user_balance(user_id, new_balance, username, first_name)
        
        message_text = (
            f"🔴 <b>ВЫ ПРОЕБАЛИ {lost_amount}$ В КАЗИНО</b> 🔴\n"
            f"💳 Ваш баланс: <b>{new_balance}$</b>"
        )
    else:
        message_text = (
            f"❌ <b>Недостаточно средств для игры в казино!</b>\n"
            f"💳 Ваш баланс: <b>{balance}$</b>"
        )
    
    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

# Обработчик команды /work
@bot.message_handler(commands=['work'])
def work_command(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "❌ Бот работает только в группах! Добавь меня в чат.")
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    balance = get_user_balance(user_id)
    
    # Варианты работы
    jobs = ['таксистом', 'юристом', 'на заводе']
    job = random.choice(jobs)
    salary = random.randint(10, 250)
    new_balance = balance + salary
    
    update_user_balance(user_id, new_balance, username, first_name)
    
    message_text = (
        f"💼 <b>Вы поработали {job}</b>\n"
        f"💰 Зарплата: <b>{salary}$</b>\n"
        f"💳 Ваш баланс: <b>{new_balance}$</b>"
    )
    
    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

# Обработчик команды /balance
@bot.message_handler(commands=['balance'])
def balance_command(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "❌ Бот работает только в группах! Добавь меня в чат.")
        return
    
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    message_text = f"💳 <b>Ваш баланс: {balance}$</b>"
    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

# Обработчик команды /pay
@bot.message_handler(commands=['pay'])
def pay_command(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "❌ Бот работает только в группах! Добавь меня в чат.")
        return
    
    try:
        user_id = message.from_user.id
        sender_username = message.from_user.username or ""
        sender_first_name = message.from_user.first_name or ""
        balance = get_user_balance(user_id)
        
        # Парсим команду
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(
                message.chat.id,
                "❌ <b>Неверный формат команды!</b>\n"
                "Используйте: /pay @username сумма\n"
                "Например: /pay @username 100",
                parse_mode='HTML'
            )
            return
        
        target_username = parts[1].replace('@', '')
        amount = int(parts[2])
        
        # Проверки суммы
        if amount < 10:
            bot.send_message(message.chat.id, "❌ <b>Минимальная сумма перевода: 10$</b>", parse_mode='HTML')
            return
        
        if amount > 1200:
            bot.send_message(message.chat.id, "❌ <b>Максимальная сумма перевода: 1200$</b>", parse_mode='HTML')
            return
        
        if balance < amount:
            bot.send_message(message.chat.id, "❌ <b>Недостаточно средств для перевода!</b>", parse_mode='HTML')
            return
        
        # Ищем получателя
        users = load_users()
        target_user_id = None
        
        for uid, user_data in users.items():
            if user_data.get('username') == target_username:
                target_user_id = int(uid)
                break
        
        if not target_user_id:
            bot.send_message(
                message.chat.id, 
                f"❌ <b>Пользователь @{target_username} не найден!</b>", 
                parse_mode='HTML'
            )
            return
        
        if target_user_id == user_id:
            bot.send_message(message.chat.id, "❌ <b>Нельзя переводить самому себе!</b>", parse_mode='HTML')
            return
        
        # Выполняем перевод
        target_balance = get_user_balance(target_user_id)
        new_target_balance = target_balance + amount
        new_sender_balance = balance - amount
        
        # Обновляем балансы
        update_user_balance(target_user_id, new_target_balance)
        update_user_balance(user_id, new_sender_balance, sender_username, sender_first_name)
        
        # Получаем информацию о получателе
        target_info = get_user_info(target_user_id)
        target_name = target_info.get('first_name', target_username)
        sender_name = sender_first_name or sender_username
        
        message_text = (
            f"✅ <b>Перевод выполнен успешно!</b>\n"
            f"👤 От: <b>{sender_name}</b>\n"
            f"👥 Кому: <b>{target_name}</b>\n"
            f"💰 Сумма: <b>{amount}$</b>\n"
            f"💳 Ваш баланс: <b>{new_sender_balance}$</b>"
        )
        
        bot.send_message(message.chat.id, message_text, parse_mode='HTML')
        
        # Уведомляем получателя (если он в этом чате)
        try:
            bot.send_message(
                target_user_id,
                f"💰 <b>Вы получили перевод!</b>\n"
                f"👤 От: <b>{sender_name}</b>\n"
                f"💵 Сумма: <b>{amount}$</b>\n"
                f"💳 Ваш баланс: <b>{new_target_balance}$</b>",
                parse_mode='HTML'
            )
        except:
            pass  # Не можем отправить сообщение пользователю
            
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ <b>Неверная сумма!</b>\n"
            "Убедитесь, что сумма - это число.",
            parse_mode='HTML'
        )
    except Exception as e:
        logging.error(f"Ошибка в переводе: {e}")
        bot.send_message(message.chat.id, "❌ <b>Произошла ошибка при переводе</b>", parse_mode='HTML')

# Обработчик всех сообщений (для логирования)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Логируем активность
    logging.info(f"Сообщение от {message.from_user.id} в чате {message.chat.id}")

# Запуск бота
if __name__ == "__main__":
    logging.info("Бот запущен...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка при работе бота: {e}")
