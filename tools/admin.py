from django.contrib import admin

from .models import BorrowRequest, Tool

admin.site.register(Tool)
admin.site.register(BorrowRequest)