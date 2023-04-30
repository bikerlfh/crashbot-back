# Standard Library
import inspect
import logging

# Libraries
from apps.django_projects.customers import selectors as customers_selectors
from apps.sockets.exceptions import WSCustomerNotFound, WSFunctionNotFound
from apps.sockets.models import SocketMessage
from apps.telegram_bot import services as telegram_services

logger = logging.getLogger(__name__)


def send_message_to_admin(*, message: str, **_kwargs) -> None:
    telegram_services.send_telegram_message(chat_id="me", message=message)


def send_message_to_user(*, message: str, customer_id: int, **_kwargs):
    customer_data = (
        customers_selectors.filter_customer(id=customer_id)
        .values("phone_number")
        .first()
    )
    if not customer_data:
        raise WSCustomerNotFound(f"customer {customer_id} not found")
    telegram_services.send_telegram_message(
        chat_id=customer_data["phone_number"], message=message
    )


def send_message(message: SocketMessage) -> None:
    frame = inspect.currentframe()
    functions = [
        obj for obj in frame.f_back.f_locals.values() if inspect.isfunction(obj)
    ]
    func = [func for func in functions if func.__name__ == message.func]
    if not func:
        raise WSFunctionNotFound(
            f"websocket :: function ({message.func}) not implemented"
        )
    func[0](**vars(message))
