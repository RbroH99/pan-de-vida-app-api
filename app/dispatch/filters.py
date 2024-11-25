from django_filters import rest_framework as filters
from core.models import Dispatch


class DispatchFilter(filters.FilterSet):
    date__gte = filters.DateTimeFilter(
        field_name="date",
        lookup_expr="gte",
        label="Start Date")
    date__lte = filters.DateTimeFilter(
        field_name="date",
        lookup_expr="lte",
        label="End Date")

    class Meta:
        model = Dispatch
        fields = [
            'code',
            'dispatcher__name',
            'church__municipality__province',
            'date__gte',
            'date__lte'
        ]
