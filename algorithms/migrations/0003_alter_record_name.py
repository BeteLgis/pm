# Generated by Django 3.2.5 on 2022-05-04 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('algorithms', '0002_record_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]