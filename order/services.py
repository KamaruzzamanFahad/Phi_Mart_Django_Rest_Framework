from django.db import transaction
from order.models import Cart, Order, OrderItem
from rest_framework.exceptions import PermissionDenied, ValidationError
class OrderServices:
    @staticmethod
    def create_order(user_id, cart_id):
        with transaction.atomic(): # use for ghotle sobkicho ghotbe nahoy kichoi hobe na.
            cart = Cart.objects.get(pk=cart_id)
            cart_items = cart.items.select_related('product').all()

            total_price = sum([item.product.price * item.quantity for item in cart_items])

            order = Order.objects.create(user_id =user_id, total_price =total_price)

            order_item = [
                OrderItem(
                    order=order,
                    product = item.product,
                    price = item.product.price,
                    quantity = item.quantity,
                    total_price = item.product.price * item.quantity
                )
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_item)

            cart.delete()
            return order
        
    @staticmethod
    def cancle_order(order, user):
        if user.is_staff:
            order.status = Order.CANCELLED
            order.save()
            return order
        
        if order.user != user:
            raise PermissionDenied("You do not have permissiton to cancle this order")
        
        if order.status == Order.NOT_PAID:
            order.status = Order.CANCELLED
            order.save()
            return order
        else:
            ValidationError("You can only cancle Pending order")