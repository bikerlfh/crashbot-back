from apps.django_projects.bets.models import CustomerBalance

from apps.django_projects.bets import selectors as bets_selectors
from apps.game.domain import models
from apps.django_projects.bets.constants import BetStatus


class Game:
    def __init__(
        self,
        *,
        customer_balance: CustomerBalance,
    ):
        self.customer_balance = customer_balance
        self.customer_id = self.customer_balance.customer_id
        self.home_bet_id = self.customer_balance.home_bet_id
        self.bets: list[models.Bet] = []
        self._load_bets()

    def _load_bets(self):
        bets_qry = bets_selectors.filter_bet(
            customer_id=self.customer_id,
            home_bet_id=self.home_bet_id
        ).order_by('id').values('id', 'amount', 'multiplier', 'profit_amount', 'status')
        for bet_ in bets_qry:
            self.bets.append(
                models.Bet(
                    id=bet_['id'],
                    amount=bet_['amount'],
                    multiplier=bet_['multiplier'],
                    profit_amount=bet_['profit_amount'],
                    status=bet_['status']
                )
            )