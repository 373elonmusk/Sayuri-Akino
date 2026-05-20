import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


async def wait_for_message(client: Client, chat_id: int, timeout: int = 60):
    """Wait for next message from user using pyrogram native listener"""
    future = asyncio.get_event_loop().create_future()
    
    @client.on_message(filters.chat(chat_id) & (filters.forwarded | (filters.text & ~filters.forwarded)), group=999)
    async def _listener(c, m):
        if not future.done():
            future.set_result(m)
        await client.remove_handler(_listener.__wrapped__, group=999)

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        try:
            await client.remove_handler(_listener.__wrapped__, group=999)
        except Exception:
            pass
        return None


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Step 1: Get first message
    await message.reply("Forward The First Message From DB Channel (With Quotes)..\n\nOr Send The DB Channel Post Link", quote=True)
    while True:
        first_message = await wait_for_message(client, message.chat.id)
        if first_message is None:
            await message.reply("⏰ Timeout! Try /batch again.", quote=True)
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nThis Post Is Not From DB Channel. Try Again.", quote=True)

    # Step 2: Get last message
    await message.reply("Forward The Last Message From DB Channel (With Quotes)..\n\nOr Send The DB Channel Post Link", quote=True)
    while True:
        second_message = await wait_for_message(client, message.chat.id)
        if second_message is None:
            await message.reply("⏰ Timeout! Try /batch again.", quote=True)
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nThis Post Is Not From DB Channel. Try Again.", quote=True)

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here Is Your Link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    await message.reply("Forward Message From The DB Channel (With Quotes)..\n\nOr Send The DB Channel Post link", quote=True)
    while True:
        channel_message = await wait_for_message(client, message.chat.id)
        if channel_message is None:
            await message.reply("⏰ Timeout! Try /genlink again.", quote=True)
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nThis Post Is Not From DB Channel. Try Again.", quote=True)

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here Is Your Link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
