# tgAntiSticker

tgAntiSticker is a Telegram bot designed to help manage and control the use of stickers in your Telegram groups. It provides feature to ensure that stickers are used appropriately and do not disrupt the flow of conversation.

## Features

- Can be used in multiple groups
- Automatically delete stickers from specified packs

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Hydr0x1de/tgAntiSticker.git
    ```
2. Navigate to the project directory:
    ```sh
    cd tgAntiSticker
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
    (developed with pyTelegramBotAPI 4.26.0)

## Usage

1. Set up your bot by creating a new bot on Telegram and obtaining the API token.
2. write `TOKEN = 'yourTokenHere'` in `secret.py`, or set environment variable TOKEN.
3. Run the bot:
    ```sh
    python3 main.py
    ```
