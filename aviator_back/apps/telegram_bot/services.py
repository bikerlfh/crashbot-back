from typing import Union, List
from datetime import datetime
from asgiref.sync import async_to_sync
from apps.telegram_bot import telegram
from apps.telegram_bot.typing import Message


@async_to_sync
async def send_telegram_messages(
    *,
    messages: List[Message]
) -> Union[None]:
    connector = telegram.TelegramConnector()
    await connector.connect()
    for message in messages:
        await connector.send_message(
            message=message
        )
    await connector.disconnect()


def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    return check_time >= begin_time or check_time <= end_time
