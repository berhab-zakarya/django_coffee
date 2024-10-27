
from django.shortcuts import render,redirect
from django.contrib import messages
from products.models import Product
from orders1.models import Order,OrderDetails,Payment
from django.utils import timezone
def add_to_cart(request):
    if 'pro_id' in request.GET and 'qty' in request.GET and 'price' in request.GET and request.user.is_authenticated and not request.user.is_anonymous:
        print(request.user)
        pro_id = request.GET['pro_id']
        qty = request.GET['qty']
        order = Order.objects.all().filter(user=request.user,
                                           is_finished=False,)
        if Product.objects.all().filter(id=pro_id).exists():
            product = Product.objects.get(id=pro_id)
        else:
            redirect('products ')
        if order:
            #messages.success(request,'There an old order!')
            old_order = Order.objects.get(user=request.user,is_finished=False)
            if OrderDetails.objects.all().filter(order=old_order,product=product).exists():
                orderdetails = OrderDetails.objects.get(order=old_order,product=product)
                orderdetails.quantity += int(qty)
                orderdetails.save()
            else:
                orderdetails = OrderDetails.objects.create(
                    product=product,
                    order = old_order,
                    price = product.price,
                    quantity = qty
                )
            messages.success(request,'Was added to cart for old order!') 
        else:
            #messages.success(request,'New Order')
            new_order = Order()
            new_order.user = request.user
            new_order.order_date = timezone.now()
            new_order.is_finished = False
            new_order.save()
            order_details = OrderDetails.objects.create(
                product=product,
                order = new_order,
                price = product.price,
                quantity = qty
            )
            messages.success(request,'Was added to cart for new order!')
        
        return redirect('/products/'+request.GET['pro_id'])
    else:
        if 'pro_id' in request.GET:
            messages.error(request,'You must be logged in!')
            return redirect('/products/'+request.GET['pro_id'])
        else:
            return redirect('products')

def cart(request):
    context = None
    if  request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(user=request.user,is_finished=False).exists():
            order = Order.objects.get(user=request.user,is_finished=False)
            orders_details = OrderDetails.objects.all().filter(order = order)
            total = 0
            for sub in orders_details:
                total+= sub.price * sub.quantity
            context = {
                'order':order,
                'orderdetails':orders_details,
                'total':total,
            }
    return render(request,'orders/cart.html',context)


def remove_from_cart(request,orderdetails_id):
    if request.user.is_authenticated and not request.user.is_anonymous:
        orderdetails = OrderDetails.objects.get(id=orderdetails_id)
        if orderdetails.order.user.id == request.user.id:
            orderdetails.delete() 
    return redirect('cart')
    
def add_qty(request,orderdetails_id):
    if isAuthenticated(request) and orderdetails_id:
        orderdetails = OrderDetails.objects.get(id=orderdetails_id)
        orderdetails.quantity +=1
        orderdetails.save()
    return redirect('cart')

def sub_qty(request,orderdetails_id):
    if isAuthenticated(request) and orderdetails_id:
        orderdetails = OrderDetails.objects.get(id=orderdetails_id)
        if orderdetails.quantity > 1 : orderdetails.quantity -=1
        orderdetails.save()
    return redirect('cart')

def isAuthenticated(request):
    return  request.user.is_authenticated and not request.user.is_anonymous


def payment(request):
    context = None
    ship_address = None
    ship_phone = None
    card_number = None
    expire = None
    csv = None
    is_added = None
    
    if request.method == 'POST' and 'btnpayment' in request.POST:
        ship_address = request.POST.get('ship_address', '')
        ship_phone = request.POST.get('ship_phone', '')
        card_number = request.POST.get('card_number', '')
        expire = request.POST.get('expire', '')
        csv = request.POST.get('csv', '')
        if isAuthenticated(request):
            if Order.objects.all().filter(user=request.user,is_finished=False):
                order = Order.objects.get(user=request.user,is_finished=False)
                payment = Payment(
                    order=order,
                    shipment_address=ship_address,
                    shipment_phone=ship_phone,
                    card_number=card_number,
                    expire=expire,
                    security_code = csv
                )
                payment.save()
                order.is_finished = True
                order.save()
                is_added = True
                messages.success(request,'Your order is finished! ')
        context = {
         'ship_address': ship_address,
            'ship_phone': ship_phone,
         'card_number': card_number,
            'expire': expire,
         'csv_code': csv,
         'is_added': is_added,
    }
    else:
        if  request.user.is_authenticated and not request.user.is_anonymous:
            if Order.objects.all().filter(user=request.user,is_finished=False).exists():
                order = Order.objects.get(user=request.user,is_finished=False)
                orders_details = OrderDetails.objects.all().filter(order = order)
                total = 0
                for sub in orders_details:
                    total+= sub.price * sub.quantity
                context = {
                    'order':order,
                    'orderdetails':orders_details,
                    'total':total,
                }
    return render(request,'orders/payment.html',context)


def show_orders(request):
    context = None
    if isAuthenticated(request):
        all_orders = Order.objects.filter(user=request.user)
        total_price = 0
        for order in all_orders:
            order_details = OrderDetails.objects.filter(order=order)
            for detail in order_details:
                total_price += detail.price * detail.quantity
        
        context = {
            'all_orders': all_orders,
            'total_price': total_price
        }
    return render(request, 'orders/show_orders.html', context)
