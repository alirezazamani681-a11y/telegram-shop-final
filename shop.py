from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models import ProductType, Order, OrderStatus
from session import async_session
from pricing import get_price, get_limit
from validator import validate_recipient
from payment_info import card_payment_text
from notify import notify_admins_new_order
from user_kb import back_to_main_kb

router = Router()

class BuyStars(StatesGroup):
    waiting_quantity = State()
    waiting_recipient = State()
    waiting_receipt = State()

@router.callback_query(F.data == "buy:stars")
async def stars_entry(cb: CallbackQuery, state: FSMContext):
    unit_price = await get_price("stars_unit") or 0
    min_qty, max_qty = await get_limit(ProductType.STARS)
    await state.set_state(BuyStars.waiting_quantity)
    await state.update_data(product_type="stars")
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 بازگشت به منو", callback_data="back:main")
    await cb.message.edit_text(
        f"⭐ **خرید استارز**\n\n"
        f"💰 قیمت هر استارز: **{unit_price:,}** تومان\n"
        f"📊 محدوده: **{min_qty:,}** تا **{max_qty:,}** استارز\n\n"
        f"تعداد استارز مورد نظر را بفرستید:\nمثال: `100`",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown",
    )
    await cb.answer()

@router.message(BuyStars.waiting_quantity)
async def receive_quantity(msg: Message, state: FSMContext):
    text = (msg.text or "").replace(",", "").replace("،", "").strip()
    if not text.isdigit():
        await msg.answer("❌ لطفاً فقط عدد بفرستید. مثال: `100`", parse_mode="Markdown")
        return
    qty = int(text)
    min_qty, max_qty = await get_limit(ProductType.STARS)
    if qty < min_qty or qty > max_qty:
        await msg.answer(f"❌ تعداد باید بین **{min_qty:,}** تا **{max_qty:,}** باشد.", parse_mode="Markdown")
        return
    
    unit_price = await get_price("stars_unit") or 0
    total = qty * unit_price
    await state.update_data(quantity=qty, unit_price=unit_price, total=total)
    await state.set_state(BuyStars.waiting_recipient)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 انصراف", callback_data="back:main")
    await msg.answer(
        f"✅ تعداد: **{qty:,}** استارز\n💰 مبلغ: **{total:,}** تومان\n\n"
        f"حالا **@username** گیرنده را بفرستید:\nمثال: `@username`",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown",
    )

@router.message(BuyStars.waiting_recipient)
async def receive_recipient(msg: Message, state: FSMContext, bot: Bot):
    recipient = (msg.text or "").strip()
    if not recipient:
        await msg.answer("❌ آیدی گیرنده را بفرستید.")
        return
    ok, err = await validate_recipient(bot, recipient)
    if not ok:
        await msg.answer(f"❌ {err}\nدوباره بفرستید:")
        return

    data = await state.get_data()
    qty = data["quantity"]
    total = data["total"]
    
    async with async_session() as session:
        order = Order(
            user_id=msg.from_user.id,
            product_type=ProductType.STARS,
            product_detail=f"{qty:,} استارز",
            quantity=qty,
            recipient=recipient,
            price_toman=total,
            status=OrderStatus.AWAITING_RECEIPT,
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        order_id = order.id

    await state.update_data(order_id=order_id, recipient=recipient)
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ واریز کردم، ارسال رسید", callback_data=f"paid:{order_id}")
    kb.button(text="❌ انصراف", callback_data=f"cancel_order:{order_id}")
    await msg.answer(card_payment_text(total, order_id), reply_markup=kb.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("paid:"))
async def ask_receipt(cb: CallbackQuery, state: FSMContext):
    order_id = int(cb.data.split(":")[1])
    await state.set_state(BuyStars.waiting_receipt)
    await state.update_data(order_id=order_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ انصراف", callback_data=f"cancel_order:{order_id}")
    await cb.message.edit_text(
        "📸 **لطفاً عکس رسید واریز را بفرستید.**\n\n"
        "⚠️ رسید باید واضح باشد و مبلغ، تاریخ و شماره پیگیری در آن دیده شود.",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown",
    )
    await cb.answer()

@router.message(BuyStars.waiting_receipt, F.photo)
async def receive_receipt(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data["order_id"]
    file_id = msg.photo[-1].file_id

    async with async_session() as session:
        order = await session.get(Order, order_id)
        if not order or order.status != OrderStatus.AWAITING_RECEIPT:
            await msg.answer("❌ سفارش نامعتبر یا قبلاً پردازش شده.")
            await state.clear()
            return
        order.receipt_file_id = file_id
        order.status = OrderStatus.AWAITING_CONFIRM
        await session.commit()
        order_data = {
            "id": order.id, "user_id": order.user_id, "product_detail": order.product_detail,
            "quantity": order.quantity, "recipient": order.recipient,
            "price_toman": order.price_toman, "created_at": order.created_at,
        }

    await notify_admins_new_order(bot, order_data, file_id)
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 بازگشت به منو", callback_data="back:main")
    await msg.answer(
        f"✅ رسید شما دریافت شد!\n\n🆔 شماره سفارش: **#{order_id}**\n"
        f"⏳ رسید شما در حال بررسی است. پس از تأیید، سفارش تحویل داده می‌شود.",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown",
    )

@router.message(BuyStars.waiting_receipt)
async def reject_non_photo(msg: Message):
    await msg.answer("❌ لطفاً **عکس** رسید را بفرستید، نه متن یا فایل.")

@router.callback_query(F.data.startswith("cancel_order:"))
async def cancel_order(cb: CallbackQuery, state: FSMContext):
    order_id = int(cb.data.split(":")[1])
    async with async_session() as session:
        order = await session.get(Order, order_id)
        if order and order.status in (OrderStatus.PENDING, OrderStatus.AWAITING_RECEIPT):
            order.status = OrderStatus.CANCELLED
            await session.commit()
    await state.clear()
    await cb.message.edit_text(f"❌ سفارش #{order_id} لغو شد.", reply_markup=back_to_main_kb())
    await cb.answer()