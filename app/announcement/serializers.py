from rest_framework import serializers

from core.models import Announcement

from django.contrib.auth import get_user_model


User = get_user_model()


class AnnouncementSerializer(serializers.ModelSerializer):
    directed_to = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'content',
            'date',
            'initial_date',
            'final_date',
            'directed_to',
            'is_public',
            'author'
        ]

    def validate_directed_to(self, values):
        allowed_roles = range(0, 6)
        if not all(role in allowed_roles for role in values):
            raise serializers.ValidationError("One or more roles are invalid.")
        return values

    def validate_author(self, value):
        if value != self.context['request'].user:
            raise serializers.ValidationError(
                "You can't create an announcement for another user."
            )
        value = self.context['request'].user
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        author = instance.author
        representation["author"] = {
            "id": author.id,
            "name": author.name,
            "email": author.email,
        }
        return representation
