import os
import random
from random import randint
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from django.core.files import File
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from myproject.views import food_add
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import FoodItem,OrderItem
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone
from .forms import AddRestoForm
from .models import AddResto,Booking_resto

from django.http import HttpResponse
import os
from django.conf import settings
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


from .models import SuperRegister
from .forms import SuperRegisterForm, SuperLoginForm


import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Cart, Order_pay, Registration, FoodItem
from datetime import date

import json
from django.db.models import Sum, F
from django.db.models.functions import TruncDate
from .forms import ContactMessageForm
from .models import ContactMessage
from django.core.mail import EmailMessage
from .forms import EmailForm 

from .forms import (
    RegistrationForm, LoginForm,
    ForgotPasswordForm, OTPForm, ResetPasswordForm,
    FoodItemForm, AdminOwner,AdminLoginForm, AdminOwnerRegisterForm
)
from .models import Registration, FoodItem

from .models import AdminOwner, FoodItem, Discount,Order
from .forms import DiscountForm 
from django.shortcuts import render, redirect
from .models import Registration
from datetime import datetime

from django.contrib.auth.signals import user_logged_in
from .models import Cart, FoodItem

def profile_view(request):
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        user = Registration.objects.filter(id=user_id).first()

    return render(request, 'profile.html', {'user': user})


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = Registration.objects.get(id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.city = request.POST.get('city')
        user.gender = request.POST.get('gender')
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        
        

        if user.profile_image:
            request.session['image'] = user.profile_image.url
        else:
            request.session['image'] = None

        return redirect('profile_page')  

    return render(request, 'edit_profile.html', {'user': user})


from django.shortcuts import render, redirect
from .models import Registration, Booking_resto

def my_booking(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = Registration.objects.get(id=user_id)

    user_bookings = Booking_resto.objects.filter(contact_number=user.phone).select_related('restaurant')

    return render(request, 'my_booking.html', {
        'bookings': user_bookings,
        'user': user,
    })


def send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"success": False, "message": "Email is required"})

        request.session["registration_data"] = request.POST.dict()
        
        if "profile_image" in request.FILES:
            uploaded_file = request.FILES["profile_image"]
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_filename = f"{now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
            temp_path = os.path.join(temp_dir, temp_filename)
            with open(temp_path, "wb+") as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
            request.session["temp_profile_image"] = temp_path

        otp = str(random.randint(100000, 999999))
        request.session["otp"] = otp
        request.session["email_for_otp"] = email

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({"success": True, "message": "OTP sent successfully"})
    
    return JsonResponse({"success": False, "message": "Invalid request"})


def register_page(request):
    form = RegistrationForm()

    if request.method == "POST":
        if "create_user" in request.POST:
            user_otp = request.POST.get("otp")
            session_otp = request.session.get("otp")
            data = request.session.get("registration_data")

            if user_otp == session_otp and data:
                form = RegistrationForm(data)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.password = make_password(data["password"])

                    temp_image_path = request.session.get("temp_profile_image")
                    if temp_image_path and os.path.exists(temp_image_path):
                        with open(temp_image_path, "rb") as f:
                            instance.profile_image.save(os.path.basename(temp_image_path), File(f))
                        os.remove(temp_image_path)

                    instance.save()

                    for key in ["registration_data", "otp", "email_for_otp", "temp_profile_image"]:
                        request.session.pop(key, None)

                    messages.success(request, "Registration successful! Please log in.")
                    return redirect("login_page")
                else:
                    messages.error(request, "Invalid form data. Try again.")

            else:
                messages.error(request, "Invalid OTP or expired session. Please try again.")

    return render(request, "register.html", {"form": form})



def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = Registration.objects.get(email=email)
                
                if check_password(password, user.password):
                    request.session['user_name'] = user.first_name + ' ' + user.last_name
                    request.session['user_id'] = user.id
                    request.session['image'] = user.profile_image.url if user.profile_image else None
                    request.session['user_phone'] = user.phone    

                    messages.success(request, f"Welcome {user.first_name}!")
                    return redirect('/')
                else:
                    messages.error(request, "Incorrect password!")
            except Registration.DoesNotExist:
                messages.error(request, "User with this email does not exist!")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



def logout_user(request):
    request.session.pop('user_name', None)
    request.session.pop('user_id', None)
    request.session.pop('image', None)
    
    request.session.pop('cart', None)
    
    messages.success(request, "You have successfully logged out.")
    return redirect('/')


def success(request):
    return render(request, 'success.html')

def homepage(request):
    data={'title' : 'Wel-Come Zomato'}
    return render(request,"homepage.html",data)

def about(request):
    data={'title' : 'About-Us'}

    return render(request,"aboutus.html",data)

def contact(request):
    data={'title' : 'Contact-Us'}

    return render(request,"contactus.html",data)

def menu(request):
    data={'title' : 'Menu'}

    return render(request,"menu.html",data)

def restaurant(request):
    data={'title' : 'Menu'}

    return render(request,"restaurant.html",data)



def forgot_password(request):
    
    
    if 'otp_sent' not in request.session:
        request.session['otp_sent'] = False
        request.session['otp_verified'] = False
    
    
    
    if request.method == 'POST' and not request.session['otp_sent']:
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Registration.objects.get(email=email)
                otp = randint(100000, 999999)
                request.session['reset_email'] = email
                request.session['otp_code'] = str(otp)
                request.session['otp_sent'] = True
                request.session['otp_verified'] = False               
                
                send_mail(
                    'Your OTP for Foodeat Password Reset',
                    f'Your OTP is: {otp}',
                    'noreply@foodeat.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f"OTP sent to {email}")
                return redirect('forgot_password')
            except Registration.DoesNotExist:
                messages.error(request, "Email not registered")
   
    
    elif request.method == 'POST' and request.session.get('otp_sent') and not request.session.get('otp_verified'):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            if otp_input == request.session.get('otp_code'):
                request.session['otp_verified'] = True
                messages.success(request, "OTP verified. Please set your new password.")
                return redirect('forgot_password')
            else:
                messages.error(request, "Invalid OTP. Try again.")    
  
    
    elif request.method == 'POST' and request.session.get('otp_verified'):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            email = request.session.get('reset_email')
            try:
                user = Registration.objects.get(email=email)
                user.password = make_password(password)
                user.save()
                messages.success(request, "Password reset successful!")               
                
                
                request.session.pop('otp_sent')
                request.session.pop('otp_verified')
                request.session.pop('otp_code')
                request.session.pop('reset_email')
                return redirect('/login/')
            except Registration.DoesNotExist:
                messages.error(request, "Something went wrong. Try again.")   
   
    
    if not request.session.get('otp_sent'):
        form = ForgotPasswordForm()
    elif request.session.get('otp_sent') and not request.session.get('otp_verified'):
        form = OTPForm()
    else:
        form = ResetPasswordForm()
    
    return render(request, "forgot_password.html", {'form': form})

    

def add_to_cart(request, food_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('/login')

    user = get_object_or_404(Registration, id=user_id)

    try:
        food = FoodItem.objects.get(id=food_id)
    except FoodItem.DoesNotExist:
        messages.error(request, "Food item does not exist.")
        return redirect('/menu')

    cart_item, created = Cart.objects.get_or_create(user=user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{food.food_name} added to your cart.")
    return redirect('cart_page')

def cart_page(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Please log in to view your cart.")
        return redirect('/login')

    user = get_object_or_404(Registration, id=user_id)
    cart_items = Cart.objects.filter(user=user)

    total = 0
    total_after_discount = 0
    today = timezone.now().date()

    for item in cart_items:
        item.subtotal = item.food.price * item.quantity

        discount = (
            Discount.objects.filter(
                product=item.food,
                active=True,
                start_date__lte=today,
                end_date__gte=today
            )
            .order_by('-discount_percentage')
            .first()
        )

        item.discount_percent = discount.discount_percentage if discount else 0
        item.final_price = item.subtotal - (item.subtotal * item.discount_percent / 100)

        total += item.subtotal
        total_after_discount += item.final_price

    discount_difference = total - total_after_discount

    context = {
        'cart_items': cart_items,
        'total': total,
        'total_after_discount': total_after_discount,
        'discount_difference': discount_difference,  
    }
    return render(request, 'cart.html', context)


def cart_view(request):
    user_id = request.session.get('user_id') 
    if not user_id:
        cart_items = []
    else:
        user = get_object_or_404(Registration, id=user_id)
        cart_items = Cart.objects.filter(user=user)

    return render(request, 'cart.html', {'cart_items': cart_items})


def merge_session_cart(sender, user, request, **kwargs):
    session_cart = request.session.get('cart', {})
    for food_id_str, quantity in session_cart.items():
        food = FoodItem.objects.get(id=int(food_id_str))
        cart_item, created = Cart.objects.get_or_create(
            user=user,     
            food=food,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
    request.session['cart'] = {}

user_logged_in.connect(merge_session_cart)

def increase_quantity(request, cart_item_id):
    """ Increases the quantity of a specific item in the database cart. """
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
    messages.info(request, f"Updated quantity for {cart_item.food.food_name}.")
    return redirect('cart_page')

def decrease_quantity(request, cart_item_id):
    """ Decreases the quantity of a specific item, removing it if quantity is 1. """
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.info(request, f"Updated quantity for {cart_item.food.food_name}.")
    else:
        cart_item.delete()
        messages.warning(request, f"{cart_item.food.food_name} has been removed from your cart.")
    return redirect('cart_page')

def remove_from_cart(request, cart_item_id):
    """ Removes an item completely from the cart, regardless of quantity. """
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    food_name = cart_item.food.food_name
    cart_item.delete()
    messages.warning(request, f"{food_name} has been removed from your cart.")
    return redirect('cart_page')


def restaurant_list(request):
    restaurants = AddResto.objects.all()
    return render(request, "restaurant_view.html", {"restaurants": restaurants})


def book_table(request, restaurant_id):
    restaurant = get_object_or_404(AddResto, id=restaurant_id)

    if request.method == "POST":
        name = request.POST.get("customer_name")
        contact = request.POST.get("contact_number")
        members = request.POST.get("members")

        Booking_resto.objects.create(
            restaurant=restaurant,
            customer_name=name,
            contact_number=contact,
            members=members
        )
        messages.success(request, f"Your table has been booked at {restaurant.name}!")
        return redirect("restaurant_list")

    return redirect("restaurant_list")  


def edit_booking(request, id):
    booking = get_object_or_404(Booking_resto, id=id)

    if request.method == "POST":
        booking.customer_name = request.POST['customer_name']
        booking.contact_number = request.POST['contact_number']
        booking.address = request.POST['address']
        booking.members = request.POST['members']
        booking.booking_time = request.POST['booking_time']
        booking.save()
        return redirect('my_booking') 

    return render(request, 'edit_booking.html', {'booking': booking})

def delete_booking(request, id):
    booking = get_object_or_404(Booking_resto, id=id)
    booking.delete()
    return redirect('my_booking')



def checkout_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first.")
        return redirect('/login')

    user = get_object_or_404(Registration, id=user_id)
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('/menu')

    total_amount = 0
    for item in cart_items:
        discount = item.food.discounts.filter(active=True).first()
        price = item.food.price
        if discount:
            price -= price * (Decimal(discount.discount_percentage) / 100)
        total_amount += price * item.quantity

    total_amount_paise = int(total_amount * 100) 

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
    DATA = {
        "amount": total_amount_paise,
        "currency": "INR",
        "payment_capture": 1, 
    }
    razorpay_order = client.order.create(data=DATA)

    order = Order_pay.objects.create(
        user=user,
        razorpay_order_id=razorpay_order['id'],
        amount=total_amount,
        status='created'
    )

    context = {
        "cart_items": cart_items,
        "total": total_amount,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "callback_url": "/paymenthandler/",
    }
    return render(request, "checkout.html", context)

@csrf_exempt
def payment_success(request):
    import json
    data = json.loads(request.body)

    razorpay_order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")

    try:
        order_payment = Order_pay.objects.get(razorpay_order_id=razorpay_order_id)
        order_payment.payment_id = payment_id
        order_payment.status = "paid"
        order_payment.save()

        user = order_payment.user
        cart_items = Cart.objects.filter(user=user)
        total_amount = sum(item.food.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            final_amount=total_amount,
            delivery_name=user.full_name if hasattr(user, 'full_name') else user.username,
            delivery_phone=user.phone if hasattr(user, 'phone') else '',
            delivery_address=user.address if hasattr(user, 'address') else '',
            status='paid'
        )

        cart_items.delete()
    except Order_pay.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Order not found"})

    return JsonResponse({"status": "success"})


def paymenthandler(request):
    payment_id = request.GET.get('payment_id')
    razorpay_order_id = request.GET.get('order_id')

    order_payment = get_object_or_404(Order_pay, razorpay_order_id=razorpay_order_id)

    order_payment.payment_id = payment_id
    order_payment.status = 'paid'
    order_payment.save()

    user = order_payment.user
    cart_items = Cart.objects.filter(user=user)

    total_amount = sum(item.food.price * item.quantity for item in cart_items)
    total_discount = 0
    final_amount = total_amount - total_discount

    order = Order.objects.create(
        user=None, 
        total_amount=total_amount,
        total_discount=total_discount,
        final_amount=final_amount,
        delivery_name=f"{user.first_name} {user.last_name}",
        delivery_phone=user.phone,
        delivery_address=user.city or "Not provided",
        status='paid'
    )

    cart_items.delete()

    messages.success(request, "Payment successful! Your order has been placed.")
    return redirect('/menu')


def my_orders(request):
    user_id = request.session.get('user_id') 
    if not user_id:
        return redirect('/login')
    
    user = Registration.objects.get(id=user_id)
    orders = Order_pay.objects.filter(user=user)
    return render(request, 'my_orders.html', {'orders': orders})


def download_bill(request, order_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login/')

    user = get_object_or_404(Registration, id=user_id)
    order = get_object_or_404(Order_pay, id=order_id, user=user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')

        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            p.drawImage(logo, 50, height - 90, width=80, height=60, mask='auto')
        else:
            p.setFillColor(colors.red)
            p.drawString(50, height - 70, "[Logo Missing]")
    except Exception as e:
        p.setFillColor(colors.red)
        p.drawString(50, height - 70, f"[Logo Error: {e}]")

    p.setFillColorRGB(0.9, 0.3, 0.3)
    p.rect(0, height - 80, width, 80, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2 + 30, height - 50, "🍽️ ZOMATO FOOD ORDER BILL")

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, height - 120, "Customer Details:")
    p.setFont("Helvetica", 11)
    p.drawString(70, height - 140, f"Name: {user.first_name} {user.last_name}")
    p.drawString(70, height - 155, f"Email: {user.email}")

    y = height - 210
    table_data = [
        ["Field", "Details"],
        ["Order ID", order.razorpay_order_id or "—"],
        ["Payment ID", order.payment_id or "—"],
        ["Amount Paid (₹)", f"{order.amount:.2f}"],
        ["Status", order.status],
        ["Order Date", order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
    ]

    x_start, x_end = 50, width - 50
    row_height = 25
    col_split = x_start + (x_end - x_start) * 0.4

    p.setFillColorRGB(0.95, 0.4, 0.4)
    p.rect(x_start, y, x_end - x_start, row_height, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x_start + 10, y + 7, "Field")
    p.drawString(col_split + 10, y + 7, "Details")

    p.setFillColor(colors.black)
    p.setFont("Helvetica", 11)
    for i, (field, value) in enumerate(table_data[1:], start=1):
        row_y = y - i * row_height
        p.rect(x_start, row_y, x_end - x_start, row_height, fill=0)
        p.drawString(x_start + 10, row_y + 7, field)
        p.drawString(col_split + 10, row_y + 7, str(value))

    y -= (len(table_data) + 1) * row_height + 20
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(colors.darkgray)
    text = (
        "Thank you for choosing Zomato! We hope you enjoyed your meal.\n"
        "For feedback or issues, please contact support@zomato.com.\n\n"
        "This is a system-generated invoice — no signature required."
    )
    text_obj = p.beginText(70, y)
    for line in text.split("\n"):
        text_obj.textLine(line)
    p.drawText(text_obj)

    p.setFont("Helvetica", 9)
    p.setFillColor(colors.gray)
    p.drawCentredString(width / 2, 50, "© 2025 Zomato India Pvt. Ltd. | www.zomato.com")

    p.showPage()
    p.save()

    return response


    #--------------------------- Admin Restaurant---------------------------
def admin_profile(request):
    if 'admin_id' not in request.session:
        return redirect('adminlogin')
    admin_user = AdminOwner.objects.get(id=request.session['admin_id'])
    return render(request, 'admin_owner/admin_profile.html', {'admin_user': admin_user})


def admin_profile_edit(request, admin_id):
    admin_user = get_object_or_404(AdminOwner, id=admin_id)

    if request.method == "POST":
        admin_user.full_name = request.POST.get('full_name', '').strip()
        admin_user.restaurant_name = request.POST.get('restaurant_name', '').strip()
        admin_user.email = request.POST.get('email', '').strip()

        if 'profile_image' in request.FILES and request.FILES['profile_image']:
            admin_user.profile_image = request.FILES['profile_image']

        admin_user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('admin_profile')

    return render(request, 'admin_owner/admin_profile_edit.html', {'admin_user': admin_user})


def dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('adminlogin')

    admin_user = AdminOwner.objects.get(id=request.session['admin_id'])

    
    total_items = FoodItem.objects.filter(restaurant_name=admin_user.restaurant_name).count()

    total_users = User.objects.count()

    context = {
        'admin_user': admin_user,
        'total_items': total_items,
        'total_users': total_users,
    }
    return render(request, 'admin_owner/dashboard.html', context)



def adminheader(request):
    return render(request, 'admin_owner/adminheader.html')

otp_store = {} 
def adminregister(request):
    if request.method == 'POST':
        form = AdminOwnerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/adminlogin/')
    else:
        form = AdminOwnerRegisterForm()

    return render(request, 'admin_owner/adminregister.html', {'form': form})


def adminlogin(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                admin = AdminOwner.objects.get(email=email)  
                if admin.password == password:  
                    request.session['admin_id'] = admin.id
                    request.session['admin_name'] = admin.full_name
                    request.session['restaurant_name'] = admin.restaurant_name  
                    messages.success(request, f"Welcome, {admin.full_name}!")
                    return redirect('/dashboard') 
                else:
                    messages.error(request, "Incorrect password")
            except AdminOwner.DoesNotExist:
                messages.error(request, "Admin with this email does not exist")
    else:
        form = AdminLoginForm()
    return render(request, 'admin_owner/adminlogin.html', {'form': form})

def adminlogout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
    if 'admin_name' in request.session:
        del request.session['admin_name']
    if 'restaurant_name' in request.session:
        del request.session['restaurant_name']

    from django.contrib import messages
    messages.success(request, "Admin has been logged out successfully.")
    return redirect('adminlogin')

def addfood(request):
    if 'admin_id' not in request.session:
        messages.error(request, "You must log in first.")
        return redirect('adminlogin') 

    try:
        admin_user = AdminOwner.objects.get(id=request.session['admin_id'])
    except AdminOwner.DoesNotExist:
        messages.error(request, "Invalid admin session. Please log in again.")
        return redirect('adminlogin')

    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.restaurant_name = admin_user.restaurant_name  
            food.save()
            messages.success(request, "Food item added successfully!")
            return redirect("food_list")
    else:
        form = FoodItemForm()

    return render(request, "admin_owner/addfood.html", {
        "form": form,
        "admin_user": admin_user, 
    })


def food_list(request):
    if 'admin_id' not in request.session:
        messages.error(request, "You must log in first.")
        return redirect('adminlogin')

    try:
        admin_user = AdminOwner.objects.get(id=request.session['admin_id'])
    except AdminOwner.DoesNotExist:
        messages.error(request, "Invalid admin session. Please log in again.")
        return redirect('adminlogin')

    foods = FoodItem.objects.filter(restaurant_name=admin_user.restaurant_name)

    foods_with_discount = []
    for food in foods:
        active_discount = food.discounts.filter(active=True).first()
        foods_with_discount.append({
            "food": food,
            "discount": active_discount
        })

    return render(request, "admin_owner/food_list.html", {
        "foods_with_discount": foods_with_discount,
        "admin_user": admin_user,
    })

def view_food_items(request): 
    restaurant_name = request.session.get('restaurant_name')
    if restaurant_name: 
        food_items = FoodItem.objects.filter(restaurant_name=restaurant_name)
    else: 
        food_items = FoodItem.objects.none()
        messages.error(request, "Please log in to view your food items.")

    return render(request, 'view_food.html', {'food_items': food_items})



def menu_page(request):
    food_items = FoodItem.objects.all()
    today = timezone.now().date()

    for item in food_items:
        item.active_discount = item.discounts.filter(
            start_date__lte=today,
            end_date__gte=today,
            active=True
        ).first() 

        if item.active_discount:
            discount_percent = Decimal(item.active_discount.discount_percentage) / Decimal(100)
            item.discounted_price = item.price * (Decimal(1) - discount_percent)
        else:
            item.discounted_price = item.price

    return render(request, 'menu.html', {'food_items': food_items})


def edit_food(request, food_id):
    admin_id = request.session.get('admin_id')
    food = get_object_or_404(FoodItem, pk=food_id)

    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food) 
        if form.is_valid():
            form.save()
            return redirect('food_list')
    else:
        form = FoodItemForm(instance=food) 

    return render(request, 'admin_owner/edit_food.html', {'form': form})

def delete_food(request, id):
    food = get_object_or_404(FoodItem, id=id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                food.delete()
        except Exception as e:
            print("Error deleting food:", e)
        return redirect('food_list')
    return redirect('food_list')

def bulk_delete_foods(request):
    if request.method == 'POST':
        selected_food_ids = request.POST.getlist('selected_foods')
        if selected_food_ids:
            try:
                with transaction.atomic():
                    deleted_count, _ = FoodItem.objects.filter(id__in=selected_food_ids).delete()
                    messages.success(request, f"{deleted_count} food item(s) deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting selected items: {e}")
        else:
            messages.warning(request, "No food items selected for deletion.")
    return redirect('food_list')



def add_discount(request):
    if 'admin_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('adminlogin')

    admin_user = AdminOwner.objects.get(id=request.session['admin_id'])

    products = FoodItem.objects.filter(restaurant_name=admin_user.restaurant_name)

    if request.method == "POST":
        form = DiscountForm(request.POST)
        form.fields['product'].queryset = products  
        if form.is_valid():
            form.save()
            messages.success(request, "Discount added successfully!")
            return redirect('discount_list')
    else:
        form = DiscountForm()
        form.fields['product'].queryset = products

    return render(request, "admin_owner/discount.html", {
        "form": form,
        "products": products
    })


def discount_list(request):
    today_date = date.today()
    discounts = Discount.objects.select_related('product').all()

    for discount in discounts:
        if discount.end_date <= today_date and discount.active:
            discount.active = False
            discount.save()

    return render(request, 'admin_owner/discount_list.html', {
        'discounts': discounts,
        'today_date': today_date
    })


def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)

    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            return redirect('discount_list')  
    else:
        form = DiscountForm(instance=discount)

    return render(request, 'admin_owner/edit_discount.html', {'form': form, 'discount': discount})


def delete_discount(request, id):
    discount = get_object_or_404(Discount, id=id)
    if request.method == "POST":
        discount.delete()
        messages.success(request, "Discount deleted successfully!")
        return redirect("discount_list") 
    return redirect("discount_list")


def toggle_discount_status(request, discount_id):
    if 'admin_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('adminlogin')

    discount = get_object_or_404(Discount, id=discount_id)
    discount.active = not discount.active
    discount.save()
    messages.success(request, f"Discount status updated to {'Active' if discount.active else 'Inactive'}.")
    return redirect('discount_list')


def add_resto(request):
    if request.method == 'POST':
        form = AddRestoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('resto_list') 
    else:
        form = AddRestoForm()
    return render(request, 'admin_owner/add_restaurant.html', {'form': form})


def resto_list(request):

    admin_id = request.session.get('admin_id')
    restaurant_name = request.session.get('restaurant_name')

    if not admin_id:
        return redirect('/adminlogin/')

    try:
        admin_owner = AdminOwner.objects.get(id=admin_id)
    except AdminOwner.DoesNotExist:
        return redirect('/adminlogin/')

    restos = AddResto.objects.filter(name__iexact=restaurant_name)

    return render(request, 'admin_owner/restaurant_list.html', {
        'restos': restos,
        'admin_owner': admin_owner
    })
    
def edit_restaurant(request, id):
    resto = get_object_or_404(AddResto, id=id)

    if request.method == 'POST':
        form = AddRestoForm(request.POST, request.FILES, instance=resto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully!')
            return redirect('resto_list')  
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddRestoForm(instance=resto)

    return render(request, 'admin_owner/edit_restaurant.html', {'form': form, 'resto': resto})

def delete_restaurant(request, id):
    restaurant = get_object_or_404(AddResto, id=id)
    restaurant.delete()
    messages.success(request, "Restaurant deleted successfully!")
    return redirect('resto_list') 

def delete_all_restaurants(request):
    if request.method == 'POST':
        AddResto.objects.all().delete()
        return JsonResponse({'status': 'success', 'message': 'All restaurants deleted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)    
   

def book_table(request, restaurant_id):
    restaurant = get_object_or_404(AddResto, id=restaurant_id)

    booked_members = restaurant.bookings_resto.aggregate(total=Sum('members'))['total'] or 0
    available_seats = restaurant.seating_capacity - booked_members

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        members = request.POST.get('members')

        if not (customer_name and contact_number and members):
            messages.error(request, "All required fields must be filled.")
            return redirect('restaurant_list')

        if not contact_number.isdigit() or len(contact_number) != 10:
            messages.error(request, "Mobile number must be 10 digits.")
            return redirect('restaurant_list')

        try:
            members = int(members)
        except ValueError:
            messages.error(request, "Please enter a valid number of members.")
            return redirect('restaurant_list')

        if members > available_seats:
            messages.error(request, f"Only {available_seats} seats are available.")
            return redirect('restaurant_list')

    
        Booking_resto.objects.create(
            restaurant=restaurant,
            customer_name=customer_name,
            contact_number=contact_number,
            address=address or "N/A",
            members=members,
            booking_time=datetime.now()
        )

        messages.success(request, f"🎉 Table booked successfully at {restaurant.name}!")
        return redirect('restaurant_list')

    return render(request, 'book_table.html', {
        'restaurant': restaurant,
        'available_seats': available_seats
    })
    
        
def restaurant_list(request):
    restaurants = AddResto.objects.all()
    today = date.today()  

    for restaurant in restaurants:
        bookings_today = restaurant.bookings_resto.filter(booking_time__date=today)

        booked_members = 0
        for b in bookings_today:
            try:
                booked_members += int(b.members)
            except (ValueError, TypeError):
                continue

        restaurant.available_seats = restaurant.seating_capacity - booked_members

    return render(request, 'restaurant_view.html', {'restaurants': restaurants})


def owner_bookings(request):
    owner_id = request.session.get('admin_id')
    restaurant_name = request.session.get('restaurant_name')

    if not owner_id:
        messages.error(request, "Please log in first")
        return redirect('adminlogin') 

    try:
        admin_owner = AdminOwner.objects.get(id=owner_id)
    except AdminOwner.DoesNotExist:
        messages.error(request, "Invalid session. Please log in again.")
        return redirect('adminlogin')

    restaurants = AddResto.objects.filter(name__iexact=restaurant_name)

    bookings = Booking_resto.objects.filter(restaurant__in=restaurants).order_by('-booking_time')

    context = {
        'bookings': bookings,
        'admin_owner': admin_owner,
        'restaurants': restaurants,
    }

    return render(request, 'admin_owner/owner_bookings.html', context)


# ----------------------------------------Main Admin----------------------------------




def super_register(request):
    if request.method == 'POST':
        form = SuperRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save() 
            messages.success(request, 'Registration successful! Please login.')
            return redirect('super_login')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors) 
    else:
        form = SuperRegisterForm()

    return render(request, 'super_admin/super_register.html', {'form': form})


def super_login(request):
    super_user = None
    if 'super_id' in request.session:
        try:
            super_user = SuperRegister.objects.get(id=request.session['super_id'])
        except SuperRegister.DoesNotExist:
            request.session.flush()

    if request.method == 'POST':
        form = SuperLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = SuperRegister.objects.get(email=email)
                if user.check_password(password):
                    request.session['super_id'] = user.id
                    request.session['super_name'] = user.full_name
                    messages.success(request, f'Welcome {user.full_name}!')
                    return redirect('super_dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except SuperRegister.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = SuperLoginForm()

    return render(request, 'super_admin/super_login.html', {
        'form': form,
        'super_user': super_user
    })


def super_profile(request):
    if 'super_id' not in request.session:
        return redirect('/super_login/')

    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('/super_login/')

    context = {
        'super_user': super_user,
        'page_title': 'My Profile'
    }
    return render(request, 'super_admin/super_profile.html', context)


def super_profile_edit(request):
    if 'super_id' not in request.session:
        return redirect('/super_login/')

    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('/super_login/')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        profile_img = request.FILES.get('profile_img')

        if full_name:
            super_user.full_name = full_name
        if email:
            super_user.email = email
        if profile_img:
            super_user.profile_img = profile_img  
        super_user.save()
        return redirect('/super_profile/')

    context = {
        'super_user': super_user,
        'page_title': 'Edit Profile'
    }
    return render(request, 'super_admin/super_profile_edit.html', context)

def super_dashboard(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = SuperRegister.objects.get(id=request.session['super_id'])

    orders_by_day = (
        Order.objects.annotate(day=TruncDate('order_date'))
        .values('day')
        .annotate(
            total_profit=Sum('final_amount'),
            total_products=Sum(F('orderitem__quantity')),
            total_orders=Sum(1)
        )
        .order_by('day')
    )

    chart_labels = [o['day'].strftime("%d %b") for o in orders_by_day]
    chart_profit = [o['total_profit'] or 0 for o in orders_by_day]
    chart_products = [o['total_products'] or 0 for o in orders_by_day]
    chart_orders = [o['total_orders'] or 0 for o in orders_by_day]

    restaurants = Order.objects.values('delivery_name').distinct()
    chart_restaurant_labels, chart_restaurant_orders, chart_restaurant_profit = [], [], []
    for r in restaurants:
        name = r['delivery_name']
        chart_restaurant_labels.append(name)
        orders_count = Order.objects.filter(delivery_name=name).count()
        total_profit = Order.objects.filter(delivery_name=name).aggregate(total=Sum('final_amount'))['total'] or 0
        chart_restaurant_orders.append(orders_count)
        chart_restaurant_profit.append(total_profit)

    foods = FoodItem.objects.all()
    chart_food_labels = [f.food_name for f in foods]
    chart_food_prices = [float(f.price) for f in foods]
    chart_food_is_spicy = [1 if f.is_spicy else 0 for f in foods]
    chart_food_is_veg = [1 if f.is_veg else 0 for f in foods]
    chart_food_is_available = [1 if f.is_available else 0 for f in foods]

    context = {
        'super_user': super_user,
        'chart_labels': json.dumps(chart_labels),
        'chart_profit': json.dumps(chart_profit),
        'chart_products': json.dumps(chart_products),
        'chart_orders': json.dumps(chart_orders),
        'chart_restaurant_labels': json.dumps(chart_restaurant_labels),
        'chart_restaurant_orders': json.dumps(chart_restaurant_orders),
        'chart_restaurant_profit': json.dumps(chart_restaurant_profit),
        'chart_food_labels': json.dumps(chart_food_labels),
        'chart_food_prices': json.dumps(chart_food_prices),
        'chart_food_is_spicy': json.dumps(chart_food_is_spicy),
        'chart_food_is_veg': json.dumps(chart_food_is_veg),
        'chart_food_is_available': json.dumps(chart_food_is_available),
    }

    return render(request, 'super_admin/super_dashboard.html', context)


def super_logout(request):
    if 'super_id' in request.session:
        del request.session['super_id']
    if 'super_name' in request.session:
        del request.session['super_name']

    messages.success(request, "Super Admin has been logged out successfully.")
    return redirect('super_login')


def contactus(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save() 
           
            
            return redirect('contactus')  
    else:
        form = ContactMessageForm()
    return render(request, 'contactus.html', {'form': form})



def admin_contact_list(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('super_login')

    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    return render(request, 'super_admin/admin_contact_list.html', {
        'messages_list': messages_list,
        'super_user': super_user,   
        'page_title': 'Contact List', 
    })


def admin_contact_delete(request, message_id):
    try:
        msg = ContactMessage.objects.get(id=message_id)
        msg.delete()
        messages.success(request, "Message deleted successfully!")
    except ContactMessage.DoesNotExist:
        messages.error(request, "Message not found!")
    
    return redirect('admin_contact_list')


def show_owners(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('super_login')

    owners = AdminOwner.objects.all()
    return render(request, 'super_admin/show_owners.html', {
        'owners': owners,
        'super_user': super_user,
        'page_title': 'Restaurants', 
    })


def show_orders(request):
    if 'super_id' not in request.session:
        return redirect('/super_login/')  

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('/super_login/')

    orders = Order.objects.all().order_by('-id')  

    context = {
        'super_user': super_user,
        'orders': orders,
        'page_title': 'All Orders',
    }
    return render(request, 'super_admin/show_orders.html', context)


def showsuper_users(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('super_login')

    users = Registration.objects.all()

    return render(request, 'super_admin/show_users.html', {
        'owners': users,             
        'super_user': super_user,    
        'page_title': 'Users',      
    })


def show_food(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('super_login')

    food_items = FoodItem.objects.all()

    return render(request, 'super_admin/show_food.html', {
        'owners': food_items,         
        'super_user': super_user,    
        'page_title': 'Food Items',  
    })


def show_booking(request):
    if 'super_id' not in request.session:
        return redirect('super_login')

    super_user = None
    try:
        super_user = SuperRegister.objects.get(id=request.session['super_id'])
    except SuperRegister.DoesNotExist:
        request.session.flush()
        return redirect('super_login')

    restos = AddResto.objects.prefetch_related('bookings_resto').all()

    return render(request, 'super_admin/show_booking.html', {
        'restos': restos,
        'super_user': super_user,   
        'page_title': 'Restaurant Bookings', 
    })


def send_email_to_user(request, pk):
    user_to_email = get_object_or_404(Registration, pk=pk)

    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']
            attachment = request.FILES.get('attachment')

            recipient_email = user_to_email.email
            sender_email = settings.EMAIL_HOST_USER

            email = EmailMessage(
                subject,
                message_body,
                sender_email,
                [recipient_email],
                reply_to=[sender_email]
            )

            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)

            try:
                email.send()
                messages.success(request, f"✅ Email sent successfully to {user_to_email.email}!")
            except Exception as e:
                messages.error(request, f"❌ Failed to send email. Error: {e}")
        else:
            messages.error(request, "⚠️ Please correct the errors in the email form.")
    else:
        messages.warning(request, "Invalid access. Please use the 'Send Email' button.")
    return redirect('showsuper_users')