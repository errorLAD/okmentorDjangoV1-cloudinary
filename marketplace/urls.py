from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView
from django.views.generic import RedirectView
from .book_service_view import book_service

# Remove RedirectView for /signup/ and add mentee_signup placeholder

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('book/service/<int:service_id>/', book_service, name='book_service'),
    path('', views.home, name='home'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('mentors/<str:username>/', views.mentor_profile, name='mentor_profile'),
    path('mentor/signup/', views.mentor_signup, name='mentor_signup'),
    path('digital-products/', views.digital_product_list, name='digital_product_list'),
    path('mentor/digital-products/', views.mentor_digital_products, name='mentor_digital_products'),
    path('mentor/digital-products/add/', views.digital_product_add, name='digital_product_add'),
    path('digital-products/buy/<int:product_id>/', views.digital_product_buy, name='digital_product_buy'),
    path('mentor/services/add/', views.mentor_service_add, name='mentor_service_add'),
    path('mentor/services/', views.service_list, name='service_list'),
    path('mentor/services/add/', views.service_add, name='service_add'),
    path('mentor/services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('mentor/services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('mentor/availability/', views.availability_manage, name='availability_manage'),
    path('mentor/bookings/', views.mentor_bookings, name='mentor_bookings'),
    path('mentor/bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('mentor/orders/<int:order_id>/', views.digital_order_detail, name='digital_order_detail'),
    path('mentor/analytics/', views.mentor_analytics, name='mentor_analytics'),
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('mentor/profile/update/', views.mentor_profile_update, name='mentor_profile_update'),
    path('mentor/settings/', views.mentor_settings, name='mentor_settings'),
    path('mentor/availability/', views.mentor_availability, name='mentor_availability'),
    path('user/order-history/', views.user_order_history, name='user_order_history'),
    path('booking/<int:booking_id>/razorpay/', views.razorpay_payment, name='razorpay_payment'),
    path('booking/<int:booking_id>/razorpay/callback/', views.razorpay_payment_callback, name='razorpay_payment_callback'),
    path('digital-order/<int:order_id>/razorpay/', views.razorpay_payment_digital, name='razorpay_payment_digital'),
    path('digital-order/<int:order_id>/razorpay/callback/', views.razorpay_payment_digital_callback, name='razorpay_payment_digital_callback'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.signup_options, name='signup_options'),
    path('mentee/signup/', views.mentee_signup, name='mentee_signup'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]
