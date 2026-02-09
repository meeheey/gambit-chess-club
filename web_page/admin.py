# web_page/admin.py
from django.contrib import admin
from .models import ClubMember

# Basic registration
admin.site.register(ClubMember)