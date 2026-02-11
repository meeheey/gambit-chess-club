from django.db import models
from django.conf import settings

# Create your models here.
class ClubMember(models.Model):
    first_name = models.CharField(
        'Ime',
        max_length=100,
        help_text='Ime člana tima'
    )
    
    last_name = models.CharField(
        'Prezime',
        max_length=100,
        help_text='Prezime člana tima'
    )
    
    rating = models.CharField(
        'Rejting',
        max_length=4,
        help_text='FIDE rejting za standardni šah'
    )
    
    description = models.TextField(
        'Opis',
        blank=True,
        null=True,
        help_text='Biografija i postignuća člana'
    )
    
    image = models.ImageField(
        'Fotografija',
        upload_to=settings.TEAM_IMAGE_UPLOAD_PATH if hasattr(settings, 'TEAM_IMAGE_UPLOAD_PATH') else 'team/',
        blank=True,
        null=True,
        help_text='Upload-ujte fotografiju člana tima'
    )
    
    is_active = models.BooleanField(
        'Aktivan',
        default=True,
        help_text='Da li je član tima trenutno aktivan u ligi'
    )
    
    order = models.PositiveIntegerField(
        'Redosled',
        default=0,
        help_text='Redosled prikaza na stranici (manji broj = prvi)'
    )
    
    created_at = models.DateTimeField(
        'Kreirano',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        'Ažurirano',
        auto_now=True
    )
    
    class Meta:
        ordering = ['order', 'rating', 'first_name', 'last_name']
        verbose_name = 'Član tima'
        verbose_name_plural = 'Članovi tima'
    
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
        UPCOMING = 0, 'Upcoming'
        REGISTRATION = 1, 'Registration Open'
        ONGOING = 2, 'Ongoing'
        COMPLETED = 3, 'Completed'

    name = models.CharField(
        'Naziv',
        max_length=100,
        help_text='Naziv turnira'
    )

    description = models.TextField(
        'Opis turnira',
        help_text='Opis turnira'
    )

    start_date = models.DateField('Početak')
    end_date = models.DateField('Kraj')

    rounds = models.PositiveIntegerField('Kola', default=0, help_text='Broj kola')
    time_control_mins = models.PositiveIntegerField('Vreme', default=0, help_text='Vreme(minuti)')
    increment = models.PositiveIntegerField('Dodatak', default=0, help_text='Dodatak po potezu(sekunde)')

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.UPCOMING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', 'end_date']
        verbose_name = 'Turnir'
        verbose_name_plural = 'Turniri'

    def time_control_display(self):
        return f"{self.time_control_mins}+{self.increment}"

    def __str__(self):
        return self.name