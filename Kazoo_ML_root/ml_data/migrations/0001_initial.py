# Generated by Django 3.0.2 on 2020-02-21 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('add_hubs', '0003_auto_20200221_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='ml_models',
            fields=[
                ('model_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('model_file', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='hubs_models',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('hub_ml_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ml_data.ml_models')),
                ('hub_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='add_hubs.hubs')),
            ],
        ),
    ]
