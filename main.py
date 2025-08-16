import telebot
from telebot import types
import sqlite3
import os
import time
from datetime import datetime

# Bot token
bot = telebot.TeleBot('8075441973:AAGYebdfGR8ldxu55WfkalrLKkpURZ3Ez20')

# Initialize database
def init_db():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    # Movies table
    c.execute('''CREATE TABLE IF NOT EXISTS movies
                 (code TEXT PRIMARY KEY, description TEXT, file_id TEXT)''')
    
    # Channels table
    c.execute('''CREATE TABLE IF NOT EXISTS channels
                 (username TEXT PRIMARY KEY, title TEXT)''')
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, username TEXT, first_name TEXT, 
                  last_name TEXT, joined_date TEXT)''')
    
    # Admins table
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (user_id TEXT PRIMARY KEY, added_by TEXT, added_date TEXT)''')
    
    # Super users table
    c.execute('''CREATE TABLE IF NOT EXISTS super_users
                 (user_id TEXT PRIMARY KEY, added_by TEXT, added_date TEXT)''')
    
    # Add initial admin
    c.execute("INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)",
             ('7445142075', 'system', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

# User management functions
def register_user(user):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_date) VALUES (?, ?, ?, ?, ?)",
                 (str(user.id), user.username, user.first_name, user.last_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    conn.close()

def get_all_users():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, last_name FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

# Admin management functions
def is_admin(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins WHERE user_id = ?", (str(user_id),))
    result = c.fetchone() is not None
    conn.close()
    return result

def add_admin(user_id, added_by):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)",
                 (str(user_id), str(added_by), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def remove_admin(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id = ?", (str(user_id),))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_admins():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT a.user_id, u.username, u.first_name, u.last_name FROM admins a LEFT JOIN users u ON a.user_id = u.user_id")
    admins = c.fetchall()
    conn.close()
    return admins

# Super user management functions
def is_super_user(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM super_users WHERE user_id = ?", (str(user_id),))
    result = c.fetchone() is not None
    conn.close()
    return result

def add_super_user(user_id, added_by):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO super_users (user_id, added_by, added_date) VALUES (?, ?, ?)",
                 (str(user_id), str(added_by), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def remove_super_user(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM super_users WHERE user_id = ?", (str(user_id),))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_super_users():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT s.user_id, u.username, u.first_name, u.last_name FROM super_users s LEFT JOIN users u ON s.user_id = u.user_id")
    super_users = c.fetchall()
    conn.close()
    return super_users

# Channel management functions
def add_channel(username, title):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO channels (username, title) VALUES (?, ?)", (username, title))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def remove_channel(username):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE username = ?", (username,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_channels():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT username, title FROM channels")
    channels = c.fetchall()
    conn.close()
    return channels

# Movie management functions
def add_movie(code, description, file_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO movies (code, description, file_id) VALUES (?, ?, ?)",
                 (code, description, file_id))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def delete_movie_by_code(code):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE code = ?", (code,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_movie_by_code(code):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT description, file_id FROM movies WHERE code = ?", (code,))
    movie = c.fetchone()
    conn.close()
    return movie

# Message broadcasting function
def broadcast_message(message_obj):
    users = get_all_users()
    successful = 0
    failed = 0
    
    for user_id, _, _, _ in users:
        try:
            # Forward the original message
            if message_obj.forward_from or message_obj.forward_from_chat:
                bot.forward_message(user_id, message_obj.chat.id, message_obj.message_id)
            # Send photo with caption
            elif message_obj.photo:
                bot.send_photo(
                    user_id,
                    message_obj.photo[-1].file_id,
                    caption=message_obj.caption if message_obj.caption else None
                )
            # Send video with caption
            elif message_obj.video:
                bot.send_video(
                    user_id,
                    message_obj.video.file_id,
                    caption=message_obj.caption if message_obj.caption else None
                )
            # Send regular text message
            else:
                bot.send_message(user_id, message_obj.text)
            
            successful += 1
            time.sleep(0.1)  # Avoid hitting rate limits
        except Exception as e:
            failed += 1
            print(f"Failed to send message to {user_id}: {e}")
    
    return successful, failed

# Check subscription for all channels
def check_subscription(chat_id):
    # If user is admin or super user, bypass subscription check
    if is_admin(chat_id) or is_super_user(chat_id):
        return True
        
    channels = get_all_channels()
    if not channels:  # If no channels are added, allow access
        return True
    
    for channel_username, _ in channels:
        try:
            member = bot.get_chat_member(f'@{channel_username}', chat_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Error checking membership for {chat_id} in {channel_username}: {e}")
            continue
    return True

# Get subscription markup
def get_subscription_markup():
    markup = types.InlineKeyboardMarkup()
    channels = get_all_channels()
    
    for username, title in channels:
        channel_button = types.InlineKeyboardButton(
            f"{title} 📢", 
            url=f"https://t.me/{username}"
        )
        markup.add(channel_button)
    
    check_button = types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_subscription")
    markup.add(check_button)
    return markup

# Callback query handler for subscription check
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    if check_subscription(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Kino kodini kiriting 🎬")
    else:
        bot.answer_callback_query(
            call.id,
            "Siz hali kanallarga obuna bo'lmagansiz! ⚠️",
            show_alert=True
        )

# Get cancel markup
def get_cancel_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("❌ Bekor qilish"))
    return markup

# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    # Register user in database
    register_user(message.from_user)
    
    if not check_subscription(message.chat.id):
        markup = get_subscription_markup()
        bot.send_message(
            message.chat.id, 
            "Bot ishlashi uchun barcha kanallarga obuna bo'ling! 🔔", 
            reply_markup=markup
        )
        return

    if is_admin(message.chat.id):
        show_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Kino kodini kiriting 🎬")

# Admin command handler
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if is_admin(message.chat.id):
        show_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Bu buyruq faqat adminlar uchun! ⛔")

# Admin menu
def show_admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Movie management buttons
    add_movie_btn = types.KeyboardButton("Kino qo'shish 📥")
    delete_movie_btn = types.KeyboardButton("Kino o'chirish 🗑")
    
    # Channel management buttons
    add_channel_btn = types.KeyboardButton("Kanal qo'shish ➕")
    remove_channel_btn = types.KeyboardButton("Kanal o'chirish ➖")
    
    # User management buttons
    admin_mgmt_btn = types.KeyboardButton("Admin boshqaruvi 👨‍💼")
    super_user_btn = types.KeyboardButton("Super user boshqaruvi 👑")
    
    # Messaging buttons
    broadcast_btn = types.KeyboardButton("Reklama yuborish 📢")
    direct_msg_btn = types.KeyboardButton("Xabar yuborish ✉️")
    
    # List buttons
    channels_btn = types.KeyboardButton("Kanallar 📋")
    users_btn = types.KeyboardButton("Userlar 👥")
    
    # Database button
    db_btn = types.KeyboardButton("Kinolar bazasi 💾")
    
    # Add all buttons to markup
    markup.add(
        add_movie_btn, delete_movie_btn,
        add_channel_btn, remove_channel_btn,
        admin_mgmt_btn, super_user_btn,
        broadcast_btn, direct_msg_btn,
        channels_btn, users_btn,
        db_btn
    )
    
    bot.send_message(chat_id, "Admin panel 👨‍💼", reply_markup=markup)

# Admin menu handler
@bot.message_handler(func=lambda message: is_admin(message.chat.id))
def handle_admin_commands(message):
    if message.text == "❌ Bekor qilish":
        show_admin_menu(message.chat.id)
        return
        
    if message.text == "Kino qo'shish 📥":
        msg = bot.send_message(
            message.chat.id,
            "Kino video faylini yuboring 🎥",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_movie_file)
        
    elif message.text == "Kino o'chirish 🗑":
        msg = bot.send_message(
            message.chat.id,
            "O'chirmoqchi bo'lgan kino kodini kiriting 🗑",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, delete_movie)
        
    elif message.text == "Kanal qo'shish ➕":
        msg = bot.send_message(
            message.chat.id,
            "Kanal usernameni kiriting (@ belgisisiz) 📝",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_channel_username)
        
    elif message.text == "Kanal o'chirish ➖":
        channels = get_all_channels()
        if not channels:
            bot.send_message(message.chat.id, "Kanallar ro'yxati bo'sh! ⚠️")
            return
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for username, title in channels:
            markup.add(types.KeyboardButton(f"❌ {title} (@{username})"))
        markup.add(types.KeyboardButton("🔙 Orqaga"))
        
        bot.send_message(
            message.chat.id,
            "O'chirmoqchi bo'lgan kanalni tanlang:",
            reply_markup=markup
        )
        
    elif message.text.startswith("❌ ") and "(@" in message.text and ")" in message.text:
        # Extract username from the button text (format: "❌ Title (@username)")
        username = message.text.split("(@")[1].split(")")[0]
        if remove_channel(username):
            bot.send_message(message.chat.id, "Kanal muvaffaqiyatli o'chirildi ✅")
        else:
            bot.send_message(message.chat.id, "Xatolik yuz berdi ⚠️")
        show_admin_menu(message.chat.id)
        
    elif message.text == "Kanallar 📋":
        channels = get_all_channels()
        if not channels:
            text = "Kanallar ro'yxati bo'sh 📝"
        else:
            text = "Kanallar ro'yxati 📝:\n\n"
            for i, (username, title) in enumerate(channels, 1):
                text += f"{i}. {title} (@{username})\n"
        bot.send_message(message.chat.id, text)
        
    elif message.text == "Admin boshqaruvi 👨‍💼":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("Admin qo'shish ➕"),
            types.KeyboardButton("Admin o'chirish ➖"),
            types.KeyboardButton("Adminlar ro'yxati 📋"),
            types.KeyboardButton("🔙 Orqaga")
        )
        bot.send_message(message.chat.id, "Admin boshqaruv paneli 👨‍💼", reply_markup=markup)
        
    elif message.text == "Admin qo'shish ➕":
        msg = bot.send_message(
            message.chat.id,
            "Yangi admin ID raqamini kiriting 🔢",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_add_admin)
        
    elif message.text == "Admin o'chirish ➖":
        admins = get_all_admins()
        if not admins:
            bot.send_message(message.chat.id, "Adminlar ro'yxati bo'sh! ⚠️")
            return
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for admin_id, username, first_name, last_name in admins:
            display_name = first_name or username or admin_id
            markup.add(types.KeyboardButton(f"❌ {display_name} ({admin_id})"))
        markup.add(types.KeyboardButton("🔙 Orqaga"))
        
        bot.send_message(
            message.chat.id,
            "O'chirmoqchi bo'lgan adminni tanlang:",
            reply_markup=markup
        )
        
    elif message.text == "Adminlar ro'yxati 📋":
        admins = get_all_admins()
        if not admins:
            text = "Adminlar ro'yxati bo'sh 📝"
        else:
            text = "Adminlar ro'yxati 📝:\n\n"
            for i, (admin_id, username, first_name, last_name) in enumerate(admins, 1):
                display_name = first_name or username or admin_id
                text += f"{i}. {display_name} ({admin_id})\n"
        bot.send_message(message.chat.id, text)
        
    elif message.text == "Super user boshqaruvi 👑":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("Super user qo'shish ➕"),
            types.KeyboardButton("Super user o'chirish ➖"),
            types.KeyboardButton("Super userlar ro'yxati 📋"),
            types.KeyboardButton("🔙 Orqaga")
        )
        bot.send_message(message.chat.id, "Super user boshqaruv paneli 👑", reply_markup=markup)
        
    elif message.text == "Super user qo'shish ➕":
        msg = bot.send_message(
            message.chat.id,
            "Yangi super user ID raqamini kiriting 🔢",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_add_super_user)
        
    elif message.text == "Super user o'chirish ➖":
        super_users = get_all_super_users()
        if not super_users:
            bot.send_message(message.chat.id, "Super userlar ro'yxati bo'sh! ⚠️")
            return
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for user_id, username, first_name, last_name in super_users:
            display_name = first_name or username or user_id
            markup.add(types.KeyboardButton(f"❌ {display_name} ({user_id})"))
        markup.add(types.KeyboardButton("🔙 Orqaga"))
        
        bot.send_message(
            message.chat.id,
            "O'chirmoqchi bo'lgan super userni tanlang:",
            reply_markup=markup
        )
        
    elif message.text == "Super userlar ro'yxati 📋":
        super_users = get_all_super_users()
        if not super_users:
            text = "Super userlar ro'yxati bo'sh 📝"
        else:
            text = "Super userlar ro'yxati 📝:\n\n"
            for i, (user_id, username, first_name, last_name) in enumerate(super_users, 1):
                display_name = first_name or username or user_id
                text += f"{i}. {display_name} ({user_id})\n"
        bot.send_message(message.chat.id, text)
        
    elif message.text == "Reklama yuborish 📢":
        msg = bot.send_message(
            message.chat.id,
            "Yubormoqchi bo'lgan xabaringizni yuboring (rasm, video, forward xabar yoki matn) 📝",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_broadcast)
        
    elif message.text == "Xabar yuborish ✉️":
        msg = bot.send_message(
            message.chat.id,
            "Xabar yubormoqchi bo'lgan foydalanuvchi ID raqamini kiriting 🔢",
            reply_markup=get_cancel_markup()
        )
        bot.register_next_step_handler(msg, process_direct_message_step1)
        
    elif message.text == "Userlar 👥":
        users = get_all_users()
        if not users:
            text = "Foydalanuvchilar ro'yxati bo'sh 📝"
        else:
            text = f"Foydalanuvchilar ro'yxati 📝 (jami: {len(users)}):\n\n"
            for i, (user_id, username, first_name, last_name) in enumerate(users[:20], 1):
                display_name = first_name or username or user_id
                text += f"{i}. {display_name} ({user_id})\n"
            if len(users) > 20:
                text += f"\n...va yana {len(users) - 20} foydalanuvchi"
        bot.send_message(message.chat.id, text)
        
    elif message.text == "Kinolar bazasi 💾":
        try:
            with open('movies.db', 'rb') as db_file:
                bot.send_document(
                    message.chat.id,
                    db_file,
                    caption="Kinolar bazasi 💾"
                )
        except Exception as e:
            bot.send_message(message.chat.id, "Bazani yuklashda xatolik yuz berdi ⚠️")
            
    elif message.text == "🔙 Orqaga":
        show_admin_menu(message.chat.id)
        
    # Handle admin and super user removal
    elif message.text.startswith("❌ ") and "(" in message.text and ")" in message.text:
        # Extract user ID from the button text
        user_id = message.text.split("(")[1].split(")")[0]
        
        # Try to remove admin
        if remove_admin(user_id):
            bot.send_message(message.chat.id, "Admin muvaffaqiyatli o'chirildi ✅")
            try:
                bot.send_message(user_id, "Sizning admin huquqingiz bekor qilindi ⚠️")
            except:
                pass
        # Try to remove super user
        elif remove_super_user(user_id):
            bot.send_message(message.chat.id, "Super foydalanuvchi muvaffaqiyatli o'chirildi ✅")
            try:
                bot.send_message(user_id, "Sizning super foydalanuvchi huquqingiz bekor qilindi ⚠️")
            except:
                pass
        else:
            bot.send_message(message.chat.id, "Xatolik yuz berdi ⚠️")
        
        show_admin_menu(message.chat.id)

# Process broadcast message
def process_broadcast(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Ha ✅"),
        types.KeyboardButton("Yo'q ❌")
    )
    
    preview_text = "Rasm bilan xabar" if message.photo else \
                  "Video bilan xabar" if message.video else \
                  "Forward xabar" if message.forward_from or message.forward_from_chat else \
                  f"Matn: {message.text}"
    
    msg = bot.send_message(
        message.chat.id,
        f"Quyidagi xabarni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?\n\n"
        f"Xabar turi: {preview_text}",
        reply_markup=markup
    )
    
    # Store the original message for broadcasting
    bot.register_next_step_handler(msg, confirm_broadcast, message)

def confirm_broadcast(message, original_message):
    if message.text == "Ha ✅":
        bot.send_message(message.chat.id, "Xabar yuborilmoqda... ⏳")
        successful, failed = broadcast_message(original_message)
        bot.send_message(
            message.chat.id,
            f"Xabar yuborildi ✅\n"
            f"Yuborildi: {successful}\n"
            f"Yuborilmadi: {failed}"
        )
    else:
        bot.send_message(message.chat.id, "Xabar yuborish bekor qilindi ❌")
    
    show_admin_menu(message.chat.id)

# Movie management handlers
def process_movie_file(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    if message.content_type != 'video':
        bot.send_message(message.chat.id, "Iltimos, video fayl yuboring! ⚠️")
        show_admin_menu(message.chat.id)
        return

    file_id = message.video.file_id
    msg = bot.send_message(
        message.chat.id,
        "Kino haqida tavsif kiriting 📝",
        reply_markup=get_cancel_markup()
    )
    bot.register_next_step_handler(msg, process_description, file_id)

def process_description(message, file_id):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    description = message.text
    msg = bot.send_message(
        message.chat.id,
        "Kino uchun kod kiriting 🔑",
        reply_markup=get_cancel_markup()
    )
    bot.register_next_step_handler(msg, save_movie, file_id, description)

def save_movie(message, file_id, description):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    code = message.text
    if add_movie(code, description, file_id):
        bot.send_message(message.chat.id, "Kino muvaffaqiyatli qo'shildi ✅")
    else:
        bot.send_message(message.chat.id, "Bu kod allaqachon mavjud! ⚠️")
    show_admin_menu(message.chat.id)

def delete_movie(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    code = message.text
    if delete_movie_by_code(code):
        bot.send_message(message.chat.id, "Kino muvaffaqiyatli o'chirildi ✅")
    else:
        bot.send_message(message.chat.id, "Bunday kodli kino topilmadi! ⚠️")
    show_admin_menu(message.chat.id)

# Channel management handlers
def process_channel_username(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    username = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "Kanal nomini kiriting 📝",
        reply_markup=get_cancel_markup()
    )
    bot.register_next_step_handler(msg, process_channel_title, username)

def process_channel_title(message, username):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    title = message.text.strip()
    if add_channel(username, title):
        bot.send_message(message.chat.id, "Kanal muvaffaqiyatli qo'shildi ✅")
    else: 
        bot.send_message(message.chat.id, "Bu kanal allaqachon mavjud! ⚠️")
    show_admin_menu(message.chat.id)

# Admin management handlers
def process_add_admin(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    new_admin_id = message.text.strip()
    
    # Check if user exists
    if not get_user_by_id(new_admin_id):
        bot.send_message(message.chat.id, "Bu foydalanuvchi botdan foydalanmagan! Avval bot bilan muloqot qilishi kerak. ⚠️")
        show_admin_menu(message.chat.id)
        return
    
    # Check if already admin
    if is_admin(new_admin_id):
        bot.send_message(message.chat.id, "Bu foydalanuvchi allaqachon admin! ⚠️")
        show_admin_menu(message.chat.id)
        return
    
    if add_admin(new_admin_id, message.chat.id):
        bot.send_message(message.chat.id, f"Admin muvaffaqiyatli qo'shildi ✅ (ID: {new_admin_id})")
        try:
            bot.send_message(new_admin_id, "Siz admin etib tayinlandingiz! 🎉\nAdmin buyruqlarini ko'rish uchun /admin")
        except:
            pass
    else:
        bot.send_message(message.chat.id, "Adminni qo'shishda xatolik yuz berdi! ⚠️")
    
    show_admin_menu(message.chat.id)

# Super user management handlers
def process_add_super_user(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    new_user_id = message.text.strip()
    
    # Check if user exists
    if not get_user_by_id(new_user_id):
        bot.send_message(message.chat.id, "Bu foydalanuvchi botdan foydalanmagan! Avval bot bilan muloqot qilishi kerak. ⚠️")
        show_admin_menu(message.chat.id)
        return
    
    # Check if already super user
    if is_super_user(new_user_id):
        bot.send_message(message.chat.id, "Bu foydalanuvchi allaqachon super foydalanuvchi! ⚠️")
        show_admin_menu(message.chat.id)
        return
    
    if add_super_user(new_user_id, message.chat.id):
        bot.send_message(message.chat.id, f"Super foydalanuvchi muvaffaqiyatli qo'shildi ✅ (ID: {new_user_id})")
        try:
            bot.send_message(new_user_id, "Siz super foydalanuvchi etib tayinlandingiz! 🎉\nEndi siz kanallarga obuna bo'lmasdan kinolarni ko'rishingiz mumkin.")
        except:
            pass
    else:
        bot.send_message(message.chat.id, "Super foydalanuvchini qo'shishda xatolik yuz berdi! ⚠️")
    
    show_admin_menu(message.chat.id)

# Direct message handlers
def process_direct_message_step1(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    user_id = message.text.strip()
    
    # Check if user exists
    if not get_user_by_id(user_id):
        bot.send_message(message.chat.id, "Bu foydalanuvchi topilmadi! ⚠️")
        show_admin_menu(message.chat.id)
        return
    
    msg = bot.send_message(
        message.chat.id,
        f"Foydalanuvchi {user_id} ga yubormoqchi bo'lgan xabaringizni kiriting 📝",
        reply_markup=get_cancel_markup()
    )
    bot.register_next_step_handler(msg, process_direct_message_step2, user_id)

def process_direct_message_step2(message, user_id):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Amal bekor qilindi ❌")
        show_admin_menu(message.chat.id)
        return
        
    direct_message = message.text
    
    try:
        bot.send_message(user_id, f"📩 Admindan xabar: {direct_message}")
        bot.send_message(message.chat.id, f"Xabar foydalanuvchi {user_id} ga muvaffaqiyatli yuborildi ✅")
    except Exception as e:
        bot.send_message(message.chat.id, f"Xabar yuborishda xatolik yuz berdi: {e} ⚠️")
    
    show_admin_menu(message.chat.id)

# Handle movie code requests
@bot.message_handler(func=lambda message: True)
def handle_movie_code(message):
    # Register user in database
    register_user(message.from_user)
    
    # Check if message is from admin menu
    if is_admin(message.chat.id) and message.text.startswith("❌"):
        return
    
    # Check subscription for non-admin users
    if not check_subscription(message.chat.id):
        start(message)
        return

    # Handle movie code
    movie = get_movie_by_code(message.text)
    if movie:
        description, file_id = movie
        try:
            bot.send_video(message.chat.id, file_id, caption=description + " 🎬")
        except Exception as e:
            bot.send_message(message.chat.id, "Kinoni yuborishda xatolik yuz berdi! ⚠️")
            print(f"Error sending movie: {e}")
    else:
        bot.send_message(message.chat.id, "Bunday kodli kino topilmadi! ⚠️")

# Initialize database and start bot
if __name__ == "__main__":
    init_db()
    bot.polling(none_stop=True)
