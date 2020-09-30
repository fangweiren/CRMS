from django.contrib import admin
from crm.models import Customer, ClassList, Campuses

# Register your models here.
admin.site.register(Customer)
admin.site.register(ClassList)
admin.site.register(Campuses)