# Taxi Service Bot

This is a Telegram bot for a taxi service that allows users to register as drivers or passengers, check their balance, and get help.

## Features

- **User Registration**: Users can register as either drivers or passengers.
- **Balance Check**: Users can check their balance.
- **Help**: Users can get help and information about how to use the bot.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/taxi-service-bot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd taxi-service-bot
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory and add your Telegram bot token and PostgreSQL database credentials:
    ```env
    TELEGRAM_TOKEN=your_telegram_bot_token
    DATABASE_URL=your_postgresql_database_url
    ```

## Usage

1. Run the bot:
    ```bash
    python bot.py
    ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
