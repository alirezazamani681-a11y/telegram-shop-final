from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from services.membership import check_all_channels
from user_kb import join_channels_kb, main_menu, back_to_main_kb

router = Router()

def welcome_text(name: str) -> str:
    return (
        f"سلام {name} 👋\n\n"
        "به فروشگاه تلگرام خوش آمدید!\n"
        "یکی از محصولات زیر را انتخاب کنید:"
    )

@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(welcome_text(msg.from_user.first_name), reply_markup=main_menu())

@router.callback_query(F.data == "check_membership")
async def check_membership(cb: CallbackQuery, bot: Bot):
    missing = await check_all_channels(bot, cb.from_user.id)
    if missing:
        await cb.answer("❌ هنوز عضو همه کانال‌ها نشده‌اید!", show_alert=True)
        await cb.message.edit_text(
            "🔒 لطفاً در همه کانال‌های زیر عضو شوید:",
            reply_markup=join_channels_kb(missing),
        )
        return
    await cb.answer("✅ خوش آمدید!")
    await cb.message.edit_text(
        welcome_text(cb.from_user.first_name),
        reply_markup=main_menu(),
    )

@router.callback_query(F.data == "back:main")
async def back_main(cb: CallbackQuery):
    await cb.message.edit_text(
        welcome_text(cb.from_user.first_name),
        reply_markup=main_menu(),
    )
    await cb.answer()

@router.callback_query(F.data == "support")
async def support(cb: CallbackQuery):
    await cb.message.edit_text(
        "📞 پشتیبانی\n\n"
        "برای ارتباط با پشتیبانی به آیدی زیر پیام دهید:\n"
        "@YourSupportID\n\n"
        "⏰ ساعات پاسخگویی: ۹ صبح تا ۱۲ شب",
        reply_markup=back_to_main_kb(),
    )
    await cb.answer()