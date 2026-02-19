from django.db import models
from django.conf import settings

# Create your models here.
class ClubMember(models.Model):
    first_name = models.CharField(
        'Име',
        max_length=100,
        help_text='Име члана тима'
    )
    
    last_name = models.CharField(
        'Презиме',
        max_length=100,
        help_text='Презиме члана тима'
    )

    fide_id = models.CharField(
        'ФИДЕ број',
        max_length=20,
        blank=True,
        null=True
    )

    rating = models.PositiveIntegerField(
        'Рејтинг',
        blank=True,
        null=True
    )
    
    description = models.TextField(
        'Опис',
        blank=True,
        null=True,
        help_text='Биографија и постигнућа члана'
    )
    
    image = models.ImageField(
        'Фотографија',
        upload_to=settings.TEAM_IMAGE_UPLOAD_PATH if hasattr(settings, 'TEAM_IMAGE_UPLOAD_PATH') else 'team/',
        blank=True,
        null=True,
        help_text='Окачи фотографију члана тима'
    )
    
    is_active = models.BooleanField(
        'Активан',
        default=True,
        help_text='Да ли је члан тима тренутно активан у лиги'
    )
    
    order = models.PositiveIntegerField(
        'Редослед',
        default=1,
        help_text='Редослед приказа на страници (мањи број=1; 0 за капитена; 1 за првотимце; 2 за остале)'
    )
    
    created_at = models.DateTimeField(
        'Креирано',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        'Ажурирано',
        auto_now=True
    )
    
    class Meta:
        ordering = ['order', 'rating', 'first_name', 'last_name']
        verbose_name = 'Члан тима'
        verbose_name_plural = 'Чланови тима'
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name}  ({self.rating})"
    
    @property
    def full_name(self):
        """Return full name of team member"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def has_image(self):
        """Check if team member has an image"""
        return bool(self.image)
    
class ClubTournament(models.Model):

    class Status(models.IntegerChoices):
        UPCOMING = 0, 'У најави'
        REGISTRATION = 1, 'Отворена регистрација'
        ONGOING = 2, 'У току'
        COMPLETED = 3, 'Завршен'

    name = models.CharField(
        'Назив',
        max_length=100,
        help_text='Назив турнира'
    )

    description = models.TextField(
        'Опис турнира',
        help_text='Опис турнира'
    )

    start_date = models.DateField('Почетак')
    end_date = models.DateField('Крај')

    rounds = models.PositiveIntegerField('Кола', default=0, help_text='Број кола')
    time_control_mins = models.PositiveIntegerField('Време', default=0, help_text='Време(минути)')
    increment = models.PositiveIntegerField('Додатак', default=0, help_text='Додатак по потезу(секунде)')

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.UPCOMING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', 'end_date']
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турнири'

    def time_control_display(self):
        return f"{self.time_control_mins}+{self.increment}"

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Наслов"
    )

    content = models.TextField(
        verbose_name="Садржај"
    )

    featured_image = models.ImageField(
        upload_to="articles/featured/",
        blank=True,
        null=True,
        verbose_name="Naslovna slika"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Креирано"
    )

    published_at = models.DateTimeField(
        verbose_name="Датум објаве",
        blank=True,
        null=True
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name="Објављено"
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Чланак"
        verbose_name_plural = "Чланци"

    def save(self, *args, **kwargs):
        # If published_at not set, use created_at
        if not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="articles/",
        verbose_name="Слика"
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Опис слике"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.article.title}"


class LeagueStatisticsField(models.Model):
    title = models.CharField(
        'Назив статистичког податка',
        max_length=100,
        help_text='Назив статистичког податка'
    )

    value = models.FloatField(
        'Вредност статистичког податка',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        'Активан',
        default=True,
        help_text='Да ли се податак тренутно приказује на страници'
    )
    
    order = models.PositiveIntegerField(
        'Редослед',
        default=0,
        help_text='Редослед приказа на страници (мањи број=1)'
    )
    
    created_at = models.DateTimeField(
        'Креирано',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        'Ажурирано',
        auto_now=True
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Статистички податак о лиги'
        verbose_name_plural = 'Статистички подаци о лиги'
    
    def __str__(self):
        return f"{self.title}: {self.value}"