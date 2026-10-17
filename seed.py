from sqlalchemy import select
from session import async_session
from models import PriceConfig, UnitLimit, ProductType, GiftItem

DEFAULT_PRICES = [
    ("stars_unit", 4140, "قیمت هر استارز", "تومان/دانه"),
    ("reaction_unit", 4140, "قیمت هر ری‌اکشن", "تومان/دانه"),
    ("premium_3", 3600000, "پریمیوم ۳ ماهه", "تومان"),
    ("premium_6", 4800000, "پریمیوم ۶ ماهه", "تومان"),
    ("premium_12", 8600000, "پریمیوم ۱۲ ماهه", "تومان"),
]

DEFAULT_LIMITS = [
    (ProductType.STARS, 50, 2000),
    (ProductType.GIFT, 1, 2000),
    (ProductType.REACTION, 1, 2000),
]

DEFAULT_GIFTS = [
    ("teddy", "تدی", "🧸", 15, 1),
    ("heart", "قلب", "❤️", 15, 2),
    ("diamond", "الماس", "💎", 100, 3),
    ("ring", "حلقه", "💍", 100, 4),
    ("cup", "جام", "🏆", 100, 5),
    ("cake", "کیک تولد", "🎂", 25, 6),
    ("champagne", "شامپاین", "🍾", 50, 7),
    ("rocket", "موشک", "🚀", 50, 8),
    ("giftbox", "جعبه کادو", "🎁", 25, 9),
    ("rose", "گل رز", "🌹", 25, 10),
    ("bouquet", "دسته گل", "💐", 50, 11),
]

async def seed_all():
    async with async_session() as session:
        result = await session.execute(select(PriceConfig).limit(1))
        if not result.scalar_one_or_none():
            for key, value, label, unit in DEFAULT_PRICES:
                session.add(PriceConfig(key=key, value=value, label=label, unit=unit))
            print("✅ قیمت‌ها seed شدند.")

        result = await session.execute(select(UnitLimit).limit(1))
        if not result.scalar_one_or_none():
            for ptype, mn, mx in DEFAULT_LIMITS:
                session.add(UnitLimit(product_type=ptype, min_qty=mn, max_qty=mx))
            print("✅ محدوده‌ها seed شدند.")

        result = await session.execute(select(GiftItem).limit(1))
        if not result.scalar_one_or_none():
            for code, name, emoji, star_cost, sort in DEFAULT_GIFTS:
                session.add(GiftItem(
                    code=code, name=name, emoji=emoji,
                    star_cost=star_cost, sort_order=sort,
                ))
            print("✅ گیفت‌ها seed شدند.")

        await session.commit()