from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Puzzle(models.Model):
    puzzle_id = models.CharField(max_length=20, unique=True)
    fen = models.TextField(help_text="Forsyth-Edwards Notation")
    moves = models.TextField(help_text="Comma-separated UCI moves")
    rating = models.IntegerField(default=1500, validators=[MinValueValidator(0), MaxValueValidator(3000)])
    rating_deviation = models.IntegerField(default=100)
    popularity = models.IntegerField(default=50)
    nb_plays = models.IntegerField(default=0)
    themes = models.TextField(blank=True)
    game_url = models.URLField(blank=True)
    opening_tags = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def difficulty(self):
        """Calculate difficulty based on rating"""
        if self.rating < 1200:
            return 'easy'
        elif self.rating < 1800:
            return 'medium'
        elif self.rating < 2400:
            return 'hard'
        else:
            return 'expert'
    
    @property
    def move_list(self):
        """Parse moves string into list"""
        return [move.strip() for move in self.moves.split(',')]
    
    @property
    def theme_list(self):
        """Parse themes string into list"""
        return [theme.strip() for theme in self.themes.split(',')] if self.themes else []
    
    def __str__(self):
        return f"Puzzle {self.puzzle_id} ({self.rating})"
    
    class Meta:
        ordering = ['-rating', 'puzzle_id']