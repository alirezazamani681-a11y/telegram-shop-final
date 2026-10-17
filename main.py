import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# ایمپورت‌های بدون پوشه
from config import BOT_TOKEN
from session import init_db
from seed import seed_all
from membership import MembershipMiddleware
import start, shop, payment, admin, wallet

async def main():
    if not BOT_TOKEN:
        raise SystemExit("❌ BOT_TOKEN تنظیم نشده!")

    await init_db()
    await seed_all()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(MembershipMiddleware())
    dp.callback_query.middleware(MembershipMiddleware())

    dp.include_routers(
        start.router,
        shop.router,
        payment.router,
        wallet.router,
        admin.router,
    )

    print("🚀 ربات در حال اجراست...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
