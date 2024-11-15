import time
import telebot
from telebot import types
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon.tl.functions.contacts import ApproveChatRequest
from telethon.tl.functions.channels import EditAdminRequest, LeaveChannel
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import asyncio
import threading

# Bot setup
API_TOKEN = '7821967646:AAFHUS91204U6P6xqnBOdAefk42agRWzTc0'
bot = telebot.TeleBot(API_TOKEN)

# User account credentials (for Telethon)
api_id = '22012880'
api_hash = '5b0e07f5a96d48b704eb9850d274fe1d'
phone_number = '7367017930'

# Initialize Telethon client (this will represent your user account)
client = TelegramClient('session_name', api_id, api_hash)

# Ensure the Telethon client is logged in properly
async def login():
    try:
        # Check if the client is already authorized
        await client.start(phone_number)
    except SessionPasswordNeededError:
        print("Two-step verification is enabled. Please provide the password.")
    except Exception as e:
        print(f"Failed to log in: {e}")
        raise e

# Function to accept all join requests with the given user account
async def accept_all_requests(channel_username):
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_username)

        # Accept all pending join requests
        pending_requests = await client.get_chat_requests(channel)
        for request in pending_requests:
            try:
                # Approve each request
                await client.approve_chat_request(channel, request.user_id)
                print(f"Approved join request for user {request.user_id}")
            except FloodWaitError as e:
                # Handle FloodWaitError by waiting the required amount of time
                print(f"Rate limit hit. Waiting for {e.seconds} seconds...")
                time.sleep(e.seconds)  # Wait for the specified time before retrying
                await client.approve_chat_request(channel, request.user_id)

    except Exception as e:
        print(f"Error: {e}")

# Function to add a user account as an admin in the channel
async def add_user_as_admin(channel_username, user_id):
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_username)

        # Create rights for the user
        rights = ChatAdminRights(add_admin=True, change_info=True)

        # Add the user as an admin with the created rights
        await client(EditAdminRequest(channel, user_id, rights=rights))
        print(f"User {user_id} added as admin.")

    except Exception as e:
        print(f"Error adding admin: {e}")

# Function for the bot to leave the channel
async def bot_leave_channel(channel_username):
    try:
        # Get the bot entity and leave the channel
        channel = await client.get_entity(channel_username)
        await client(LeaveChannel(channel))
        print("Bot has left the channel.")
    except Exception as e:
        print(f"Error when bot leaves the channel: {e}")

# Function for the user account to leave the channel
async def user_leave_channel(channel_username):
    try:
        # Get the user account and leave the channel
        channel = await client.get_entity(channel_username)
        await client(LeaveChannel(channel))
        print("User account has left the channel.")
    except Exception as e:
        print(f"Error when user account leaves the channel: {e}")

# Function to send the welcome message
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Create the inline button for the developer's link
    developer_button = types.InlineKeyboardButton(text="• Developer •", url="https://t.me/Ur_Amit_01")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(developer_button)

    # Craft the welcome message with explanations
    welcome_text = (
        "Welcome to the Auto Join Request Acceptor Bot! 🚀\n\n"
        "This bot allows you to accept all join requests at once in your private channels.\n\n"
        "How it works:\n"
        "1. Add the bot to your channel as an admin with the add new admins permissions.\n"
        "2. Use the /acceptall command, and the bot will automatically accept all pending join requests.\n"
        "3. Once done, the bot will leave your channel.\n\n"
        "Enjoy!🗿"
    )
    
    # Send the message along with the inline button
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

# Bot command to trigger the accept all requests
@bot.message_handler(commands=['acceptall'])
def handle_accept_all(message):
    try:
        # Get the channel username or ID from the message
        chat = message.chat
        channel_username = chat.username if chat.username else chat.id

        # Get the user ID to add as an admin (You will have to pass this user ID in the command or set it)
        user_id = '6803505727'  # Replace with the actual user ID

        # Send an acknowledgment message to the user
        bot.reply_to(message, "Processing join requests...")

        # First, add the user account as admin
        asyncio.run(add_user_as_admin(channel_username, user_id))

        # Then, accept all join requests using the user account
        asyncio.run(accept_all_requests(channel_username))

        # Make sure the bot and user account leave the channel after completing the task
        asyncio.run(bot_leave_channel(channel_username))
        asyncio.run(user_leave_channel(channel_username))

        bot.reply_to(message, "All join requests accepted and bot have left the channel!")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")
        print(f"Bot error: {e}")

# Start the bot and listen for incoming commands
def start_bot():
    print("Bot is starting...")
    bot.polling(non_stop=True, interval=0)

# Start the Telethon client (user account) in a separate thread
def start_telethon_client():
    print("Logging in to Telethon client...")
    asyncio.run(login())

# Running both the bot and Telethon client in parallel using threads
if __name__ == "__main__":
    # Create two threads for the bot and the Telethon client
    bot_thread = threading.Thread(target=start_bot)
    telethon_thread = threading.Thread(target=start_telethon_client)

    # Start the threads
    bot_thread.start()
    telethon_thread.start()

    # Wait for both threads to complete
    bot_thread.join()
    telethon_thread.join()
