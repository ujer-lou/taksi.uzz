from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from env import API_KEY
from bot.main.main2 import start
from bot.main.main2 import button, handle_message


def main() -> None:
    application = Application.builder().token(API_KEY).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.CONTACT, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()


if __name__ == '__main__':
    main()
