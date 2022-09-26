from json import loads
from phonenumbers import is_possible_number, parse

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


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
    # print(type(request.data['products']))
    result = []

    if request.method == 'POST':
        error = False

        try:
            order_positions = request.data['products']
        except KeyError:
            result.append({
                'error': '\'products\': Обязательное поле'
            })
            error = True

        try:
            firstname = request.data['firstname']
        except KeyError:
            result.append({
                'error': '\'firstname\': Обязательное поле'
            })
            error = True

        try:
            lastname = request.data['lastname']
        except KeyError:
            result.append({
                'error': '\'lastname\': Обязательное поле'
            })
            error = True

        try:
            phonenumber = request.data['phonenumber']
        except KeyError:
            result.append({
                'error': '\'phonenumber\': Обязательное поле'
            })
            error = True

        try:
            address = request.data['address']
        except KeyError:
            result.append({
                'error': '\'address\': Обязательное поле'
            })
            error = True

        if not error:
            if type(request.data['products']) != list:
                result.append({
                    'error': 'products: Ожидался list со значениями, но был получен \'str\''
                })

                error = True

            if type(request.data['firstname']) != str:
                result.append({
                    'error': '\'firstname\': Не является действительной строкой'
                })

                error = True

            if type(request.data['lastname']) != str:
                result.append({
                    'error': '\'lastname\': Не является действительной строкой'
                })

                error = True

            if type(request.data['address']) != str:
                result.append({
                    'error': '\'address\': Не является действительной строкой'
                })

                error = True

            if not request.data['products']:
                result.append({
                    'error': '\'products\': Этот список не может быть пустым'
                })

                error = True

            if not request.data['firstname']:
                result.append({
                    'error': '\'firstname\': Это поле не может быть пустым'
                })

                error = True

            if not request.data['lastname']:
                result.append({
                    'error': '\'lastname\': Это поле не может быть пустым'
                })

                error = True

            if not request.data['phonenumber']:
                result.append({
                    'error': '\'phonenumber\': Это поле не может быть пустым'
                })

                error = True

            if not request.data['address']:
                result.append({
                    'error': '\'address\': Это поле не может быть пустым'
                })

                error = True

            try:
                for order_position in order_positions:
                    product_id = order_position['product']
                    product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                result.append({
                    'error': f'\'products\': Недопустимый первичный ключ \'{product_id}\''
                })

                error = True

            if phonenumber:
                parsed_phonenumber = parse(phonenumber)
                if not is_possible_number(parsed_phonenumber):

                    result.append({
                        'error': '\'phonenumber\': Введен некорректный номер телефона'
                    })

                    error = True


        if not error:
            order = Order.objects.create(
                address=address,
                firstname=firstname,
                lastname=lastname,
                phonenumber=phonenumber
            )

            for order_position in order_positions:
                product = Product.objects.get(pk=order_position['product'])

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=order_position['quantity']
                )
        
    return Response(result)
