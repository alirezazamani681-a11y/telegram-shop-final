from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS
from database.session import async_session
from database.models import Order

async def notify_admins_new_order(bot: Bot, order_data: dict, receipt_file_id: str):
    text = (
        f"🔔 **سفارش جدید با رسید**\n\n"
        f"🆔 سفارش: **#{order_data['id']}**\n"
        f"👤 کاربر: `{order_data['user_id']}`\n"
        f"📦 محصول: {order_data['product_detail']}\n"
        f"🎯 گیرنده: {order_data['recipient']}\n"
        f"💰 مبلغ: **{order_data['price_toman']:,}** تومان\n"
        f"🕐 زمان: {order_data['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
        f"لطفاً رسید را بررسی کنید:"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ تأیید پرداخت", callback_data=f"admin:approve_payment:{order_data['id']}")
    kb.button(text="❌ رد رسید", callback_data=f"admin:reject_payment:{order_data['id']}")
    kb.adjust(2)

    for admin_id in ADMIN_IDS:
        try:
            sent = await bot.send_photo(
                chat_id=admin_id,
                photo=receipt_file_id,
                caption=text,
                reply_markup=kb.as_markup(),
                parse_mode="Markdown",
            )
            async with async_session() as session:
                order = await session.get(Order, order_data["id"])
                if order and order.receipt_message_id is None:
                    order.receipt_message_id = sent.message_id
                    await session.commit()
        except Exception as e:
            print(f"خطا در ارسال به ادمین {admin_id}: {e}")