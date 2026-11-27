
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fraze',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tekstas', models.CharField(max_length=500, unique=True)),
                ('sukurta', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Tyrimas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metodas', models.CharField(choices=[('bge', 'Tik BGE-M3'), ('raktas_bge', 'Raktas + BGE-M3')], max_length=20)),
                ('irenginys', models.CharField(choices=[('cpu', 'CPU'), ('cuda', 'GPU')], max_length=10)),
                ('rezultatai', models.JSONField(default=list)),
                ('trukme', models.FloatField(default=0)),
                ('sukurta', models.DateTimeField(auto_now_add=True)),
                ('frazes', models.ManyToManyField(to='paieska.fraze')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
