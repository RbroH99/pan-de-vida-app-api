from rest_framework import serializers

from core.models import Announcement


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

    def validate_directed_to(self, value):
        allowed_roles = range(0, 6)
        if not all(role in allowed_roles for role in value):
            raise serializers.ValidationError("One or more roles are invalid.")
        return

    def validate_author(self, value):
        if value != self.context['request'].user:
            raise serializers.ValidationError(
                "You can't create an announcement for another user."
            )
        value = self.context['request'].user
        return value
