# Generated by Django 5.1.2 on 2024-11-30 21:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_initial'),
        ('invitation', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitationmodel',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='company.company'),
        ),
    ]
