from os import getenv
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in getenv("ADMIN_IDS", "").split(",") if x.strip()]
DATABASE_URL = getenv("DATABASE_URL", "sqlite+aiosqlite:///shop.db")

CARD_NUMBER = getenv("CARD_NUMBER", "")
CARD_HOLDER = getenv("CARD_HOLDER", "")
CARD_BANK = getenv("CARD_BANK", "")

@dataclass
class RequiredChannel:
    chat_id: str
    username: str
    invite_link: str

def _parse_channels(raw: str) -> list[RequiredChannel]:
    channels = []
    for line in raw.split(","):
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        channels.append(RequiredChannel(
            chat_id=parts[0].strip(),
            username=parts[1].strip(),
            invite_link=parts[2].strip(),
        ))
    return channels

REQUIRED_CHANNELS = _parse_channels(getenv("REQUIRED_CHANNELS", ""))