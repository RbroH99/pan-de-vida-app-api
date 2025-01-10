from django_filters import (
    rest_framework as filters,
    CharFilter,
    NumberFilter,
    DateTimeFilter,
)
from .models import Treatment, Medicine, Contact, Announcement

from medicine.serializers import TreatmentSerializer


class TreatmentMedicineFilter(filters.Filter):

    def filter(self, qs, value):
        treatments_id = []
        if value is not None:
            serializer = TreatmentSerializer(qs, many=True)
            for treatment in serializer.data:
                medicine_ids = treatment.get('medicine', None)
                if medicine_ids:
                    for id in medicine_ids:
                        if Medicine.objects.get(id=id).name == value:
                            treatments_id.append(treatment['id'])
            qs = qs.filter(id__in=list(treatments_id))
        return qs


class TreatmentFilter(filters.FilterSet):
    medicine = TreatmentMedicineFilter()
    disease = CharFilter(method='filter_by_disease_name')
    donee = NumberFilter(method='filter_by_donee')

    class Meta:
        model = Treatment
        fields = ['medicine', 'disease', 'donee']

    def filter_by_disease_name(self, queryset, name, value):
        return queryset.filter(disease__name=value)

    def filter_by_donee(self, queryset, name, value):
        return queryset.filter(donee__id=value)


class ChurchContactTypeFilter(filters.Filter):
    def filter(self, qs, value):
        if value == "priest":
            priest_ids = list(
                Contact.objects.filter(
                    church_priest__isnull=False
                ).values_list('id', flat=True).distinct()
            )
            return qs.filter(id__in=priest_ids)

        elif value == "facilitator":
            facilitator_ids = list(
                Contact.objects.filter(
                    church_facilitator__isnull=False
                ).values_list('id', flat=True).distinct()
            )
            return qs.filter(id__in=facilitator_ids)

        return qs


class ContactFilterset(filters.FilterSet):
    type = ChurchContactTypeFilter()
    gender = CharFilter(method='filter_by_gender')

    class Meta:
        model = Contact
        fields = ['gender', 'type']

    def filter_by_gender(self, queryset, name, value):
        return queryset.filter(gender=value)


class SpecificAnnouncementsFilter(filters.Filter):
    """Filter to isolate announces directed to specific user roles."""
    def filter(self, qs, value):
        if value is not None:
            specific_ids = [instance.id for instance in qs if value in instance.directed_to] # noqa
            qs = qs.filter(id__in=specific_ids)
        return qs


class AnnouncementFilterSet(filters.FilterSet):
    """Filter Set class for Announcements viewset."""
    initial_date__gte = DateTimeFilter(
        field_name="initial_date",
        label="Start Date",
    )
    initial_date__lte = DateTimeFilter(
        field_name="initial_date",
        label="End Date",
    )
    final_date__gte = DateTimeFilter(
        field_name='final_date',
        label="Start Date"
        )
    final_date__lte = DateTimeFilter(
        field_name='final_date',
        label="End Date"
        )
    date__gte = DateTimeFilter(
        field_name="date",
        lookup_expr="gte",
        label="Start Date")
    date__lte = DateTimeFilter(
        field_name="date",
        lookup_expr="lte",
        label="End Date")
    directed_to = SpecificAnnouncementsFilter()

    class Meta:
        model = Announcement
        fields = [
            "initial_date__gte",
            "initial_date__lte",
            "final_date__gte",
            "final_date__lte",
            "date__gte",
            "date__lte",
            "author",
            "directed_to",
            "is_public"
        ]
