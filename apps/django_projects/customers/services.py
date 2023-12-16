# Standard Library
import logging
from datetime import datetime, timedelta
from typing import Optional

# Django
from django.db import transaction
from django.db.models import F
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.customers import selectors
from apps.django_projects.customers.models import (
    Customer,
    CustomerBalance,
    CustomerSession,
)
from apps.utils.exceptions import MOAPIException, ErrorCode

logger = logging.getLogger(__name__)


@transaction.atomic
def create_customer(
    *,
    username: str,
    password: str,
    email: str,
    phone_number: str,
    home_bet_ids: list[int],
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Customer:
    user_exists = selectors.filter_user_by_username(username=username).exists()
    if user_exists:
        raise ValidationError(f"User {username} already exists")
    home_bets = core_selectors.filter_home_bet(
        filter_=dict(id__in=home_bet_ids)
    ).all()
    user_data = dict(
        username=username,
        email=email,
        password=password,
    )
    if first_name:
        user_data.update(first_name=first_name)
    if last_name:
        user_data.update(last_name=last_name)
    user = User.objects.create_user(**user_data)
    customer = Customer.objects.create(user=user, phone_number=phone_number)
    if not home_bets:
        return customer
    balances = []
    for home_bet in home_bets:
        balances.append(
            CustomerBalance(customer=customer, home_bet=home_bet, amount=0)
        )
    CustomerBalance.objects.bulk_create(balances)
    return customer


@transaction.atomic
def update_customer(
    *,
    customer_id: int,
    email: str,
    phone_number: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Customer | None:
    customer = selectors.filter_customer(id=customer_id).first()
    if not customer:
        return None
    user = customer.user
    user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    customer.phone_number = phone_number
    user.save()
    customer.save()
    return customer


def get_customer_data(*, user_id: int, app_hash_str: str) -> dict[str, any]:
    customer = (
        selectors.filter_customer(user_id=user_id)
        .prefetch_related("balances", "balances__home_bet", "plans")
        .first()
    )
    if not customer:
        raise ValidationError("Customer does not exist")
    # TODO add more data if required
    data = dict(customer_id=customer.id)
    customer_plan = customer.plans.filter(is_active=True).first()
    if not customer_plan:
        raise MOAPIException(ErrorCode.AUTH02)
    plan = customer_plan.plan

    crash_app = plan.crash_apps.filter(hash_str=app_hash_str).first()
    if not crash_app:
        raise MOAPIException(ErrorCode.AUTH02)

    home_bet_ids = list(
        crash_app.home_bet_games.all().values_list("home_bet_id", flat=True)
    )
    home_bets_qry = (
        customer.balances.filter(home_bet_id__in=home_bet_ids, is_active=True)
        .annotate(name=F("home_bet__name"), url=F("home_bet__url"))
        .values(
            "home_bet_id",
            "name",
            "url",
        )
    )
    home_bets = []
    for home_bet in home_bets_qry:
        home_bet_id = home_bet["home_bet_id"]
        # limits = (
        #     crash_app.home_bet_games.filter(home_bet__id=home_bet_id)
        #     .values("limits")
        #     .first()
        # )
        home_bets.append(
            dict(
                id=home_bet_id,
                name=home_bet["name"],
                url=home_bet["url"],
                # limits=limits["limits"],
            )
        )
    home_bet_games = []
    for game in crash_app.home_bet_games.all():
        home_bet_games.append(
            dict(
                id=game.id,
                home_bet_id=game.home_bet_id,
                crash_game=game.crash_game.name,
                limits=game.limits,
            )
        )
    crash_app_data = dict(
        version=crash_app.version,
        home_bet_games=home_bet_games,
        home_bets=home_bets,
    )
    plan_data = dict(
        name=plan.name,
        with_ai=plan.with_ai,
        start_dt=customer_plan.start_dt,
        end_dt=customer_plan.end_dt,
        is_active=customer_plan.is_active,
        crash_app=crash_app_data,
    )
    data.update(plan=plan_data)
    return data


def get_customer_balance_data(
    *,
    customer_id: int,
    home_bet_id: int,
) -> dict[str, any]:
    balance = selectors.filter_balance(
        customer_id=customer_id, home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    data = dict(amount=balance.amount)
    return data


def update_customer_balance(
    *,
    customer_id: int,
    home_bet_id: int,
    amount: float,
    currency: Optional[str] = None,
) -> CustomerBalance:
    balance = selectors.filter_balance(
        customer_id=customer_id, home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    balance.amount = amount
    if currency is not None:
        balance.currency = currency
    balance.save()
    return balance


def inactive_customer_plans_at_end_dt():
    """
    inactive all plans at a day after end_dt
    """
    yesterday = (datetime.now() - timedelta(days=1)).date()
    customer_plans = selectors.filter_customer_plans(
        end_dt__lte=yesterday, is_active=True
    ).prefetch_related("customer", "customer__user")
    if not customer_plans.exists():
        logger.info(
            "inactive_customer_plans_at_end_dt :: "
            "No customer plans to inactive"
        )
        return
    for customer_plan in customer_plans:
        with transaction.atomic():
            customer_plan.is_active = False
            customer_plan.save()
            customer = customer_plan.customer
            other_active_plan = (
                customer.plans.filter(is_active=True)
                .exclude(id=customer_plan.id)
                .exists()
            )
            if other_active_plan:
                continue
            user = customer.user
            user.is_active = False
            user.save()


def create_customer_session(
    *,
    customer_id: int,
    home_bet_id: int,
) -> CustomerSession:
    session = CustomerSession.objects.create(
        customer_id=customer_id, home_bet_id=home_bet_id, is_active=True
    )
    return session


def live_customer(
    *,
    customer_id: int,
    home_bet_id: int,
    closing_session: bool,
    amount: float,
    currency: Optional[str] = None,
) -> dict[str, any]:
    update_customer_balance(
        customer_id=customer_id,
        home_bet_id=home_bet_id,
        amount=amount,
        currency=currency,
    )
    session = selectors.filter_customer_session(
        customer_id=customer_id, home_bet_id=home_bet_id, is_active=True
    ).first()
    if closing_session:
        if session:
            session.is_active = False
            session.save()
        return dict(allowed_to_save_multiplier=False)
    if not session:
        session = create_customer_session(
            customer_id=customer_id,
            home_bet_id=home_bet_id,
        )
    # get first session of home_bet_id
    first_session = (
        selectors.filter_customer_session(
            home_bet_id=home_bet_id, is_active=True
        )
        .order_by("created_at")
        .first()
    )
    allowed_to_save_multiplier = first_session == session
    data = dict(allowed_to_save_multiplier=allowed_to_save_multiplier)
    # update session
    session.updated_at = timezone.make_aware(datetime.utcnow())
    session.save()
    return data


def inactive_customer_sessions() -> None:
    """
    inactive all sessions at a day after end_dt
    this session does not have any effect on customer
    is only to control the allowed customer to save multiplier
    """
    date_ = datetime.now() - timedelta(seconds=60)
    sessions = selectors.filter_customer_session(
        updated_at__lte=date_, is_active=True
    )
    if not sessions.exists():
        logger.info("inactive_customer_sessions :: No sessions to inactive")
        return
    sessions.update(is_active=False)
