from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import (
    Item,
    Dispatch,
    DispatchItems,
    Church,
    Donee,
    Medicine,
)


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for the Item Objects."""
    category = serializers.CharField(required=False)

    class Meta:
        model = Item
        fields = ['id', 'name', 'quantity', 'category']
        read_only_fields = ['id']


class DispatchSerializer(serializers.ModelSerializer):
    """Serializer for the dispatch objects."""
    code = serializers.CharField(read_only=True)
    church = serializers.PrimaryKeyRelatedField(
        queryset=Church.objects.all(),
        many=False,
        required=True
    )
    dispatcher = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        many=False,
        required=False
    )

    class Meta:
        model = Dispatch
        fields = [
            "id",
            "code",
            "church",
            "dispatcher",
            "date",
            "receiver",
        ]

    def validate_dispatcher(self, value):
        if not value:
            value = self.context['request'].user
        return value

    def create(self, validated_data):
        validated_data['dispatcher'] = self.context['request'].user
        validated_data['date'] = timezone.now()

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        church = instance.church
        representation["church"] = {
            "id": church.id,
            "name": church.name,
            "province": str(church.municipality.province) if church.municipality else None # noqa
        }

        dispatcher = instance.dispatcher
        representation["dispatcher"] = {
            "id": dispatcher.id,
            "name": dispatcher.name
            }

        dispatch_items = instance.dispatchitems_set.all()
        stock_items = []
        non_stock_items = {}

        for item in dispatch_items:
            item_data = {
                "id": item.id,
                "content_type": item.content_type.model,
                "object_id": item.object_id,
                "item": str(item.item),
                "quantity": item.quantity,
                "beneficiary": {
                    "id": item.beneficiary.id if item.beneficiary else None,
                    "name": item.beneficiary.name if item.beneficiary else None,
                } if item.beneficiary else None,
            }

            if item.stock:
                stock_items.append(item_data)
            else:
                # Group non-stock items by benficiary
                beneficiary_id = item.beneficiary.id if item.beneficiary else "unknown" # noqa
                if beneficiary_id not in non_stock_items:
                    non_stock_items[beneficiary_id] = {
                        "beneficiary": {
                            "id": item.beneficiary.id if item.beneficiary else None, # noqa
                            "name": item.beneficiary.name if item.beneficiary else "Unknown Beneficiary", # noqa
                        },
                        "items": [],
                    }
                non_stock_items[beneficiary_id]["items"].append(item_data)

        # Agregar al resultado final
        representation["dispatch_items"] = {
            "stock_items": stock_items,
            "non_stock_items": list(non_stock_items.values()),
        }

        return representation


class DispatchItemSerializer(serializers.ModelSerializer):
    dispatch = serializers.PrimaryKeyRelatedField(
        queryset=Dispatch.objects.all()
    )
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
        )
    object_id = serializers.IntegerField()
    beneficiary = serializers.PrimaryKeyRelatedField(
        queryset=Donee.objects.all(),
        allow_null=True,
        required=False
    )
    item = serializers.SerializerMethodField()

    class Meta:
        model = DispatchItems
        fields = [
            'id', 'dispatch', 'content_type', 'object_id', 'item',
            'quantity', 'beneficiary', 'stock'
        ]

    def get_item(self, obj):
        """Obtains a representation of the vinculated object."""
        return str(obj.item) if obj.item else None

    def validate(self, data):
        """Custom DispatchItem model validations."""
        # Validate quantity
        if data['quantity'] <= 0:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be greater than 0."}
            )

        # Validate stock and beneficiary relation
        if data.get('beneficiary') and data.get('stock'):
            raise serializers.ValidationError(
                {"stock": "Stock can't have a beneficiary."}
            )
        elif not data.get("stock") and not data.get("beneficiary"):
            message = "If item is not stock, it must have a beneficiary."
            raise serializers.ValidationError({
                "beneficiary": message
            })

        # Validate content_type is coherent with the object
        content_type = data['content_type']
        object_id = data['object_id']
        model_class = content_type.model_class()

        try:
            item_instance = model_class.objects.get(pk=object_id)
        except model_class.DoesNotExist:
            message = f"Invalid object_id for content_type {content_type}."
            raise serializers.ValidationError(
                {"object_id": message}
            )

        if content_type.model == 'medicine':
            if not isinstance(item_instance, Medicine):
                raise serializers.ValidationError(
                    {"content_type": "Vinculate only medicines."}
                )
        elif content_type.model == 'item':
            if not isinstance(item_instance, Item):
                raise serializers.ValidationError(
                    {"content_type": "Vinculate only items."}
                )

        return data
