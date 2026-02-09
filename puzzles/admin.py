from django.contrib import admin
from .models import Puzzle

class DifficultyFilter(admin.SimpleListFilter):
    """Custom filter for difficulty property"""
    title = 'difficulty'
    parameter_name = 'difficulty'

    def lookups(self, request, model_admin):
        return [
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('expert', 'Expert'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'easy':
            return queryset.filter(rating__lt=1200)
        elif self.value() == 'medium':
            return queryset.filter(rating__gte=1200, rating__lt=1800)
        elif self.value() == 'hard':
            return queryset.filter(rating__gte=1800, rating__lt=2400)
        elif self.value() == 'expert':
            return queryset.filter(rating__gte=2400)
        return queryset

@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('puzzle_id', 'rating', 'get_difficulty', 'nb_plays', 'created_at')
    list_filter = (DifficultyFilter, 'rating')
    search_fields = ('puzzle_id', 'themes', 'opening_tags')
    
    # Add a method to display difficulty in list view
    def get_difficulty(self, obj):
        return obj.difficulty
    get_difficulty.short_description = 'Difficulty'
    get_difficulty.admin_order_field = 'rating'  # Allow ordering by rating
    
    readonly_fields = ('get_difficulty',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('puzzle_id', 'fen', 'moves', 'rating')
        }),
        ('Statistics', {
            'fields': ('rating_deviation', 'popularity', 'nb_plays')
        }),
        ('Metadata', {
            'fields': ('themes', 'game_url', 'opening_tags')
        }),
        ('Calculated', {
            'fields': ('get_difficulty',)
        }),
    )