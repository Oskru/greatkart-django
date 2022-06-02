from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem


# Create your views here.

def _cart_id(request):
    """
    If the session key exists, return it. If it doesn't exist, create it and return it
    
    :param request: The request object that is passed to the view
    :return: The cart id is being returned.
    """
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart


def cart(request, total=0, quantity=0, cart_items=None):
    """
    It gets the cart, gets the cart items, calculates the total, quantity, tax, and grand total, and
    then passes all of that to the template
    
    :param request: The request object
    :param total: The total cost of all the items in the cart, defaults to 0 (optional)
    :param quantity: The total number of items in the cart, defaults to 0 (optional)
    :param cart_items: This is a list of all the items in the cart
    :return: The cart.html template is being rendered with the context.
    """

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (0.02 * total)
        grand_total = total + tax
    except ObjectNotExist:
        pass   # Just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)


def add_cart(request, product_id):
    """
    If the cart exists, add the product to the cart. If the cart doesn't exist, create a new cart and
    add the product to the cart
    
    :param request: The request object
    :param product_id: The id of the product that is being added to the cart
    :return: The cart_id is being returned.
    """
    product = Product.objects.get(id=product_id)  # Get the product

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request),
        )

    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id):
    """
    If the quantity of the product in the cart is greater than 1, then subtract 1 from the quantity and
    save the cart item. Otherwise, delete the cart item
    
    :param request: The request object is a Django object that contains metadata about the request sent
    to the server
    :param product_id: The id of the product to be removed from the cart
    :return: The cart_item.quantity is being returned.
    """

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


def remove_cart_item(request, product_id):
    """
    It gets the cart and the product, then deletes the cart item
    
    :param request: The request object is passed to the view by Django. It contains metadata about the
    request, including the HTTP method
    :param product_id: The id of the product to be removed from the cart
    :return: The cart_item is being deleted and the user is being redirected to the cart page.
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()

    return redirect('cart')