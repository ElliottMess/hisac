from django.contrib import admin

# Register your models here.
from .models import Diver

admin.site.register(Diver)

from .models import Creature
admin.site.register(Creature)

from .models import Observation
admin.site.register(Observation)
