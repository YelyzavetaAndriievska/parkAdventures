# Generated by Django 5.1.2 on 2024-12-05 17:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('castle', models.IntegerField(default=0)),
                ('forge', models.IntegerField(default=0)),
                ('magic', models.IntegerField(default=0)),
                ('wood', models.IntegerField(default=0)),
                ('iron', models.IntegerField(default=0)),
                ('gold', models.IntegerField(default=0)),
                ('life', models.IntegerField(default=100)),
                ('shield', models.IntegerField(default=0)),
                ('magic_shield', models.IntegerField(default=0)),
                ('sword', models.IntegerField(default=0)),
                ('magic_sword', models.IntegerField(default=0)),
                ('elixir', models.IntegerField(default=0)),
                ('flash', models.IntegerField(default=0)),
                ('dragon_life', models.IntegerField(default=100)),
                ('username', models.CharField(max_length=100)),
                ('score', models.IntegerField(default=0)),
                ('log', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
