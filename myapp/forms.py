from django import forms
from .models import Registration
from .models import AdminOwner


from django import forms
from .models import FoodItem
from django import forms
from .models import FoodItem

from .models import Discount
from myapp.models import Registration

from django.db import models
from django.contrib.auth.models import User
from myapp.models import FoodItem
from .models import AddResto
from .models import ContactMessage
from .models import SuperRegister



class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Registration
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'city', 'gender', 'profile_image', 'password'
        ]
        widgets = {
            'password': forms.PasswordInput(),
            'gender': forms.Select(choices=Registration.GENDER_CHOICES),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control'
    }))



class AdminOwnerRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AdminOwner
        fields = ['full_name', 'email', 'password', 'restaurant_name', 'restaurant_address', 'profile_image']


class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': "Business Email Address",
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Password",
        'class': 'form-control'
    }))
    


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['restaurant_name', 'food_name', 'description', 'price', 'category', 'is_veg', 'is_spicy', 'is_available', 'food_image']


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    
class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))
    
class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))
    
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        cpw = cleaned_data.get("confirm_password")
        if pw != cpw:
            raise forms.ValidationError("Passwords do not match")


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['product', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CartForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.food.food_name} ({self.quantity})"


class AddRestoForm(forms.ModelForm):
    class Meta:
        model = AddResto
        fields = ['name', 'email', 'address', 'seating_capacity', 'image', 'menu', 'opening_time', 'closing_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
   

class SuperRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = SuperRegister
        fields = ['full_name', 'email', 'phone', 'address', 'profile_img', 'role', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class SuperLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)



class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'block w-full text-base',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full text-base',
                'placeholder': 'you@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'block w-full text-base',
                'placeholder': 'e.g., Question about my order'
            }),
            'message': forms.Textarea(attrs={
                'class': 'block w-full text-base resize-none',
                'rows': 5,
                'placeholder': 'Write your message here...'
            }),
        }


class EmailForm(forms.Form):
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Subject of the email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Your message here...'}))
    attachment = forms.FileField(required=False, help_text='Optional: Attach a file (e.g., a menu)')