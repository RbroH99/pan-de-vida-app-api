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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context['request'].user

        if user.role > 1:
            representation.pop("quantity", None)
        return representation


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

    def _validate_dispatch_item(self, dispatch_items_data, stock=False):
        """Validates the dispatch items without having created dispatch."""
        for item_data in dispatch_items_data:
            if not item_data.get("quantity", None):
                raise serializers.ValidationError(
                    {"dispatch_items": "Quantity must is required"},
                    code="required",
                )
            elif item_data.get("quantity", 0) <= 0:
                raise serializers.ValidationError(
                    {"dispatch_items": "Quantity must be greater than 0"},
                    code="invalid",
                )
            elif not item_data.get("content_type", None):
                raise serializers.ValidationError(
                    {"dispatch_items": "Content type is required."}
                )
            elif not item_data.get("object_id", None):
                raise serializers.ValidationError(
                    {"dispatch_items": "Object id is required."}
                    )

            content_type = ContentType.objects.get_for_id(
                item_data.get("content_type", None)
                )
            object_id = item_data.get("object_id", None)
            model_class = content_type.model_class()
            item_quantity = model_class.objects.get(id=object_id).quantity
            if item_data.get("quantity", 0) > item_quantity:
                raise serializers.ValidationError(
                    {"quantity": "Quantity must be less than item quantity."}
                )

    def create(self, validated_data):
        request = self.context['request']
        validated_data['dispatcher'] = request.user
        validated_data['date'] = timezone.now()
        dispatch_items_data = request.data.get('dispatch_items', {})

        # Validate dispatch items data before attempting to create dispatch
        non_stock_items = dispatch_items_data.get("non_stock_items", [])
        for item in non_stock_items:
            self._validate_dispatch_item(item["items"], stock=False)
        stock_items = dispatch_items_data.get("stock_items", [])
        self._validate_dispatch_item(stock_items, stock=True)

        dispatch = super().create(validated_data)

        for item_data in dispatch_items_data.get("stock_items", []):
            self._create_dispatch_item(dispatch, item_data, stock=True)

        for non_stock in dispatch_items_data.get("non_stock_items", []):
            beneficiary_id = non_stock.get("beneficiary", None)

            if beneficiary_id:
                try:
                    beneficiary = Donee.objects.get(pk=beneficiary_id)
                except Donee.DoesNotExist:
                    raise serializers.ValidationError(
                        {"dispatch_items": f"Beneficiary with id {beneficiary_id} does not exist."} # noqa
                    )
            else:
                raise serializers.ValidationError(
                    {"dispatch_items": "Each non-stock item must have a valid beneficiary."} # noqa
                )

            for item_data in non_stock.get("items", []):
                self._create_dispatch_item(
                    dispatch, item_data, stock=False, beneficiary=beneficiary
                )

        return dispatch

    def _create_dispatch_item(
            self, dispatch, item_data, stock, beneficiary=None
            ):
        """Helper method to create a DispatchItem."""
        item_data["dispatch"] = dispatch.id
        item_data["stock"] = stock
        if beneficiary:
            item_data["beneficiary"] = beneficiary.id

        serializer = DispatchItemSerializer(
            data=item_data,
            context=self.context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

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
                    "name": item.beneficiary.contact.name if item.beneficiary else None, # noqa
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
                            "name": item.beneficiary.contact.name if item.beneficiary else "Unknown Beneficiary", # noqa
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


class DispatchListSerializer(serializers.ModelSerializer):
    """Serializer for the dispatch list method."""
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
            'quantity', 'beneficiary', 'stock', "observation"
        ]

    def get_item(self, obj):
        """Obtains a representation of the vinculated object."""
        return str(obj.item) if obj.item else None

    def validate(self, data):
        """Custom DispatchItem model validations."""
        content_type = data['content_type']
        model_class = content_type.model_class()
        object_id = data['object_id']

        # Validate quantity
        quantity = data['quantity']
        item_quantity = model_class.objects.get(id=object_id).quantity
        if quantity <= 0:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be greater than 0."}
            )
        elif quantity > item_quantity:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be less than item quantity."}
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

    def create(self, validated_data):
        dispatch_item = super().create(validated_data)
        item = dispatch_item.item
        quantity = validated_data.get('quantity', 0)
        item.quantity = item.quantity - quantity
        item.save()
        return dispatch_item
