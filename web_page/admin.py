# web_page/admin.py
from django.contrib import admin
from django.core.management import call_command
from .models import ClubMember, ClubTournament, LeagueStatisticsField, Article, ArticleImage

@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "rating")
    actions = ["update_ratings_action"]

    def update_ratings_action(self, request, queryset):
        call_command("update_fide_ratings")
        self.message_user(request, "Ratings updated successfully.")

    update_ratings_action.short_description = "Апдејтуј ФИДЕ рејтинг према тренутним подацима."

admin.site.register(ClubTournament)
admin.site.register(LeagueStatisticsField)

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticleImageInline]
    list_display = ("title", "published_at", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title",)