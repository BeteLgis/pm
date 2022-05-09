# Generated by Django 3.2.5 on 2022-05-07 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('algorithms', '0004_alter_record_json'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='error',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='name',
            field=models.CharField(default='', max_length=64),
        ),
    ]