# web_page/admin.py
from django.contrib import admin
from .models import ClubMember, ClubTournament

# Basic registration
admin.site.register(ClubMember)
admin.site.register(ClubTournament)