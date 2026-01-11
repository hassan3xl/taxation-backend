from django.contrib import admin
from .models import User, TaxPayer, Agent

admin.site.register(User)
admin.site.register(TaxPayer)
admin.site.register(Agent)