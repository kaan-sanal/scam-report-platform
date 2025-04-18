# Generated by Django 5.2 on 2025-04-17 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scamreport',
            name='report_type',
            field=models.CharField(choices=[('investment', 'Investment Scam'), ('shopping', 'Shopping Scam'), ('banking', 'Banking Scam'), ('social', 'Social Media Scam'), ('other', 'Other')], max_length=20),
        ),
        migrations.AlterField(
            model_name='scamreport',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
