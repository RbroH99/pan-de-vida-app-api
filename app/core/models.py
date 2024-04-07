"""
Models for the pandevida app API.
"""
from django.db import models


class MedClass(models.Model):
    """Medicine classification model."""
    name = models.CharField(max_length=60,
                            unique=True,
                            null=False,
                            blank=False)

    def __str__(self) -> str:
        return self.name
