# Generated by Django 4.1 on 2022-09-25 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("foodcartapp", "0002_order_orderitem"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orderitem",
            options={
                "verbose_name": "Позиция заказа",
                "verbose_name_plural": "Позиции заказа",
            },
        ),
    ]
