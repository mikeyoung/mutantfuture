# Generated by Django 5.0.1 on 2024-01-21 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutantfuture', '0018_alter_race_mental_mutations_roll_str_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='random_beneficial_any_roll_str',
            field=models.CharField(default=0, max_length=12),
        ),
    ]
