from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_type', models.CharField(default='Export', max_length=50)),
                ('category', models.CharField(max_length=200)),
                ('partner_country', models.CharField(default='Ukraine', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('date', models.DateField()),
            ],
        ),
    ]
