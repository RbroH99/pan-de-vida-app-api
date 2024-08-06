from django_filters import (
    rest_framework as filters,
    CharFilter,
    NumberFilter,
)
from .models import Treatment, Medicine
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
