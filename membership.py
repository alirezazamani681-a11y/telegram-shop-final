from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from config import ADMIN_IDS
from services.membership import check_all_channels
from user_kb import join_channels_kb

SKIP_CALLBACKS = {"check_membership"}

class MembershipMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        bot: Bot = data["bot"]
        if user is None:
            return await handler(event, data)

        if user.id in ADMIN_IDS:
            return await handler(event, data)

        if isinstance(event, CallbackQuery) and event.data in SKIP_CALLBACKS:
            return await handler(event, data)

        missing = await check_all_channels(bot, user.id)
        if missing:
            text = (
                "🔒 برای استفاده از ربات، ابتدا در کانال(های) زیر عضو شوید:\n\n"
                "پس از عضویت، دکمه «✅ عضو شدم» را بزنید."
            )
            kb = join_channels_kb(missing)

            if isinstance(event, Message):
                if event.text and event.text.startswith("/start"):
                    await event.answer(text, reply_markup=kb)
                return
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ ابتدا عضو کانال شوید!", show_alert=True)
                try:
                    await event.message.answer(text, reply_markup=kb)
                except Exception:
                    pass
                return

        return await handler(event, data)