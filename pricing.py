from sqlalchemy import select
from database.session import async_session
from database.models import PriceConfig, UnitLimit, ProductType, GiftItem

async def get_price(key: str) -> int | None:
    async with async_session() as session:
        cfg = await session.get(PriceConfig, key)
        return cfg.value if cfg else None

async def get_limit(ptype: ProductType) -> tuple[int, int]:
    async with async_session() as session:
        limit = await session.get(UnitLimit, ptype)
        if not limit:
            return 1, 2000
        return limit.min_qty, limit.max_qty

async def calc_unit_price(ptype: ProductType, qty: int) -> int | None:
    key_map = {
        ProductType.STARS: "stars_unit",
        ProductType.REACTION: "reaction_unit",
    }
    key = key_map.get(ptype)
    if not key: return None
    unit = await get_price(key)
    return unit * qty if unit else None

async def get_active_gifts() -> list[GiftItem]:
    async with async_session() as session:
        result = await session.execute(
            select(GiftItem).where(GiftItem.active == True).order_by(GiftItem.sort_order)
        )
        return list(result.scalars().all())

async def get_gift(gift_id: int) -> GiftItem | None:
    async with async_session() as session:
        return await session.get(GiftItem, gift_id)

async def calc_gift_price(gift: GiftItem, qty: int) -> int:
    star_price = await get_price("stars_unit") or 0
    return gift.star_cost * star_price * qty