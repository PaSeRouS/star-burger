# Generated by Django 4.0 on 2022-11-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0016_alter_orderitem_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default=1, verbose_name='Комментарий'),
            preserve_default=False,
        ),
    ]
