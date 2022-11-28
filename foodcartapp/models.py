import copy
from collections import defaultdict

from django.db import models
from django.db.models import Sum, F, Prefetch
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy
from phonenumber_field.modelfields import PhoneNumberField

from location.geo_functions import get_or_create_locations, calc_distance


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_price_sum(self):
        return self.annotate(price_total=Sum(F('items__price') * F('items__quantity')))


    def get_locations(self, orders, menu_items):
        order_addresses = [order.address for order in orders]

        restaurant_addresses = [
            menu_item.restaurant.address
            for menu_item in menu_items
        ]

        return get_or_create_locations(
            [*order_addresses, *restaurant_addresses]
        )


    def with_available_restaurants(self):
        orders = self.prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
            )
        )

        menu_items = RestaurantMenuItem.objects.select_related(
            'restaurant',
            'product'
        ).filter(
            availability=True,
        )

        locations = self.get_locations(orders, menu_items)

        restaurants_by_items = defaultdict(list)

        for menu_item in menu_items:
            restaurants_by_items[menu_item.product.id].append(
                menu_item.restaurant
            )

        for order in orders:
            order_location = locations.get(order.address)
            
            order_restaurants_by_items = [
                copy.deepcopy(restaurants_by_items[order_item.product.id])
                for order_item in order.items.all()
            ]
            order.restaurants = list(
                set.intersection(*[
                    set(list) for list in order_restaurants_by_items
                ])
            )

            for restaurant in order.restaurants:
                restaurant_location = locations.get(restaurant.address)
                restaurant.distance = calc_distance(
                    order_location,
                    restaurant_location
                )

            order.restaurants = sorted(
                order.restaurants,
                key=lambda restaurant: restaurant.distance
            )

        return orders


class Order(models.Model):
    NEW = 'new'
    ASSEMBLE = 'assemble'
    COURIER = 'courier'
    FULFILLED = 'fulfilled'
    STATUS_CHOICES = [
        (NEW, 'Принят, ожидает подтверждение'),
        (ASSEMBLE, 'В сборке у ресторана'),
        (COURIER, 'У курьера'),
        (FULFILLED, 'Выполнен')
    ]
    CASH = 'cash'
    ONLINE = 'online'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличными'),
        (ONLINE, 'Онлайн')
    ]

    address = models.CharField(
        'Адрес',
        max_length=100
    )
    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField(
        'Мобильный номер',
        db_index=True
    )
    status = models.CharField(
        'Статус заказа',
        max_length=50,
        choices=STATUS_CHOICES,
        default=NEW,
        db_index=True
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        db_index=True,
        blank=True
    )
    comment = models.TextField(
        'Комментарий',
        blank=True
    )
    registered_at = models.DateTimeField(
        'Создано',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Подтвержено',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Доставлено',
        null=True,
        blank=True,
        db_index=True
    )
    cooking_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Готовящий ресторан'
    )

    objects = OrderQuerySet().as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Позиции заказа'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='Товар',
        related_name='order_items',
        null=True
    )
    price = models.DecimalField(
        'цена за шт',        
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name}, количество: {self.quantity}'
