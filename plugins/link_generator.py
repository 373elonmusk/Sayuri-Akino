import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


async def wait_for_message(client: Client, chat_id: int, timeout: int = 60):
    """Wait for next message - pyrogram native, no pyromod"""
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    handler_added = False

    async def _listener(c, m):
        if m.chat.id == chat_id and not future.done():
            future.set_result(m)

    handler = client.on_message(
        filters.chat(chat_id) & (filters.forwarded | (filters.text & ~filters.forwarded)),
        group=999
    )(_listener)
    handler_added = True

    try:
        result = await asyncio.wait_for(asyncio.shield(future), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return None
    finally:
        if handler_added:
            try:
                client.remove_handler(*handler)
            except Exception:
                pass


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Step 1
    sent = await message.reply(
        "📨 <b>Step 1/2</b>\n\nForward The <b>First</b> Message From DB Channel\n\nOr Send The DB Channel Post Link",
        quote=True
    )
    while True:
        first_message = await wait_for_message(client, message.chat.id, timeout=60)
        if first_message is None:
            await sent.edit("⏰ Timeout! Send /batch again.")
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            await first_message.reply("✅ First message received!", quote=True)
            break
        else:
            await first_message.reply(
                "❌ This post is not from DB Channel.\nTry again.", quote=True
            )

    # Step 2
    sent2 = await message.reply(
        "📨 <b>Step 2/2</b>\n\nForward The <b>Last</b> Message From DB Channel\n\nOr Send The DB Channel Post Link",
        quote=True
    )
    while True:
        second_message = await wait_for_message(client, message.chat.id, timeout=60)
        if second_message is None:
            await sent2.edit("⏰ Timeout! Send /batch again.")
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                "❌ This post is not from DB Channel.\nTry again.", quote=True
            )

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
    ])
    await second_message.reply_text(
        f"<b>✅ Batch Link Ready!</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup
    )


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    sent = await message.reply(
        "📨 Forward Message From The DB Channel\n\nOr Send The DB Channel Post link",
        quote=True
    )
    while True:
        channel_message = await wait_for_message(client, message.chat.id, timeout=60)
        if channel_message is None:
            await sent.edit("⏰ Timeout! Send /genlink again.")
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply(
                "❌ This post is not from DB Channel.\nTry again.", quote=True
            )

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
    ])
    await channel_message.reply_text(
        f"<b>✅ Here Is Your Link</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup
    )


# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
