from django.contrib import admin
from django.urls import path
from myproject import views

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homepage),
    path('aboutus/',views.about),
    path('contactus/',views.contactus, name='contactus'),
   
    path('menu/',views.menu_page, name='menu_page'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('success/', views.success, name='success'),
    path('adminheader/', views.adminheader, name='adminheader'),
    path('adminregister/', views.adminregister, name='adminregister'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('admin_profile/edit/<int:admin_id>/', views.admin_profile_edit, name='admin_profile_edit'),
    path('addfood/', views.addfood, name='addfood'),
    path("food_list/", views.food_list, name="food_list"),
    path('view_food/', views.view_food_items, name='view_food'), 
    path('foods/edit/<int:food_id>/', views.edit_food, name='edit_food'),
    path('foods/delete/<int:food_id>/', views.delete_food, name='delete_food'),
    path('forgot_password/', views.forgot_password, name='forgot_password'), 
    path('logout/',views.logout_user , name='logout'),    
    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin_logout/', views.adminlogout, name='adminlogout'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('food/delete/<int:id>/', views.delete_food, name='delete_food'),
    path('bulk_delete_foods/', views.bulk_delete_foods, name='bulk_delete_foods'),

    
    # path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('my_orders/download/<int:order_id>/', views.download_bill, name='download_bill'),




    path('my-bookings/', views.my_booking, name='my_booking'),

    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('profile/', views.profile_view, name='profile_page'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('add-discount/', views.add_discount, name='add_discount'),
    path('discount-list/', views.discount_list, name='discount_list'),
    path('toggle-discount/<int:discount_id>/', views.toggle_discount_status, name='toggle_discount'),
    path('discount/edit/<int:discount_id>/', views.edit_discount, name='edit_discount'),
    path("discount/<int:id>/delete/", views.delete_discount, name="delete_discount"),
   
    path('add_restaurant/', views.add_resto, name='add_restaurant'),
    path('restaurant_list/', views.resto_list, name='resto_list'), 
    path('restaurants/edit/<int:id>/', views.edit_restaurant, name='edit_restaurant'),
    path('restaurants/delete/<int:id>/', views.delete_restaurant, name='delete_restaurant'),
    path('restaurants/delete-all/', views.delete_all_restaurants, name='delete-all-restaurants'),
    #User side
    path("restaurant_view/", views.restaurant_list, name="restaurant_list"),
    path("book_table/<int:restaurant_id>/", views.book_table, name="book_table"),
    path('booking/edit/<int:id>/', views.edit_booking, name='edit_booking'),
    path('booking/delete/<int:id>/', views.delete_booking, name='delete_booking'),

    path('owner_bookings/', views.owner_bookings, name='owner_bookings'),

                                #Super admin
    path('super_register/', views.super_register, name='super_register'),
    path('super_login/', views.super_login, name='super_login'),
    path('super_profile/', views.super_profile, name='super_profile'),
    path('super_profile_edit/', views.super_profile_edit, name='super_profile_edit'),
    path('super_dashboard/', views.super_dashboard, name='super_dashboard'),
    path('super_logout/', views.super_logout, name='super_logout'),
    path('admin_contact_list/', views.admin_contact_list, name='admin_contact_list'),
    path('admin_contact_list/delete/<int:message_id>/', views.admin_contact_delete, name='admin_contact_delete'),

    path('show_owners/', views.show_owners, name='show_owners'),
    path('show_users/', views.showsuper_users, name='showsuper_users'),
    path('show_food/', views.show_food, name='show_food'),
    path('show_orders/', views.show_orders, name='show_orders'),
    path('show_booking/', views.show_booking, name='show_booking'),


    path('super_admin/users/send_email/<int:pk>/', views.send_email_to_user, name='send_email_to_user'),
    



]
 

