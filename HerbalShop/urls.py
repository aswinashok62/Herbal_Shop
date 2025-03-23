"""Online_Grocery_Shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from grocery.views import *
from django.conf.urls.static import static
from django.conf import settings
from grocery.n_view import chat_view, send_message
from grocery.n_view import send_product_request
from grocery.user_views import (
    delete_user_booking, add_to_cart, increase_cart_quantity,
    decrease_cart_quantity, remove_from_cart, view_cart,View_Booking,
    test_stock_update
)
from grocery.n_view import *
from grocery.refund_views import return_product, refund_form, admin_view_returns, submit_return_request

# from grocery.user_views import delete_user_booking

urlpatterns = [
    path('admin/', admin.site.urls),
    
   
    path('',Home,name="home"),
    path('signup',Signup,name="signup"),
	path('about/',About,name='about'),
	path('contact/',Contact,name='contact'),
    path('login/',Login,name="login"),
    path('logout/',Logout,name="logout"),
    path('view_user',View_user,name="view_user"),
    path('add_product',Add_Product,name="add_product"),
    path('view_feedback', View_feedback, name='view_feedback'),
    path('view_product(<int:pid>)', View_prodcut, name='view_product'),
    path('admin_view_product', Admin_View_product, name='admin_view_product'),
    path('login_admin',Admin_Login,name="login_admin"),
    path('admin_viewBooking', Admin_View_Booking, name='admin_viewBooking'),
    path('view_categary/', View_Categary, name='view_categary'),
    path('add_categary', Add_Categary, name='add_categary'),
    # Cart URLs
    path('add-to-cart/<int:pid>/', add_to_cart, name='add_cart'),
    path('increase-quantity/<int:cid>/', increase_cart_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:cid>/', decrease_cart_quantity, name='decrease_quantity'),
    path('remove-cart/<int:cid>/', remove_from_cart, name='remove_cart'),
    path('cart/', view_cart, name='cart'),
    path('delete_product/<int:pid>/', delete_product, name='delete_product'),
    path('delete_user/<int:pid>/', delete_user, name='delete_user'),
    path('delete_feedback/<int:pid>/', delete_feedback, name='delete_feedback'),
    path('payment/<int:total>/', payment, name='payment'),
    path('delete_booking/<int:bid>/', delete_user_booking, name='delete_booking'),
    path('return_product/<int:product_id>/', return_product, name='return_product'),
    path('refund_form/', refund_form, name='refund_form'),
    path("admin-view-returns/", admin_view_returns, name="admin_view_returns"),

    path('delete_admin_booking/<str:pid>/<int:bid>/', delete_admin_booking, name='delete_admin_booking'),
    path('booking_detail/<str:pid>/<int:bid>/', booking_detail, name='booking_detail'),
    path('admin_booking_detail/<str:pid>/<int:bid>/<int:uid>/', admin_booking_detail, name='admin_booking_detail'),
    path('Edit_status/<str:pid>/<int:bid>/', Edit_status, name='Edit_status'),
    path('booking/<str:pid>/', Booking_order, name='booking_order'),



    path('invoice/<int:bid>/', generate_invoice, name='generate_invoice'),
    path('view_booking', View_Booking, name='view_booking'),
    path('profile/', profile, name='profile'),
    path('edit_profile', Edit_profile, name='edit_profile'),
    path('delete_category/<int:pid>/', delete_category, name='delete_category'),
    path('admin_home', Admin_Home, name='admin_home'),
    path('change_password', Change_Password, name="change_password"),
    path('send_feedback/<int:pid>/', Feedback, name='send_feedback'),
    path('edit_category/<int:pid>',edit_category, name='edit_category'),
    path('edit_product/<int:pid>',edit_product, name='edit_product'),
    path('test_stock_update/<int:product_id>/<int:quantity>/', test_stock_update, name='test_stock_update'),
    path('test_stock_update/', test_stock_update, name='test_stock_update_default'),
    # path('search/', search_product, name='search_product'),
    path('admin_cancel_booking/<str:booking_id>/<int:id>/', admin_cancel_booking, name='admin_cancel_booking'),
 

    path('search_booking',search_booking, name='search_booking'),
    path('bookingbetweendate_reportdetails',bookingbetweendate_reportdetails, name='bookingbetweendate_reportdetails'),
    path('bookingbetweendate_report',bookingbetweendate_report, name='bookingbetweendate_report'),
    path('product/details/<int:product_id>/', product_details, name='product_details'),
    path('chatbot/', chatbot, name='chatbot'),




    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('user/appointments/', user_appointments, name='user_appointments'),
    path('appointment/book/', book_appointment, name='book_appointment'),
    path('appointment/<int:appointment_id>/chat/', appointment_chat, name='appointment_chat'),
    # path('profiles/', doctor_profile, name='profiles'),
    path('appointment/all/', all_appointments, name='all_appointments'),
    path('book-appointment/', book_appointment, name='book_appointment'),
    path('get_available_slots/', get_available_slots, name='get_available_slots'), 
    
    
    
    path('appointments/', doctor_appointments, name='doctor_appointments'),
    path('add_available_time_slot/', add_available_time_slot, name='add_available_time_slot'),
    path('get_available_slots/', get_available_slots, name='get_available_slots'),
    path('your_appointments/', your_appointments, name='your_appointments'),
    path('update_appointment_status/<int:appointment_id>/', update_appointment_status, name='update_appointment_status'),
    path('chat/<int:appointment_id>/', chat_view, name='chat'),
    path('chat/<int:appointment_id>/send/', send_message, name='send_message'),
    path('chat/<int:appointment_id>/fetch/', fetch_messages, name='fetch_messages'),

    path('doctor/login/', doctor_login, name='doctor_login'),
    path('doctor/register/', doctor_register, name='doctor_register'),
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),

    # path('profiles/', doctor_profile, name='doctor_profile'),
    path('doctor/notifications/', doctor_notifications, name='doctor_notifications'),
    path('appointment-history/', appointment_history, name='appointment_history'),
    path('appointments/', doctor_appointments, name='doctor_appointments'),
    # path('profile/', doctor_profile, name='doctor_profile'),




    path('supplier/login/', supplier_login, name='supplier_login'),
    path('supplier/register/', supplier_register, name='supplier_register'),
    path('supplier/dashboard/', supplier_dashboard, name='supplier_dashboard'),
    path('supplier/logout/', supplier_logout, name='supplier_logout'),
    path('send-product-request/', send_product_request, name='send_product_request'),
    path('supplier/product-requests/', supplier_product_requests, name='supplier_product_requests'),
    path('download-pdf/<str:date>/', download_requests_pdf, name='download_requests_pdf'),
    path('supplier/all-requests/', all_requests_view, name='all_requests'),
    path('supplier/update-request/<int:request_id>/', update_request_status, name='update_request_status'),
    path('supplier/submit-all-requests/', submit_all_requests, name='submit_all_requests'),
    path('supply-details/', supply_details, name='supply_details'),
    path("delete_request/<int:request_id>/", delete_product_request, name="delete_request"),
    path('download-invoice/<int:supplier_id>/', download_invoice, name='download_invoice'),
    path('cart/', view_cart, name='cart'),
    path('add-to-cart/<int:pid>/', add_to_cart, name='add_cart'),
    path('increase-quantity/<int:cid>/', increase_cart_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:cid>/', decrease_cart_quantity, name='decrease_quantity'),
    
    
    path('blog/', blog, name='blog'),
    path('add_blog/', add_blog, name='add_blog'),
    path('doctor_add_blog/', doctor_add_blog, name='doctor_add_blog'),
    path('doctor/blog/edit/<int:blog_id>/', doctor_edit_blog, name='doctor_edit_blog'),
    path('doctor/blog/delete/<int:blog_id>/', doctor_delete_blog, name='doctor_delete_blog'),
    path('blog/<int:id>/', blog_detail, name='blog_detail'),
    path('dashboard/blogs/edit/<int:blog_id>/', edit_blog, name='edit_blog'),
    path('dashboard/blogs/delete/<int:blog_id>/', delete_blog, name='delete_blog'),
    
    
    path('deliveryboy/dashboard/', delivery_boy_dashboard, name='delivery_boy_dashboard'),
    path('deliveryboy/login/', delivery_boy_login, name='delivery_boy_login'),
    path('deliveryboy/register/', delivery_boy_registration, name='delivery_boy_register'),  # Ensure this line exists
    path('success/', success_page, name='success_page'),  # Success page
    path('admin/verify_delivery_boys/', verify_delivery_boys, name='verify_delivery_boys'), # Correct URL pattern
    path('admin/verify_delivery_boy/<int:id>/', confirm_delivery_boy, name='confirm_delivery_boy'), 




     #add this
    path('verify-delivery-boys/', verify_delivery_boys, name='verify_delivery_boys'),
    path('approve-delivery-boy/<int:delivery_boy_id>/', approve_delivery_boy, name='approve_delivery_boy'),
    path('delivery-boy-details/<int:delivery_boy_id>/', delivery_boy_details, name='delivery_boy_details'),
    #here


    path('deliveryboy/orders/', deliveryboy_orders, name='deliveryboy_orders'),
    path('deliveryboy/feedback/', deliveryboy_feedback, name='deliveryboy_feedback'),
    path('deliveryboy/logout/', deliveryboy_logout, name='deliveryboy_logout'),
    path('assign_delivery_boy/<str:booking_id>/<int:booking_obj_id>/', assign_delivery_boy, name='assign_delivery_boy'),
    path('update-status/<int:booking_id>/', update_delivery_status, name='update_delivery_status'),
    path('pending_orders/', delivery_boy_pending, name='delivery_boy_pending'),
    path('delivery_history/', delivery_history, name='delivery_history'),
    path('deliveryboy/profile/', delivery_boy_profile, name='delivery_boy_profile'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    