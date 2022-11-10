# Generated by Django 4.0 on 2022-11-03 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0015_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='foodcartapp.product', verbose_name='Товар'),
        ),
    ]
