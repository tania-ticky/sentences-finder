# Generated by Django 2.0.5 on 2018-08-06 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentences_finder_name', models.CharField(max_length=264)),
                ('Last_name', models.CharField(max_length=264)),
                ('Email', models.EmailField(max_length=264, unique=True)),
            ],
        ),
    ]
