from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

async def validate_recipient(bot: Bot, recipient: str) -> tuple[bool, str | None]:
    try:
        if recipient.startswith("@"):
            await bot.get_chat(recipient)
        elif recipient.lstrip("-").isdigit():
            await bot.get_chat(int(recipient))
        else:
            return False, "فرمت گیرنده نامعتبر است. مثال: @username یا 123456789"
        return True, None
    except TelegramBadRequest:
        return False, "کاربر یافت نشد. لطفاً آیدی را بررسی کنید."