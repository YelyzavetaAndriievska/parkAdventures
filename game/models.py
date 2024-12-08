from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    castle = models.IntegerField(default=0)
    forge = models.IntegerField(default=0)
    magic = models.IntegerField(default=0)
    wood = models.IntegerField(default=0)
    iron = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    life = models.IntegerField(default=100)
    shield = models.IntegerField(default=0)
    magic_shield = models.IntegerField(default=0)
    dragon_life = models.IntegerField(default=100)
    username = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    sword = models.IntegerField(default=0)  # Поле для меча
    magic_sword = models.IntegerField(default=0)  # Поле для чарівного меча
    elixir = models.IntegerField(default=0)  # Поле для еліксиру
    flash = models.IntegerField(default=0)  # Поле для flash
    dragon_life = models.IntegerField(default=100)
    username = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    log = models.TextField()
    def __str__(self):
        return self.user.username


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('player', 'Player'),
        ('moderator', 'Moderator'),
        ('superadmin', 'SuperAdmin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='player')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class PlayerStatus(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    can_play = models.BooleanField(default=True)  # Дозвіл на гру

class ModeratorPermissions(models.Model):
    moderator = models.OneToOneField(
        User, on_delete=models.CASCADE, limit_choices_to={'userprofile__user_type': 'moderator'}
    )
    can_manage_players = models.BooleanField(default=True)  # Дозвіл на управління гравцями
