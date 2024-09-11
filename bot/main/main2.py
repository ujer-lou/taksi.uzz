import psycopg2
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext

from db.config import DB_CONNECTION


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    gg = user_id
    if gg and is_registered_taxi_driver(gg):
        await show_taxi_menu(update, context)
    elif gg and is_registered_taxi_driver1(gg):
        await user(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("Register as Taxi 🚕🚖", callback_data='register_taxi')],
            [InlineKeyboardButton("Register as User 👨🏼", callback_data='user_step')],
            [InlineKeyboardButton("Help 📞🆘", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    try:
        await query.answer()
    except telegram.error.BadRequest as e:
        if "QUERY_ID_INVALID" in str(e):
            pass

    if query.data == 'register_taxi':
        keyboard = [[KeyboardButton("Share Contact", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text("Please share your contact information:", reply_markup=reply_markup)  # noqa
        context.user_data['registration_step'] = 'contact'
    elif query.data == 'user_step':
        keyboard = [[KeyboardButton("Share Contact", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text("Please share your contact information:", reply_markup=reply_markup)  # noqa
        context.user_data['user_step'] = 'contact'
    elif query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("Back", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Help message\n\nFor support, call: +998880505502",
                                      reply_markup=reply_markup)
    elif query.data == 'back':
        await start(update, context)
    elif query.data == 'Profile':
        user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
        user_info = get_user_info(user_id)
        formatted_info = f"User ID: {user_info['user_id']}\nFull Name: {user_info['fullname']}\nBalance: {user_info['balance']}\nCar Number: {user_info['car_number']}"
        if update.effective_chat:
            await update.effective_chat.send_message(text=formatted_info)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text=formatted_info)
    elif query.data == 'Balance':
        user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
        user_info = get_user_info(user_id)
        await update.effective_chat.send_message(text=f"Your current balance is: {user_info['balance']}")
    elif query.data == 'Fill':
        await update.effective_chat.send_message(text="Please enter how much you want to fill:")
        context.user_data['update_step'] = 'change_balance'
    elif query.data == 'Fill1':
        await update.effective_chat.send_message(text="Please enter how much you want to fill:")
        context.user_data['update_step'] = 'change_balance1'
    elif query.data == 'Update':
        keyboard = [
            [InlineKeyboardButton("Change Fullname 🔄", callback_data='ChangeFullname')],
            [InlineKeyboardButton("Change Car Number 🔄", callback_data='ChangeCarNumber')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message(text="Choose an option to update your profile:",
                                                 reply_markup=reply_markup)
    elif query.data == 'ChangeFullname':
        await update.effective_chat.send_message(text="Please enter your new fullname:")
        context.user_data['update_step'] = 'change_fullname'
    elif query.data == 'ChangeCarNumber':
        await update.effective_chat.send_message(text="Please enter your new car number:")
        context.user_data['update_step'] = 'change_car_number'
    elif query.data == 'Passenger':
        pass
    elif query.data == 'Profile1':
        user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
        user_info = get_user_info1(user_id)
        formatted_info = f"User ID: {user_info['user_id']}\nFull Name: {user_info['fullname']}\nPhone number: {user_info['phone_number']}\nBalance: {user_info['balance']}"
        await update.effective_chat.send_message(text=formatted_info)
    elif query.data == 'Passenger1':
        location_button = KeyboardButton(text="Share Location", request_location=True)
        keyboard = ReplyKeyboardMarkup([[location_button]], resize_keyboard=True)
        await update.effective_chat.send_message("Press the button to share your location:", reply_markup=keyboard)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'user_step' in context.user_data:
        step = context.user_data['user_step']
        if step == 'contact':
            contact = update.message.contact
            context.user_data['contact'] = contact.phone_number
            await update.message.reply_text("Please enter your fullname:")
            context.user_data['user_step'] = 'change_fullname'
        elif step == 'change_fullname':
            fullname = update.message.text
            context.user_data['fullname'] = fullname
            context.user_data['user_id'] = update.message.from_user.id  # Add this line
            await save_to_database1(context.user_data, update.message.from_user.id)
            await update.message.reply_text("You have been registered as a user!")
            await user(update, context)
            context.user_data.clear()
    if 'registration_step' in context.user_data:
        step = context.user_data['registration_step']
        if step == 'contact':
            contact = update.message.contact
            context.user_data['contact'] = contact.phone_number
            await update.message.reply_text("Please enter your full name:")
            context.user_data['registration_step'] = 'fullname'
        elif step == 'fullname':
            fullname = update.message.text
            context.user_data['fullname'] = fullname
            await update.message.reply_text("Please enter your car number: (A951BC)")
            context.user_data['registration_step'] = 'car_number'
        elif step == 'car_number':
            car_number = update.message.text
            context.user_data['car_number'] = car_number
            context.user_data['user_id'] = update.message.from_user.id  # Add this line
            await save_to_database(context.user_data, update.message.from_user.id)
            await update.message.reply_text("You have been registered as a taxi driver!")
            await show_taxi_menu(update, context)
            context.user_data.clear()
    elif 'update_step' in context.user_data:
        step = context.user_data['update_step']
        if step == 'change_fullname':
            fullname = update.message.text
            user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
            await update_fullname(user_id, fullname)
            await update.effective_chat.send_message(text="Your fullname has been updated.")
            del context.user_data['update_step']
            await show_taxi_menu(update, context)
        elif step == 'change_car_number':
            car_number = update.message.text
            user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
            await update_car(user_id, car_number)
            await update.effective_chat.send_message(text="Your car number has been updated.")
            del context.user_data['update_step']
            await show_taxi_menu(update, context)
        elif step == 'change_balance':
            balance = update.message.text
            user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
            await update_balance(user_id, balance)
            await update.effective_chat.send_message(text=f"Your balance has been updated. {balance}")
            del context.user_data['update_step']
            await show_taxi_menu(update, context)
        elif step == 'change_balance1':
            balance = update.message.text
            user_id = update.effective_chat.id if update.effective_chat else update.callback_query.from_user.id
            await update_balance1(user_id, balance)
            await update.effective_chat.send_message(text=f"Your balance has been updated. {balance}")
            del context.user_data['update_step']
            await user(update, context)


async def user(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Profile 👤", callback_data="Profile1"),
         InlineKeyboardButton("Get Taxi 🚕🚖", callback_data="Passenger1"),
         InlineKeyboardButton("Fill Balance ⚖️", callback_data="Fill1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text('Please choose an option:', reply_markup=reply_markup)  # noqa


async def update_fullname(user_id: int, fullname: str) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("UPDATE taxi_usur SET fullname=%s WHERE user_id=%s", (fullname, str(user_id)))  # noqa
    conn.commit()
    cursor.close()
    conn.close()


async def update_car(user_id: int, fullname: str) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("UPDATE taxi_usur SET car_number=%s WHERE user_id=%s", (fullname, str(user_id)))  # noqa
    conn.commit()
    cursor.close()
    conn.close()


async def update_balance(user_id: int, fullname: str) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("UPDATE taxi_usur SET balance=%s WHERE user_id=%s", (fullname, str(user_id)))  # noqa
    conn.commit()
    cursor.close()
    conn.close()


async def update_balance1(user_id: int, fullname: str) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=%s WHERE user_id=%s", (fullname, str(user_id)))  # noqa
    conn.commit()
    cursor.close()
    conn.close()


async def update_profile(user_id: int, fullname: str, car_number: str) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE taxi_usur SET fullname=%s, car_number=%s WHERE user_id=%s",  # noqa
        (fullname, car_number, str(user_id))
    )
    conn.commit()
    cursor.close()
    conn.close()


async def show_taxi_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Profile 👤", callback_data="Profile"),
         InlineKeyboardButton("Get Passenger 🚶🏼", callback_data="Passenger")],
        [InlineKeyboardButton("Balance 🏦", callback_data="Balance"),
         InlineKeyboardButton("Fill Balance ⚖️", callback_data="Fill")],
        [InlineKeyboardButton("Update Profile ✏️", callback_data="Update")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


def get_user_info(user_id: int) -> dict:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, fullname, balance, car_number FROM taxi_usur WHERE user_id = %s",
                   (user_id,))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return {
            'user_id': result[0],
            'fullname': result[1],
            'balance': result[2],
            'car_number': result[3]
        }
    else:
        return {}


def get_user_info1(user_id: int) -> dict:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id,phone_number, fullname, balance FROM users WHERE user_id = %s", (user_id,))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return {
            'user_id': result[0],
            'phone_number': result[1],
            'fullname': result[2],
            'balance': result[3]
        }
    else:
        return {}


def get_balance(user_id: int) -> float:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM taxi_usur WHERE user_id = %s", (user_id,))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0.0  # Return 0.0 if balance is not found


async def save_to_database(user_data: dict, user_id: int) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO taxi_usur (phone_number, fullname, car_number, is_registered, user_id,balance) VALUES (%s, %s, %s, %s, %s, %s)",
        # noqa
        (user_data['contact'], user_data['fullname'], user_data['car_number'], True, str(user_id), 0.0)
    )
    conn.commit()
    cursor.close()
    conn.close()


async def save_to_database1(user_data: dict, user_id: int) -> None:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (phone_number, fullname, user_id, balance) VALUES (%s, %s, %s, %s)",  # noqa
        (user_data['contact'], user_data['fullname'], str(user_id), 0.0)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_phone_number(user_id: int) -> str:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT phone_number FROM taxi_usur WHERE phone_number = %s", (str(user_id),))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def is_registered_taxi_driver(phone_number: str) -> bool:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT is_registered FROM taxi_usur WHERE user_id = %s", (phone_number,))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and result[0]


def is_registered_taxi_driver1(phone_number: str) -> bool:
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT true FROM users WHERE user_id = %s", (phone_number,))  # noqa
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and result[0]
