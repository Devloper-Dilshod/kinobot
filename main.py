import telebot
from telebot import types
import sqlite3
import os
import time
from datetime import datetime, date

# Pagination settings
USERS_PER_PAGE = 20

# Bot token
bot = telebot.TeleBot('8075441973:AAF4NeXcB1WEOJyVdexTHhAko3weT1tcUBo')

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
    
    # User activity table for statistics
    c.execute('''CREATE TABLE IF NOT EXISTS user_activity
                 (user_id TEXT, activity_date TEXT, activity_type TEXT,
                  PRIMARY KEY (user_id, activity_date, activity_type))''')
    
    # Blocked users table
    c.execute('''CREATE TABLE IF NOT EXISTS blocked_users
                 (user_id TEXT PRIMARY KEY, blocked_date TEXT, username TEXT, 
                  first_name TEXT, last_name TEXT)''')
    
    # Add initial admin
    c.execute("INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)",
             ('7445142075', 'system', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

# User management functions
def log_user_activity(user_id, activity_type):
    """Log user activity for statistics"""
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    try:
        c.execute("INSERT OR IGNORE INTO user_activity (user_id, activity_date, activity_type) VALUES (?, ?, ?)",
                 (str(user_id), today, activity_type))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    conn.close()

def add_blocked_user(user_id, username=None, first_name=None, last_name=None):
    """Add user to blocked list"""
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO blocked_users (user_id, blocked_date, username, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                 (str(user_id), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), username, first_name, last_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    conn.close()

def remove_blocked_user(user_id):
    """Remove user from blocked list"""
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM blocked_users WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()

def get_statistics():
    """Get bot statistics"""
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    # Total users
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    # Today's new users
    today = date.today().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_date) = ?", (today,))
    today_users = c.fetchone()[0]
    
    # Today's active users
    c.execute("SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?", (today,))
    today_active = c.fetchone()[0]
    
    # Blocked users
    c.execute("SELECT COUNT(*) FROM blocked_users")
    blocked_users = c.fetchone()[0]
    
    # Total movies
    c.execute("SELECT COUNT(*) FROM movies")
    total_movies = c.fetchone()[0]
    
    # Total channels
    c.execute("SELECT COUNT(*) FROM channels")
    total_channels = c.fetchone()[0]
    
    # Total admins
    c.execute("SELECT COUNT(*) FROM admins")
    total_admins = c.fetchone()[0]
    
    # Total super users
    c.execute("SELECT COUNT(*) FROM super_users")
    total_super_users = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'today_users': today_users,
        'today_active': today_active,
        'blocked_users': blocked_users,
        'total_movies': total_movies,
        'total_channels': total_channels,
        'total_admins': total_admins,
        'total_super_users': total_super_users
    }

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

# Get blocked users with pagination
def get_blocked_users(page=1, per_page=USERS_PER_PAGE):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    offset = (page - 1) * per_page
    c.execute("SELECT user_id, username, first_name, last_name, blocked_date FROM blocked_users ORDER BY blocked_date DESC LIMIT ? OFFSET ?", (per_page, offset))
    blocked_users = c.fetchall()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM blocked_users")
    total_count = c.fetchone()[0]
    
    conn.close()
    return blocked_users, total_count

# Get users with pagination
def get_users_paginated(page=1, per_page=USERS_PER_PAGE):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    offset = (page - 1) * per_page
    c.execute("SELECT user_id, username, first_name, last_name, joined_date FROM users ORDER BY joined_date DESC LIMIT ? OFFSET ?", (per_page, offset))
    users = c.fetchall()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM users")
    total_count = c.fetchone()[0]
    
    conn.close()
    return users, total_count

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

def get_unsubscribed_channels(chat_id):
    """Get list of channels user is not subscribed to"""
    # If user is admin or super user, bypass subscription check
    if is_admin(chat_id) or is_super_user(chat_id):
        return []
        
    channels = get_all_channels()
    if not channels:  # If no channels are added, allow access
        return []
    
    unsubscribed = []
    for channel_username, channel_title in channels:
        try:
            member = bot.get_chat_member(f'@{channel_username}', chat_id)
            # Check if user is member, admin, or creator
            if member.status in ['left', 'kicked']:
                unsubscribed.append((channel_username, channel_title))
            elif member.status == 'restricted':
                # For private channels, check if user can send messages
                if not member.can_send_messages:
                    unsubscribed.append((channel_username, channel_title))
        except Exception as e:
            # Handle different types of errors
            error_msg = str(e).lower()
            if "chat not found" in error_msg:
                print(f"Channel @{channel_username} not found or bot is not member")
                # Remove invalid channel from database
                remove_channel(channel_username)
            elif "user not found" in error_msg:
                print(f"User {chat_id} not found")
                unsubscribed.append((channel_username, channel_title))
            elif "forbidden" in error_msg:
                print(f"Bot doesn't have permission to check membership in @{channel_username}")
                # For private channels where bot can't check, assume user is not member
                unsubscribed.append((channel_username, channel_title))
            else:
                print(f"Error checking membership for {chat_id} in {channel_username}: {e}")
                # If we can't check, assume not subscribed
                unsubscribed.append((channel_username, channel_title))
    
    return unsubscribed

# Check subscription for all channels
def check_subscription(chat_id):
    """Check if user is subscribed to all channels"""
    unsubscribed = get_unsubscribed_channels(chat_id)
    return len(unsubscribed) == 0

# Get subscription markup for unsubscribed channels only
def get_subscription_markup(chat_id):
    markup = types.InlineKeyboardMarkup()
    unsubscribed_channels = get_unsubscribed_channels(chat_id)
    
    for username, title in unsubscribed_channels:
        # Try to create invite link for private channels
        try:
            # Check if channel is private by trying to get chat info
            chat_info = bot.get_chat(f'@{username}')
            if chat_info.type == 'channel':
                channel_button = types.InlineKeyboardButton(
                    f"{title} 📢", 
                    url=f"https://t.me/{username}"
                )
            else:
                # For private channels, use request to join
                channel_button = types.InlineKeyboardButton(
                    f"{title} 🔒", 
                    callback_data=f"request_join_{username}"
                )
        except:
            # If we can't get chat info, it might be private
            channel_button = types.InlineKeyboardButton(
                f"{title} 🔒", 
                callback_data=f"request_join_{username}"
            )
        markup.add(channel_button)
    
    check_button = types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_subscription")
    markup.add(check_button)
    return markup

# Handle join request for private channels
@bot.callback_query_handler(func=lambda call: call.data.startswith("request_join_"))
def handle_join_request(call):
    username = call.data.replace("request_join_", "")
    
    try:
        # Try to create invite link
        invite_link = bot.create_chat_invite_link(f'@{username}', member_limit=1)
        bot.answer_callback_query(
            call.id,
            f"Maxfiy kanalga qo'shilish uchun linkni bosing",
            show_alert=False
        )
        
        # Send invite link
        markup = types.InlineKeyboardMarkup()
        join_button = types.InlineKeyboardButton("Kanalga qo'shilish 🔗", url=invite_link.invite_link)
        check_button = types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_subscription")
        markup.add(join_button)
        markup.add(check_button)
        
        bot.edit_message_text(
            f"Maxfiy kanalga qo'shilish uchun quyidagi tugmani bosing:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
    except Exception as e:
        bot.answer_callback_query(
            call.id,
            f"Kanalga qo'shilishda xatolik: {str(e)}",
            show_alert=True
        )

# Callback query handler for subscription check
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    # Log user activity
    log_user_activity(call.message.chat.id, 'subscription_check')
    
    if check_subscription(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Kino kodini kiriting 🎬")
    else:
        unsubscribed = get_unsubscribed_channels(call.message.chat.id)
        channel_names = ", ".join([title for _, title in unsubscribed])
        bot.answer_callback_query(
            call.id,
            f"Siz hali {channel_names} kanaliga obuna bo'lmagansiz! ⚠️",
            show_alert=True
        )

# Pagination callback handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith("users_page_"))
def handle_users_pagination(call):
    if not is_admin(call.message.chat.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q!", show_alert=True)
        return
    
    page = int(call.data.split("_")[-1])
    users, total_count = get_users_paginated(page, USERS_PER_PAGE)
    
    total_pages = (total_count + USERS_PER_PAGE - 1) // USERS_PER_PAGE
    
    if not users:
        bot.answer_callback_query(call.id, "Bu sahifada foydalanuvchi yo'q!", show_alert=True)
        return
    
    text = f"👥 Foydalanuvchilar ro'yxati (sahifa {page}/{total_pages})\n"
    text += f"Jami: {total_count} ta foydalanuvchi\n\n"
    
    start_idx = (page - 1) * USERS_PER_PAGE
    for i, (user_id, username, first_name, last_name, joined_date) in enumerate(users, start_idx + 1):
        display_name = first_name or username or user_id
        join_date = joined_date[:10] if joined_date else "Noma'lum"
        text += f"{i}. {display_name}\n"
        text += f"   ID: {user_id}\n"
        text += f"   Qo'shilgan: {join_date}\n\n"
    
    # Create pagination markup
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    # Previous button
    if page > 1:
        buttons.append(types.InlineKeyboardButton("⬅️ Orqaga", callback_data=f"users_page_{page-1}"))
    
    # Current page indicator
    buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="current_page"))
    
    # Next button
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton("Oldinga ➡️", callback_data=f"users_page_{page+1}"))
    
    if len(buttons) == 1:  # Only current page button
        markup.add(buttons[0])
    elif len(buttons) == 2:  # Two buttons
        markup.add(buttons[0], buttons[1])
    else:  # Three buttons
        markup.add(buttons[0], buttons[1], buttons[2])
    
    # Close button
    close_button = types.InlineKeyboardButton("❌ Yopish", callback_data="close_users_list")
    markup.add(close_button)
    
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
    
    bot.answer_callback_query(call.id)

# Blocked users pagination callback handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith("blocked_page_"))
def handle_blocked_pagination(call):
    if not is_admin(call.message.chat.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q!", show_alert=True)
        return
    
    page = int(call.data.split("_")[-1])
    blocked_users, total_count = get_blocked_users(page, USERS_PER_PAGE)
    
    total_pages = (total_count + USERS_PER_PAGE - 1) // USERS_PER_PAGE
    
    if not blocked_users:
        bot.answer_callback_query(call.id, "Bu sahifada bloklangan foydalanuvchi yo'q!", show_alert=True)
        return
    
    text = f"🚫 Bloklangan foydalanuvchilar (sahifa {page}/{total_pages})\n"
    text += f"Jami: {total_count} ta bloklangan\n\n"
    
    start_idx = (page - 1) * USERS_PER_PAGE
    for i, (user_id, username, first_name, last_name, blocked_date) in enumerate(blocked_users, start_idx + 1):
        display_name = first_name or username or user_id
        block_date = blocked_date[:10] if blocked_date else "Noma'lum"
        text += f"{i}. {display_name}\n"
        text += f"   ID: {user_id}\n"
        text += f"   Bloklangan: {block_date}\n\n"
    
    # Create pagination markup
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    # Previous button
    if page > 1:
        buttons.append(types.InlineKeyboardButton("⬅️ Orqaga", callback_data=f"blocked_page_{page-1}"))
    
    # Current page indicator
    buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="current_page"))
    
    # Next button
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton("Oldinga ➡️", callback_data=f"blocked_page_{page+1}"))
    
    if len(buttons) == 1:  # Only current page button
        markup.add(buttons[0])
    elif len(buttons) == 2:  # Two buttons
        markup.add(buttons[0], buttons[1])
    else:  # Three buttons
        markup.add(buttons[0], buttons[1], buttons[2])
    
    # Close button
    close_button = types.InlineKeyboardButton("❌ Yopish", callback_data="close_blocked_list")
    markup.add(close_button)
    
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "current_page")
def handle_current_page(call):
    bot.answer_callback_query(call.id, "Siz hozirgi sahifadasiz", show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "close_users_list")
def handle_close_users_list(call):
    if not is_admin(call.message.chat.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q!", show_alert=True)
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "close_blocked_list")
def handle_close_blocked_list(call):
    if not is_admin(call.message.chat.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q!", show_alert=True)
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

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
    
    # Log user activity
    log_user_activity(message.chat.id, 'start')
    
    # Remove from blocked users if they start the bot again
    remove_blocked_user(message.chat.id)
    
    if not check_subscription(message.chat.id):
        unsubscribed = get_unsubscribed_channels(message.chat.id)
        if len(unsubscribed) == 1:
            channel_text = f"Botdan foydalanish uchun {unsubscribed[0][1]} kanaliga obuna bo'ling! 🔔"
        else:
            channel_text = "Bot ishlashi uchun quyidagi kanallarga obuna bo'ling! 🔔"
        
        markup = get_subscription_markup(message.chat.id)
        try:
            bot.send_message(
                message.chat.id, 
                channel_text, 
                reply_markup=markup
            )
        except Exception as e:
            # User might have blocked the bot
            add_blocked_user(message.chat.id, message.from_user.username, 
                           message.from_user.first_name, message.from_user.last_name)
            print(f"User {message.chat.id} might have blocked the bot: {e}")
        return

    if is_admin(message.chat.id):
        show_admin_menu(message.chat.id)
    else:
        try:
            bot.send_message(message.chat.id, "Kino kodini kiriting 🎬")
        except Exception as e:
            # User might have blocked the bot
            add_blocked_user(message.chat.id, message.from_user.username, 
                           message.from_user.first_name, message.from_user.last_name)
            print(f"User {message.chat.id} might have blocked the bot: {e}")

# Admin command handler
@bot.message_handler(commands=['admin'])
def admin_command(message):
    # Log user activity
    log_user_activity(message.chat.id, 'admin_command')
    
    if is_admin(message.chat.id):
        show_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Bu buyruq faqat adminlar uchun! ⛔")

# Statistics command (only for admins)
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if not is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Bu buyruq faqat adminlar uchun! ⛔")
        return
    
    stats = get_statistics()
    stats_text = f"""📊 **Bot Statistikasi**

👥 **Foydalanuvchilar:**
• Jami: {stats['total_users']}
• Bugun yangi: {stats['today_users']}
• Bugun faol: {stats['today_active']}
• Bloklagan: {stats['blocked_users']}

🎬 **Kontent:**
• Kinolar: {stats['total_movies']}
• Kanallar: {stats['total_channels']}

👨‍💼 **Boshqaruv:**
• Adminlar: {stats['total_admins']}
• Super userlar: {stats['total_super_users']}

📅 **Sana:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    try:
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
    except:
        # If markdown fails, send as plain text
        bot.send_message(message.chat.id, stats_text.replace('*', ''))

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
    
    # Statistics button
    stats_btn = types.KeyboardButton("Statistika 📊")
    
    # Blocked users button
    blocked_btn = types.KeyboardButton("Bloklaganlar 🚫")
    
    # Database button
    db_btn = types.KeyboardButton("Kinolar bazasi 💾")
    
    # Add all buttons to markup
    markup.add(
        add_movie_btn, delete_movie_btn,
        add_channel_btn, remove_channel_btn,
        admin_mgmt_btn, super_user_btn,
        broadcast_btn, direct_msg_btn,
        channels_btn, users_btn,
        stats_btn, blocked_btn,
        db_btn
    )
    
    bot.send_message(chat_id, "Admin panel 👨‍💼", reply_markup=markup)

# Admin menu handler
@bot.message_handler(func=lambda message: is_admin(message.chat.id))
def handle_admin_commands(message):
    if message.text == "❌ Bekor qilish":
        show_admin_menu(message.chat.id)
        return
        
    if message.text == "Statistika 📊":
        stats = get_statistics()
        
        # Get recent activity
        conn = sqlite3.connect('movies.db')
        c = conn.cursor()
        today = date.today().strftime('%Y-%m-%d')
        
        # Get today's most active users
        c.execute("""SELECT u.user_id, u.username, u.first_name, COUNT(*) as activity_count 
                    FROM user_activity ua 
                    JOIN users u ON ua.user_id = u.user_id 
                    WHERE ua.activity_date = ? 
                    GROUP BY ua.user_id 
                    ORDER BY activity_count DESC 
                    LIMIT 5""", (today,))
        active_users = c.fetchall()
        
        # Get recent blocked users
        c.execute("""SELECT user_id, username, first_name, blocked_date 
                    FROM blocked_users 
                    ORDER BY blocked_date DESC 
                    LIMIT 5""")
        recent_blocked = c.fetchall()
        
        # Get weekly statistics
        c.execute("""SELECT COUNT(*) FROM users 
                    WHERE DATE(joined_date) >= DATE('now', '-7 days')""")
        week_users = c.fetchone()[0]
        
        # Get monthly statistics
        c.execute("""SELECT COUNT(*) FROM users 
                    WHERE DATE(joined_date) >= DATE('now', '-30 days')""")
        month_users = c.fetchone()[0]
        
        conn.close()
        
        stats_text = f"""📊 **BATAFSIL STATISTIKA**

👥 **Foydalanuvchilar:**
• Jami: {stats['total_users']} ta
• Bugun yangi: {stats['today_users']} ta
• Bugun faol: {stats['today_active']} ta
• Bu hafta yangi: {week_users} ta
• Bu oy yangi: {month_users} ta
• Botni bloklagan: {stats['blocked_users']} ta

🎬 **Kontent:**
• Jami kinolar: {stats['total_movies']} ta
• Majburiy kanallar: {stats['total_channels']} ta

👨‍💼 **Boshqaruv:**
• Adminlar: {stats['total_admins']} ta
• Super userlar: {stats['total_super_users']} ta

🔥 **Bugun eng faol foydalanuvchilar:**"""
        
        if active_users:
            for i, (user_id, username, first_name, count) in enumerate(active_users, 1):
                name = first_name or username or user_id
                stats_text += f"\n{i}. {name} - {count} ta harakat"
        else:
            stats_text += "\nHech kim faol emas"
        
        if recent_blocked:
            stats_text += "\n\n🚫 **So'nggi bloklaganlar:**"
            for user_id, username, first_name, blocked_date in recent_blocked:
                name = first_name or username or user_id
                stats_text += f"\n• {name} ({blocked_date[:10]})"
        
        stats_text += f"\n\n📅 **Yangilangan:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
        except:
            # If markdown fails, send as plain text
            bot.send_message(message.chat.id, stats_text.replace('*', ''))
        
        return
        
    if message.text == "Bloklaganlar 🚫":
        blocked_users, total_count = get_blocked_users(1, USERS_PER_PAGE)
        if not blocked_users:
            bot.send_message(message.chat.id, "Hech kim botni bloklamagan 🎉")
        else:
            # Show first page with pagination
            total_pages = (total_count + USERS_PER_PAGE - 1) // USERS_PER_PAGE
            
            text = f"🚫 Bloklangan foydalanuvchilar (sahifa 1/{total_pages})\n"
            text += f"Jami: {total_count} ta bloklangan\n\n"
            
            for i, (user_id, username, first_name, last_name, blocked_date) in enumerate(blocked_users, 1):
                display_name = first_name or username or user_id
                block_date = blocked_date[:10] if blocked_date else "Noma'lum"
                text += f"{i}. {display_name}\n"
                text += f"   ID: {user_id}\n"
                text += f"   Bloklangan: {block_date}\n\n"
            
            # Create pagination markup if needed
            if total_pages > 1:
                markup = types.InlineKeyboardMarkup(row_width=3)
                buttons = []
                
                # Current page indicator
                buttons.append(types.InlineKeyboardButton(f"1/{total_pages}", callback_data="current_page"))
                
                # Next button
                buttons.append(types.InlineKeyboardButton("Oldinga ➡️", callback_data="blocked_page_2"))
                
                markup.add(buttons[0], buttons[1])
                
                # Close button
                close_button = types.InlineKeyboardButton("❌ Yopish", callback_data="close_blocked_list")
                markup.add(close_button)
                
                bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, text)
        
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
        users, total_count = get_users_paginated(1, USERS_PER_PAGE)
        if not users:
            bot.send_message(message.chat.id, "Foydalanuvchilar ro'yxati bo'sh 📝")
        else:
            # Show first page with pagination
            total_pages = (total_count + USERS_PER_PAGE - 1) // USERS_PER_PAGE
            
            text = f"👥 Foydalanuvchilar ro'yxati (sahifa 1/{total_pages})\n"
            text += f"Jami: {total_count} ta foydalanuvchi\n\n"
            
            for i, (user_id, username, first_name, last_name, joined_date) in enumerate(users, 1):
                display_name = first_name or username or user_id
                join_date = joined_date[:10] if joined_date else "Noma'lum"
                text += f"{i}. {display_name}\n"
                text += f"   ID: {user_id}\n"
                text += f"   Qo'shilgan: {join_date}\n\n"
            
            # Create pagination markup if needed
            if total_pages > 1:
                markup = types.InlineKeyboardMarkup(row_width=3)
                buttons = []
                
                # Current page indicator
                buttons.append(types.InlineKeyboardButton(f"1/{total_pages}", callback_data="current_page"))
                
                # Next button
                buttons.append(types.InlineKeyboardButton("Oldinga ➡️", callback_data="users_page_2"))
                
                markup.add(buttons[0], buttons[1])
                
                # Close button
                close_button = types.InlineKeyboardButton("❌ Yopish", callback_data="close_users_list")
                markup.add(close_button)
                
                bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
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
            # Log movie request activity
            log_user_activity(message.chat.id, 'movie_request')
        except Exception as e:
            # User might have blocked the bot
            add_blocked_user(message.chat.id, message.from_user.username, 
                           message.from_user.first_name, message.from_user.last_name)
            try:
                bot.send_message(message.chat.id, "Kinoni yuborishda xatolik yuz berdi! ⚠️")
            except:
                pass
            print(f"Error sending movie: {e}")
    else:
        try:
            bot.send_message(message.chat.id, "Bunday kodli kino topilmadi! ⚠️")
            # Log failed movie request
            log_user_activity(message.chat.id, 'failed_movie_request')
        except Exception as e:
            # User might have blocked the bot
            add_blocked_user(message.chat.id, message.from_user.username, 
                           message.from_user.first_name, message.from_user.last_name)
            print(f"User {message.chat.id} might have blocked the bot: {e}")

# Initialize database and start bot
if __name__ == "__main__":
    init_db()
    bot.polling(none_stop=True)