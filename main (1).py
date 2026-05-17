import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import os
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8950813262:AAFnK3fBo3dH2VLsJkT6gCWBGPUM3G_3TyA"
ADMIN_IDS = [8093996396]
MANAGER_USERNAME = "@lnea_dsgn"
PAYMENT_DETAILS = "2204321185303872 Озон Банк"
PORTFOLIO_LINK = "https://t.me/enproject1"

bot = telebot.TeleBot(BOT_TOKEN)

# ========== БАЗА ДАННЫХ ==========
DB_FILE = 'studio_bot.db'

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("🗑️ Старая база данных удалена")


def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            start_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            question1 TEXT,
            question2 TEXT,
            question3 TEXT,
            full_brief TEXT,
            status TEXT DEFAULT 'Новый',
            payment_status TEXT DEFAULT 'Не оплачен',
            paid_check TEXT,
            created_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price INTEGER
        )
    ''')

    for admin_id in ADMIN_IDS:
        cursor.execute('INSERT OR IGNORE INTO admins (user_id, username) VALUES (?, ?)', (admin_id, "Главный админ"))

    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        test_products = [
            ("Логотип", "Разработка уникального логотипа", 5000),
            ("Фирменный стиль", "Полный пакет: логотип, цвета, шрифты", 25000),
            ("Дизайн упаковки", "Разработка дизайна упаковки", 15000),
            ("Сайт-визитка", "Адаптивный лендинг с уникальным дизайном", 30000)
        ]
        for name, desc, price in test_products:
            cursor.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)', (name, desc, price))

    conn.commit()
    conn.close()
    print("✅ База данных создана")


init_db()


# ========== ФУНКЦИИ БД ==========
def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def is_admin(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None or user_id in ADMIN_IDS


def add_admin(admin_id, username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO admins (user_id, username) VALUES (?, ?)', (admin_id, username))
    conn.commit()
    conn.close()


def remove_admin(admin_id):
    if admin_id in ADMIN_IDS:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
    conn.commit()
    conn.close()
    return True


def get_all_admins():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username FROM admins')
    admins = cursor.fetchall()
    conn.close()
    return admins


def add_user(user_id, username, first_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, start_date) VALUES (?, ?, ?, ?)',
                   (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, first_name FROM users')
    return cursor.fetchall()


def save_order(user_id, username, q1, q2, q3, full_brief):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, username, question1, question2, question3, full_brief, status, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, q1, q2, q3, full_brief, 'Новый', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT order_id, user_id, username, full_brief, status, payment_status FROM orders ORDER BY order_id DESC')
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_order_by_id(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT order_id, user_id, username, question1, question2, question3, full_brief, status, payment_status, paid_check FROM orders WHERE order_id = ?',
        (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order


def update_order_status(order_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
    conn.commit()
    conn.close()


def update_order_payment_status(order_id, payment_status, check_text=None):
    conn = get_db()
    cursor = conn.cursor()
    if check_text:
        cursor.execute('UPDATE orders SET payment_status = ?, paid_check = ? WHERE order_id = ?',
                       (payment_status, check_text, order_id))
    else:
        cursor.execute('UPDATE orders SET payment_status = ? WHERE order_id = ?', (payment_status, order_id))
    conn.commit()
    conn.close()


def delete_order(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT product_id, name, description, price FROM products ORDER BY product_id DESC')
    products = cursor.fetchall()
    conn.close()
    return products


def add_product(name, description, price):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)', (name, description, price))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()


def get_product_by_id(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT product_id, name, description, price FROM products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product


def update_payment_details(new_details):
    global PAYMENT_DETAILS
    PAYMENT_DETAILS = new_details


# ========== КЛАВИАТУРЫ ==========
def main_menu_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💼 Портфолио", url=PORTFOLIO_LINK),
        InlineKeyboardButton("🛍️ Товары", callback_data="show_products"),
        InlineKeyboardButton("📝 Оставить заявку", callback_data="start_survey"),
        InlineKeyboardButton("👤 Связь с менеджером", url=f"https://t.me/{MANAGER_USERNAME.replace('@', '')}")
    )
    if is_admin(user_id):
        keyboard.add(InlineKeyboardButton("🔧 Админ-панель", callback_data="admin_panel"))
    return keyboard


def admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📋 Заказы", callback_data="admin_orders"),
        InlineKeyboardButton("🛍️ Товары", callback_data="admin_products"),
        InlineKeyboardButton("➕ Добавить админа", callback_data="admin_add"),
        InlineKeyboardButton("➖ Удалить админа", callback_data="admin_remove"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("💰 Реквизиты", callback_data="admin_payment"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")
    )
    return keyboard


def products_management_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ Добавить товар", callback_data="admin_add_product"),
        InlineKeyboardButton("❌ Удалить товар", callback_data="admin_remove_product"),
        InlineKeyboardButton("📋 Список товаров", callback_data="admin_list_products"),
        InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")
    )
    return keyboard


def products_for_users_keyboard():
    products = get_all_products()
    keyboard = InlineKeyboardMarkup(row_width=1)

    if products:
        for product in products:
            product_id, name, desc, price = product
            keyboard.add(InlineKeyboardButton(f"{name} - {price}₽", callback_data=f"buy_{product_id}"))
    else:
        keyboard.add(InlineKeyboardButton("📭 Товаров пока нет", callback_data="no_action"))

    keyboard.add(InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"))
    return keyboard


def order_detail_keyboard(order_id, current_status):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if current_status != "В работе":
        keyboard.add(InlineKeyboardButton("➡️ В работу", callback_data=f"status_{order_id}_В работу"))
    if current_status != "Ожидание оплаты":
        keyboard.add(InlineKeyboardButton("➡️ Ожидание оплаты", callback_data=f"status_{order_id}_Ожидание оплаты"))
    if current_status != "Завершен":
        keyboard.add(InlineKeyboardButton("➡️ Завершен", callback_data=f"status_{order_id}_Завершен"))

    keyboard.add(InlineKeyboardButton("✏️ Написать клиенту", callback_data=f"msg_user_{order_id}"))
    keyboard.add(InlineKeyboardButton("❌ Удалить заказ", callback_data=f"del_order_{order_id}"))

    if current_status == "Ожидание оплаты":
        keyboard.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_payment_{order_id}"))

    keyboard.add(InlineKeyboardButton("⬅️ Назад к списку", callback_data="admin_orders"))
    return keyboard


def payment_keyboard(order_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{order_id}"),
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return keyboard


def back_to_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("⬅️ Назад в админ-панель", callback_data="admin_panel"))
    return keyboard


# ========== ОПРОС ==========
user_survey_data = {}


def start_survey(user_id, chat_id, message_id=None):
    user_survey_data[user_id] = {}
    text = "📝 Пожалуйста напишите ваше техническое задание:"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_to_menu_keyboard())
    else:
        bot.send_message(chat_id, text, reply_markup=back_to_menu_keyboard())

    bot.register_next_step_handler_by_chat_id(chat_id, process_survey_step1)


def back_to_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("⬅️ Отмена и назад в меню", callback_data="back_to_menu"))
    return keyboard


def process_survey_step1(message):
    if message.text == "⬅️ Отмена и назад в меню":
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_keyboard(message.from_user.id))
        return
    user_id = message.from_user.id
    user_survey_data[user_id]["q1"] = message.text
    text = "🎨 Записал, а какие цвета хотите видеть в проекте?"
    bot.send_message(message.chat.id, text, reply_markup=back_to_menu_keyboard())
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_survey_step2)


def process_survey_step2(message):
    if message.text == "⬅️ Отмена и назад в меню":
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_keyboard(message.from_user.id))
        return
    user_id = message.from_user.id
    user_survey_data[user_id]["q2"] = message.text
    text = "✨ Хорошо, есть какие нибудь пожелания?"
    bot.send_message(message.chat.id, text, reply_markup=back_to_menu_keyboard())
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_survey_step3)


def process_survey_step3(message):
    if message.text == "⬅️ Отмена и назад в меню":
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_keyboard(message.from_user.id))
        return
    user_id = message.from_user.id
    q1 = user_survey_data[user_id]["q1"]
    q2 = user_survey_data[user_id]["q2"]
    q3 = message.text

    username = message.from_user.username or f"user{user_id}"
    full_name = message.from_user.first_name or ""

    bot.send_message(message.chat.id, "✅ Спасибо за опрос мы направили сообщение дизайнеру.",
                     reply_markup=main_menu_keyboard(user_id))

    admin_text = f"""
╔══════════════════════════════════════════════╗
║              🆕 НОВАЯ ЗАЯВКА                 ║
╠══════════════════════════════════════════════╣
║ 👤 Username: @{username}
║ 👤 Имя: {full_name}
║ 🆔 ID: {user_id}
╠══════════════════════════════════════════════╣
║ 📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ:
║ {q1}
╠══════════════════════════════════════════════╣
║ 🎨 ЦВЕТА:
║ {q2}
╠══════════════════════════════════════════════╣
║ ✨ ПОЖЕЛАНИЯ:
║ {q3}
╚══════════════════════════════════════════════╝
    """

    full_brief = f"ТЗ: {q1}\nЦвета: {q2}\nПожелания: {q3}"
    order_id = save_order(user_id, username, q1, q2, q3, full_brief)

    admins = get_all_admins()
    for admin_id, admin_username in admins:
        try:
            bot.send_message(admin_id, admin_text, reply_markup=order_detail_keyboard(order_id, "Новый"))
        except Exception as e:
            print(f"Не удалось отправить админу {admin_id}: {e}")

    del user_survey_data[user_id]


# ========== ОПЛАТА ==========
def process_check(message, order_id):
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"

    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        update_order_payment_status(order_id, "Чек на проверке", file_id)

        for admin_id, _ in get_all_admins():
            try:
                bot.send_photo(admin_id, file_id,
                               caption=f"🧾 НОВЫЙ ЧЕК ДЛЯ ЗАКАЗА #{order_id}\n👤 @{username}")
                bot.send_message(admin_id, f"Проверьте чек и подтвердите оплату в админ-панели.")
            except:
                pass

        bot.send_message(message.chat.id, "✅ Спасибо! Ваш чек отправлен на проверку.",
                         reply_markup=main_menu_keyboard(user_id))
    else:
        bot.send_message(message.chat.id, "❌ Отправьте ФОТО чека")
        bot.register_next_step_handler_by_chat_id(message.chat.id, lambda msg: process_check(msg, order_id))


def confirm_payment(order_id, admin_id):
    update_order_payment_status(order_id, "Оплачено")
    order = get_order_by_id(order_id)
    if order:
        bot.send_message(order[1], "✅ Ваша оплата подтверждена! Дизайнер приступит к работе.",
                         reply_markup=main_menu_keyboard(order[1]))
    bot.send_message(admin_id, f"✅ Оплата по заказу #{order_id} подтверждена!")


# ========== ТОВАРЫ ==========
def show_products_to_user(chat_id, message_id=None):
    products = get_all_products()

    if not products:
        text = "📭 В данный момент товаров нет.\n\nОставьте заявку через кнопку «Оставить заявку»"
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=products_for_users_keyboard())
        else:
            bot.send_message(chat_id, text, reply_markup=products_for_users_keyboard())
        return

    text = "🛍️ Наши товары и услуги:\n\n"
    for product in products:
        product_id, name, desc, price = product
        text += f"━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📦 {name}\n"
        text += f"📝 {desc}\n"
        text += f"💰 Цена: {price}₽\n\n"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=products_for_users_keyboard())
    else:
        bot.send_message(chat_id, text, reply_markup=products_for_users_keyboard())


def buy_product(product_id, user_id, username, chat_id):
    product = get_product_by_id(product_id)
    if not product:
        bot.send_message(chat_id, "❌ Товар не найден", reply_markup=back_to_menu_keyboard())
        return

    prod_id, name, desc, price = product
    full_brief = f"Товар: {name}\nОписание: {desc}\nЦена: {price}₽"
    order_id = save_order(user_id, username, f"Заказ товара: {name}", desc, str(price), full_brief)
    update_order_status(order_id, "Ожидание оплаты")

    text = f"""🛒 ВЫ ВЫБРАЛИ: {name}

📝 {desc}

💰 Сумма к оплате: {price}₽

💳 Реквизиты для оплаты:
{PAYMENT_DETAILS}

После оплаты нажмите кнопку «Я оплатил» и отправьте чек."""

    bot.send_message(chat_id, text, reply_markup=payment_keyboard(order_id))

    for admin_id, _ in get_all_admins():
        try:
            bot.send_message(admin_id, f"🆕 НОВЫЙ ЗАКАЗ ТОВАРА #{order_id}\n👤 @{username}\n\n{full_brief}",
                             reply_markup=order_detail_keyboard(order_id, "Ожидание оплаты"))
        except:
            pass


# ========== CALLBACKИ ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    print(f"🔘 Нажата кнопка: {data}")

    if data == "back_to_menu":
        bot.edit_message_text("Главное меню:", call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_keyboard(user_id))
        bot.answer_callback_query(call.id)
        return

    elif data == "show_products":
        show_products_to_user(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("buy_"):
        product_id = int(data.split("_")[1])
        username = call.from_user.username or f"user{user_id}"
        buy_product(product_id, user_id, username, call.message.chat.id)
        bot.answer_callback_query(call.id)
        return

    elif data == "start_survey":
        start_survey(user_id, call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ Доступ запрещен!")
            return
        bot.edit_message_text("🔧 Админ-панель:", call.message.chat.id, call.message.message_id,
                              reply_markup=admin_panel_keyboard())
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_orders":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ Доступ запрещен!")
            return

        orders = get_orders()

        if not orders:
            bot.edit_message_text("📭 Заказов пока нет", call.message.chat.id, call.message.message_id,
                                  reply_markup=back_to_admin_panel_keyboard())
            bot.answer_callback_query(call.id)
            return

        keyboard = InlineKeyboardMarkup(row_width=1)
        for order in orders:
            order_id, uid, username, brief, status, pay_status = order
            keyboard.add(InlineKeyboardButton(f"📌 Заказ #{order_id} | {status} | @{username}",
                                              callback_data=f"view_order_{order_id}"))
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))

        bot.edit_message_text("📋 СПИСОК ЗАКАЗОВ:", call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("view_order_"):
        if not is_admin(user_id):
            return
        order_id = int(data.split("_")[2])
        order = get_order_by_id(order_id)
        if order:
            text = f"""📦 ЗАКАЗ #{order_id}
━━━━━━━━━━━━━━━━━━━━
👤 Клиент: @{order[2]}
📌 Статус: {order[7]}
💳 Оплата: {order[8]}
━━━━━━━━━━━━━━━━━━━━
📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ:
{order[3]}

🎨 ЦВЕТА:
{order[4]}

✨ ПОЖЕЛАНИЯ:
{order[5]}"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                  reply_markup=order_detail_keyboard(order_id, order[7]))
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("status_"):
        if not is_admin(user_id):
            return
        parts = data.split("_")
        order_id = int(parts[1])
        new_status = "_".join(parts[2:])
        update_order_status(order_id, new_status)
        bot.answer_callback_query(call.id, f"✅ Статус: {new_status}")

        order = get_order_by_id(order_id)
        if order:
            text = f"""📦 ЗАКАЗ #{order_id}
━━━━━━━━━━━━━━━━━━━━
👤 Клиент: @{order[2]}
📌 Статус: {new_status}
💳 Оплата: {order[8]}
━━━━━━━━━━━━━━━━━━━━
📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ:
{order[3]}

🎨 ЦВЕТА:
{order[4]}

✨ ПОЖЕЛАНИЯ:
{order[5]}"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                  reply_markup=order_detail_keyboard(order_id, new_status))
        return

    elif data.startswith("msg_user_"):
        if not is_admin(user_id):
            return
        order_id = int(data.split("_")[2])
        order = get_order_by_id(order_id)
        if order:
            msg = bot.send_message(call.message.chat.id, f"✏️ Введите сообщение для @{order[2]}:")
            bot.register_next_step_handler(msg, lambda m: send_to_user(m, order[1], order_id))
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("del_order_"):
        if not is_admin(user_id):
            return
        order_id = int(data.split("_")[2])
        delete_order(order_id)
        bot.answer_callback_query(call.id, "✅ Заказ удален")

        orders = get_orders()
        if not orders:
            bot.edit_message_text("📭 Заказов пока нет", call.message.chat.id, call.message.message_id,
                                  reply_markup=back_to_admin_panel_keyboard())
        else:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for order in orders:
                order_id2, uid, username, brief, status, pay_status = order
                keyboard.add(InlineKeyboardButton(f"📌 Заказ #{order_id2} | {status} | @{username}",
                                                  callback_data=f"view_order_{order_id2}"))
            keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
            bot.edit_message_text("📋 СПИСОК ЗАКАЗОВ:", call.message.chat.id, call.message.message_id,
                                  reply_markup=keyboard)
        return

    elif data.startswith("confirm_payment_"):
        if not is_admin(user_id):
            return
        order_id = int(data.split("_")[2])
        confirm_payment(order_id, call.message.chat.id)
        bot.answer_callback_query(call.id, "✅ Оплата подтверждена")

        order = get_order_by_id(order_id)
        if order:
            text = f"""📦 ЗАКАЗ #{order_id}
━━━━━━━━━━━━━━━━━━━━
👤 Клиент: @{order[2]}
📌 Статус: {order[7]}
💳 Оплата: Оплачено
━━━━━━━━━━━━━━━━━━━━
📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ:
{order[3]}

🎨 ЦВЕТА:
{order[4]}

✨ ПОЖЕЛАНИЯ:
{order[5]}"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                  reply_markup=order_detail_keyboard(order_id, order[7]))
        return

    elif data.startswith("paid_"):
        order_id = int(data.split("_")[1])
        order = get_order_by_id(order_id)
        if order and order[7] == "Ожидание оплаты":
            bot.send_message(call.message.chat.id, "📸 Отправьте ФОТО чека:", reply_markup=back_to_menu_keyboard())
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, lambda msg: process_check(msg, order_id))
        else:
            bot.answer_callback_query(call.id, "❌ Этот заказ нельзя оплатить", show_alert=True)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_products":
        if not is_admin(user_id):
            return
        bot.edit_message_text("🛍️ Управление товарами:", call.message.chat.id, call.message.message_id,
                              reply_markup=products_management_keyboard())
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_add_product":
        if not is_admin(user_id):
            return
        bot.send_message(call.message.chat.id, "Введите НАЗВАНИЕ товара:", reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, add_product_step_name)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_remove_product":
        if not is_admin(user_id):
            return
        products = get_all_products()
        if not products:
            bot.answer_callback_query(call.id, "Нет товаров для удаления")
            return
        keyboard = InlineKeyboardMarkup(row_width=1)
        for p in products:
            keyboard.add(InlineKeyboardButton(f"{p[1]} - {p[3]}₽", callback_data=f"delete_product_{p[0]}"))
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_products"))
        bot.edit_message_text("Выберите товар для удаления:", call.message.chat.id, call.message.message_id,
                              reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_list_products":
        if not is_admin(user_id):
            return
        products = get_all_products()
        if not products:
            text = "📭 В базе нет товаров"
        else:
            text = "📋 СПИСОК ТОВАРОВ:\n\n"
            for p in products:
                text += f"🆔 ID: {p[0]}\n📦 {p[1]}\n📝 {p[2]}\n💰 {p[3]}₽\n━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              reply_markup=products_management_keyboard())
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("delete_product_"):
        if not is_admin(user_id):
            return
        product_id = int(data.split("_")[2])
        delete_product(product_id)
        bot.answer_callback_query(call.id, "✅ Товар удален!")
        bot.edit_message_text("🛍️ Управление товарами:", call.message.chat.id, call.message.message_id,
                              reply_markup=products_management_keyboard())
        return

    elif data == "admin_add":
        if not is_admin(user_id):
            return
        bot.send_message(call.message.chat.id, "👑 Введите Telegram ID нового администратора:",
                         reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_add_admin)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_remove":
        if not is_admin(user_id):
            return
        admins = get_all_admins()
        if len(admins) <= 1:
            bot.send_message(call.message.chat.id, "❌ Нельзя удалить единственного администратора")
            bot.answer_callback_query(call.id)
            return
        keyboard = InlineKeyboardMarkup(row_width=1)
        for admin_id, username in admins:
            if admin_id not in ADMIN_IDS:
                keyboard.add(InlineKeyboardButton(f"@{username or admin_id}", callback_data=f"remove_admin_{admin_id}"))
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
        bot.edit_message_text("Выберите администратора для удаления:", call.message.chat.id, call.message.message_id,
                              reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return

    elif data.startswith("remove_admin_"):
        if not is_admin(user_id):
            return
        target_id = int(data.split("_")[2])
        if remove_admin(target_id):
            bot.answer_callback_query(call.id, "✅ Администратор удален")
            bot.edit_message_text("🔧 Админ-панель:", call.message.chat.id, call.message.message_id,
                                  reply_markup=admin_panel_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Нельзя удалить главного админа!")
        return

    elif data == "admin_broadcast":
        if not is_admin(user_id):
            return
        bot.send_message(call.message.chat.id, "📢 Введите сообщение для рассылки:",
                         reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_broadcast)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_payment":
        if not is_admin(user_id):
            return
        bot.send_message(call.message.chat.id, f"💰 ТЕКУЩИЕ РЕКВИЗИТЫ:\n{PAYMENT_DETAILS}\n\nВведите новые реквизиты:",
                         reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, update_payment_step)
        bot.answer_callback_query(call.id)
        return

    elif data == "no_action":
        bot.answer_callback_query(call.id)
        return

    else:
        print(f"⚠️ Неизвестный callback: {data}")
        bot.answer_callback_query(call.id)


# ========== ДОБАВЛЕНИЕ ТОВАРА ==========
def add_product_step_name(message):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    name = message.text
    bot.send_message(message.chat.id, "Введите ОПИСАНИЕ товара:", reply_markup=back_to_admin_panel_keyboard())
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda m: add_product_step_desc(m, name))


def add_product_step_desc(message, name):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    desc = message.text
    bot.send_message(message.chat.id, "💰 Введите ЦЕНУ (просто число, например 5000):",
                     reply_markup=back_to_admin_panel_keyboard())
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda m: add_product_step_price(m, name, desc))


def add_product_step_price(message, name, desc):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    try:
        price = int(message.text.strip())
        add_product(name, desc, price)
        bot.send_message(message.chat.id, f"✅ Товар '{name}' добавлен! Цена: {price}₽",
                         reply_markup=admin_panel_keyboard())
    except:
        bot.send_message(message.chat.id, "❌ Ошибка! Введите просто число (например 5000)",
                         reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(message.chat.id, lambda m: add_product_step_price(m, name, desc))


# ========== ФУНКЦИИ ДЛЯ АДМИНОВ ==========
def process_add_admin(message):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    try:
        admin_id = int(message.text.strip())
        username = message.from_user.username or str(admin_id)
        add_admin(admin_id, username)
        bot.send_message(message.chat.id, f"✅ Администратор с ID {admin_id} добавлен!",
                         reply_markup=admin_panel_keyboard())
    except:
        bot.send_message(message.chat.id, "❌ Ошибка! Введите корректный Telegram ID (только цифры)",
                         reply_markup=back_to_admin_panel_keyboard())
        bot.register_next_step_handler_by_chat_id(message.chat.id, process_add_admin)


def process_broadcast(message):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    users = get_all_users()
    success = 0
    for user_id, username, name in users:
        try:
            bot.send_message(user_id, f"📢 НОВОСТИ СТУДИИ\n\n{message.text}")
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ Рассылка завершена!\n📤 Отправлено: {success} из {len(users)} пользователей.",
                     reply_markup=admin_panel_keyboard())


def send_to_user(message, target_id, order_id):
    bot.send_message(target_id, f"✉️ СООБЩЕНИЕ ОТ МЕНЕДЖЕРА (заказ #{order_id}):\n\n{message.text}",
                     reply_markup=main_menu_keyboard(target_id))
    bot.send_message(message.chat.id, f"✅ Сообщение отправлено клиенту по заказу #{order_id}!",
                     reply_markup=admin_panel_keyboard())


def update_payment_step(message):
    if message.text == "⬅️ Назад в админ-панель":
        bot.send_message(message.chat.id, "🔧 Админ-панель:", reply_markup=admin_panel_keyboard())
        return
    update_payment_details(message.text)
    bot.send_message(message.chat.id, f"✅ Реквизиты обновлены!\n\nНОВЫЕ РЕКВИЗИТЫ:\n{PAYMENT_DETAILS}",
                     reply_markup=admin_panel_keyboard())


# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"
    first_name = message.from_user.first_name

    add_user(user_id, username, first_name)

    welcome_text = "🎨 Добро пожаловать в дизайн-студию LINEA!\n\nВыберите действие:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard(user_id))


@bot.message_handler(commands=['admin'])
def admin_command(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🔧 Админ-панель", reply_markup=admin_panel_keyboard())
    else:
        bot.send_message(message.chat.id, "⛔ Нет доступа")


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print(f"👑 Главный админ: 8093996396")
    print(f"📁 Портфолио: {PORTFOLIO_LINK}")
    print("=" * 50)

    products = get_all_products()
    print(f"📦 Товаров в базе: {len(products)}")
    for p in products:
        print(f"   - {p[1]}: {p[3]}₽")

    admins = get_all_admins()
    print(f"👑 Администраторов в базе: {len(admins)}")
    for a in admins:
        print(f"   - {a[0]}: {a[1]}")

    bot.infinity_polling()
