from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(House)
admin.site.register(Student)
admin.site.register(Specialist)
admin.site.register(Landlord)
admin.site.register(Reservation)
admin.site.register(University)
admin.site.register(UniversityToken)
admin.site.register(Rating)