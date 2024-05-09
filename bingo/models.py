from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime


class Diver(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensure names are unique

    def __str__(self):
        return self.name


class Creature(models.Model):
    species = models.CharField(max_length=100, null=True)
    latin_name = models.CharField(max_length=100)
    points = models.IntegerField()
    category = models.CharField(max_length=100)

    class Meta:
        ordering = ["category", "species"]

    # Other fields...
    def __str__(self):
        return self.species


class Booster(models.Model):
    booster = models.CharField(max_length=100, null=True)
    coefficient = models.FloatField()

    class Meta:
        ordering = ["coefficient"]

    def __str__(self):
        return self.booster


class Observation(models.Model):
    diver = models.ForeignKey(Diver, on_delete=models.CASCADE)
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    date_observed = models.DateField()
    points = models.FloatField()

    def __str__(self):
        
        # Return a formatted string with the desired fields
        return f"{self.diver} - {self.creature}  ({self.points} points)"

class Validation(models.Model):
    observation = models.OneToOneField(Observation, on_delete=models.CASCADE)
    validator = models.ForeignKey(
        Diver, related_name="validator", on_delete=models.CASCADE
    )
    date_validated = models.DateTimeField(auto_now_add=True)
    # Other fields...
