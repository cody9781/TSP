# Generated by Django 5.2 on 2025-05-22 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_item_spec'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='temp',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
