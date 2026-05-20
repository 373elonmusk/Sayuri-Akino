from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

CONTACT = "@yuji_henry"

# Plan details
PLANS = {
    "silver": {
        "title": "🥈 Silver Plan",
        "price": "1 Month - 50 INR",
        "desc": "This plan provides premium access for our current bot with no Ads.",
    },
    "gold": {
        "title": "🥇 Gold Plan",
        "price": "1 Month - 100 INR",
        "desc": "This plan provides premium access for our two bots with no Ads.",
    },
    "diamond": {
        "title": "💎 Diamond Plan",
        "price": "1 Month - 150 INR",
        "desc": "This plan provides premium access for our bots with no Ads.",
    },
}


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # Subscription menu
    if data == "subscription":
        await query.message.edit_text(
            text="<b>💎 Choose a Subscription Plan:</b>\n\n"
                 "Select a plan below to get details:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🥈 Buy Silver", callback_data="plan_silver")],
                [InlineKeyboardButton("🥇 Buy Gold",   callback_data="plan_gold")],
                [InlineKeyboardButton("💎 Buy Diamond", callback_data="plan_diamond")],
                [InlineKeyboardButton("🔒 Close",       callback_data="close")],
            ])
        )

    # Individual plan pages
    elif data.startswith("plan_"):
        key = data.split("_", 1)[1]   # silver / gold / diamond
        plan = PLANS.get(key)
        if not plan:
            await query.answer("Unknown plan!", show_alert=True)
            return

        await query.message.edit_text(
            text=(
                f"<b><u>{plan['title']}</u></b>\n\n"
                f"<b>{plan['price']}</b>\n\n"
                f"<blockquote>{plan['desc']}</blockquote>\n\n"
                f"◉ For payment, contact <b>{CONTACT}</b>\n\n"
                f"<i>Note: This plan is separate and lets you use bots "
                f"without verification (Ads) only. Limits will remain the same as before.</i>"
            ),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="subscription")],
                [InlineKeyboardButton("🔒 Close", callback_data="close")],
            ])
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass


# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
