# Generated by Django 5.0.7 on 2024-08-19 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0002_itementry_fiber_itementry_sodium_itementry_sugar_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userprofile',
            unique_together={('name', 'age')},
        ),
    ]
