# Generated by Django 2.1.2 on 2018-11-25 03:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment_analyzer', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='new_rank',
            new_name='rank',
        ),
        migrations.RemoveField(
            model_name='page',
            name='old_rank',
        ),
    ]
