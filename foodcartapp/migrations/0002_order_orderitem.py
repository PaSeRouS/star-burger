# Generated by Django 4.1 on 2022-09-25 19:49

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("foodcartapp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.CharField(max_length=100, verbose_name="Адрес")),
                ("name", models.CharField(max_length=50, verbose_name="Имя")),
                ("surname", models.CharField(max_length=50, verbose_name="Фамилия")),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        db_index=True,
                        max_length=128,
                        region=None,
                        verbose_name="Мобильный номер",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заказ",
                "verbose_name_plural": "Заказы",
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count", models.IntegerField(verbose_name="Количество")),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="foodcartapp.order",
                        verbose_name="Позиции заказа",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="foodcartapp.product",
                        verbose_name="Товар",
                    ),
                ),
            ],
        ),
    ]
