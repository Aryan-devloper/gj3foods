from django.db import models
from django.contrib.auth.models import User 

class Registration(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES, default='Other')
    city = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


from django.db import models

class AdminOwner(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    restaurant_name = models.CharField(max_length=255)
    restaurant_address = models.TextField()
    profile_image = models.ImageField(upload_to='owner_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name
    
class FoodItem(models.Model):
    restaurant_name = models.CharField(max_length=100)
    food_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    is_veg = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    food_image = models.ImageField(upload_to='food_images/')

    def __str__(self):
        return f"{self.restaurant_name} - {self.food_name}"


class Product(models.Model):
    food_name = models.CharField(max_length=200)
    food_image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.food_name

class Discount(models.Model):
    product = models.ForeignKey(
        'FoodItem', 
        on_delete=models.CASCADE, 
        related_name='discounts' 
    )
    discount_percentage = models.PositiveIntegerField()  
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.food_name} - {self.discount_percentage}%"


class Food(models.Model):
    food_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    food_image = models.ImageField(upload_to="food_images/", blank=True, null=True)

    def __str__(self):
        return self.food_name



class Cart(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)  
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)   
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.food.food_name} ({self.quantity})"

from .models import Registration

class Order_pay(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE) 
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, default="created")
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    total_amount = models.FloatField()
    total_discount = models.FloatField(default=0)
    final_amount = models.FloatField()
    delivery_name = models.CharField(max_length=255)
    delivery_phone = models.CharField(max_length=15)
    delivery_address = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Order {self.id} - {self.user.username if self.user else 'Guest'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    discount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """
        Computes subtotal for this item considering discount.
        """
        return (self.price - self.discount) * self.quantity




class AddResto(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    seating_capacity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='restaurant_images/')
    menu = models.FileField(upload_to='restaurant_menus/', null=True, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.name



class Booking(models.Model):
    restaurant = models.ForeignKey(AddResto, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    members = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.restaurant.name}"
    
    
    
    
    
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class SuperRegister(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_img = models.ImageField(upload_to='super_images/', blank=True, null=True)
    role = models.CharField(max_length=50, default='Super Admin')
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'super_register' 

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name
    
    
    
    from django.db import models

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

class Booking_resto(models.Model):
    restaurant = models.ForeignKey(AddResto, on_delete=models.CASCADE, related_name="bookings_resto")
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    members = models.PositiveIntegerField()
    booking_time = models.DateTimeField()

    def __str__(self):
        return f"{self.customer_name} - {self.restaurant.name}"
