from json import loads
from phonenumbers import is_possible_number, parse

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import CharField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError

from .models import Order, OrderItem, Product


class OrderDeserializer(Serializer):
    products = ListField()
    firstname = CharField()
    lastname = CharField()
    phonenumber = CharField()
    address = CharField()

    def validate_products(self, value):
        if not value:
            raise ValidationError(
                '\'products\': Этот список не может быть пустым'
            )

        try:
            for position in value:
                product_id = position['product']
                product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError(
                f'\'products\': Недопустимый первичный ключ \'{product_id}\''
            )

    def validate_firstname(self, value):
        if not value:
            raise ValidationError(
                '\'firstname\': Это поле не может быть пустым'
            )

    def validate_lastname(self, value):
        if not value:
            raise ValidationError(
                '\'lastname\': Это поле не может быть пустым'
            )

    def validate_address(self, value):
        if not value:
            raise ValidationError(
                '\'address\': Это поле не может быть пустым'
            )

    def validate_phonenumber(self, value):
        if not value:
            raise ValidationError(
                '\'phonenumber\': Это поле не может быть пустым'
            )

        phonenumber = parse(value)
        if not is_possible_number(phonenumber):
            raise ValidationError(
                '\'phonenumber\': Введен некорректный номер телефона'
            )


class OrderSerializer(Serializer):
    id = IntegerField(read_only=True)
    firstname = CharField(max_length=50)
    lastname = CharField(max_length=50)
    phonenumber = CharField()
    address = CharField(max_length=100)

    # def create(self, validated_data):
    #     return Order.objects.create(**validated_data)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    content = {}

    if request.method == 'POST':
        serializer = OrderDeserializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            address=request.data['address'],
            firstname=request.data['firstname'],
            lastname=request.data['lastname'],
            phonenumber=request.data['phonenumber']
        )

        for order_position in request.data['products']:
            product = Product.objects.get(pk=order_position['product'])

            OrderItem.objects.create(
                order=order,
                price=product.price,
                product=product,
                quantity=order_position['quantity']
            )

        serializer = OrderSerializer(order)
        content = JSONRenderer().render(serializer.data)
        
    return Response(content)
