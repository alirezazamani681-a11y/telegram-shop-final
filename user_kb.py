from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import RequiredChannel

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⭐ خرید استارز", callback_data="buy:stars")
    kb.button(text="🎁 خرید گیفت استارزی", callback_data="buy:gift")
    kb.button(text="💫 خرید ری‌اکشن استارزی", callback_data="buy:reaction")
    kb.button(text="💎 خرید پریمیوم", callback_data="buy:premium")
    kb.button(text="💰 شارژ کیف پول", callback_data="wallet:charge")
    kb.button(text="📞 پشتیبانی", callback_data="support")
    kb.adjust(1)  # هر دکمه یک ردیف
    return kb.as_markup()

def join_channels_kb(missing: list[RequiredChannel]):
    kb = InlineKeyboardBuilder()
    for i, ch in enumerate(missing, start=1):
        if ch.username:
            url = f"https://t.me/{ch.username.lstrip('@')}"
        else:
            url = ch.invite_link
        kb.button(text=f"📢 عضویت در کانال {i}", url=url)
    kb.button(text="✅ عضو شدم", callback_data="check_membership")
    kb.adjust(1)
    return kb.as_markup()

def back_to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 بازگشت به منو", callback_data="back:main")
    return kb.as_markup()