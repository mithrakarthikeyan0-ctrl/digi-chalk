from django.db import models
from common.models import UUIDTimeStampedModel


class School(UUIDTimeStampedModel):
    """
    School entity representing an educational institution.
    """
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.location})" if self.location else self.name
