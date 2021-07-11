from django.contrib import admin

# Register your models here.
from .models import Membership, UserMembership, Subscription, Address

admin.site.register(Membership)
admin.site.register(UserMembership)
admin.site.register(Subscription)
admin.site.register(Address)