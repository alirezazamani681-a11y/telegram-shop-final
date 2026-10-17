from config import CARD_NUMBER, CARD_HOLDER, CARD_BANK

def format_card_number(num: str) -> str:
    if len(num) == 16:
        return f"{num[:4]}-{num[4:8]}-{num[8:12]}-{num[12:]}"
    return num

def card_payment_text(amount: int, order_id: int) -> str:
    return (
        f"💳 **پرداخت کارت به کارت**\n\n"
        f"مبلغ: **{amount:,}** تومان\n"
        f"شماره کارت:\n"
        f"`{format_card_number(CARD_NUMBER)}`\n"
        f"به نام: **{CARD_HOLDER}**\n"
        f"بانک: {CARD_BANK}\n\n"
        f"⚠️ **مهم:** در قسمت «توضیحات» تراکنش، این کد را بنویسید:\n"
        f"`ORD-{order_id}`\n\n"
        f"بعد از واریز، دکمه «✅ واریز کردم» را بزنید."
    )