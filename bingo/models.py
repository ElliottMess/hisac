from django.contrib.auth.models import User
from django.db import models


class Diver(models.Model):
    name = models.CharField(max_length=100)
    # Other fields...

    def __str__(self):
        return self.name if self.name else 'No User'

class Creature(models.Model):
    species = models.CharField(max_length=100, null=True)
    latin_name = models.CharField(max_length=100)
    points = models.IntegerField()
    category = models.CharField(max_length=100)

    # Other fields...
    def __str__(self):
        return self.species


class Observation(models.Model):
    diver = models.ForeignKey(Diver, on_delete=models.CASCADE)
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    date_observed = models.DateField()

    # Other fields...


class Validation(models.Model):
    observation = models.OneToOneField(Observation, on_delete=models.CASCADE)
    validator = models.ForeignKey(
        Diver, related_name="validator", on_delete=models.CASCADE
    )
    date_validated = models.DateTimeField(auto_now_add=True)
    # Other fields...
