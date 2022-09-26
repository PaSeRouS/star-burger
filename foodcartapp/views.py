from json import loads

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
            error = True
        print('1', error)
        if not error:
            print('2', error)
            print(type(request.data['products']))
            if type(request.data['products']) != list:
                error = True

            print('3', error)
            if not request.data['products']:
                error = True

        print('4', error)
        if not error:
            order = Order.objects.create(
                address=request.data['address'],
                firstname=request.data['firstname'],
                lastname=request.data['lastname'],
                phonenumber=request.data['phonenumber']
            )

            for order_position in order_positions:
                product = Product.objects.get(pk=order_position['product'])

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=order_position['quantity']
                )
        else:
            error = {
                'error': 'products key not presented or not list'
            }
            
            result.append(error)
        
    return Response(result)
