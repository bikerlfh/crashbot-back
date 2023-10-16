# Django
from rest_framework.permissions import BasePermission

# Internal
from apps.django_projects.customers import selectors


class CanUserUseAI(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        plan = selectors.filter_customer_plans(
            is_active=True,
            customer__user__id=request.user.id,
        ).first()
        return plan and plan.plan.with_ai
