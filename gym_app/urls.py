from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('members/', views.member_list, name='member_list'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/new/', views.member_create, name='member_create'),
    path('active-members/', views.active_members, name='active_members'),
    path('pending-invoices/', views.pending_invoices, name='pending_invoices'),
    path('members/<int:pk>/edit/', views.member_update, name='member_update'),
    path('classes/', views.class_list, name='class_list'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    path('classes/new/', views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/', views.class_update, name='class_update'),
    path('classes/<int:pk>/register/', views.class_register, name='class_register'),  # Updated this line
    path('logout/', views.logout_view, name='logout'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('attendance/', views.attendance_history, name='attendance_history'),
    path('billing/', views.billing_dashboard, name='billing_dashboard'),
    path('pay-invoice/<int:invoice_id>/', views.pay_invoice, name='pay_invoice'),
    path('generate-invoice/<int:member_id>/', views.generate_invoice, name='generate_invoice'),
    path('send-invoice-whatsapp/<int:invoice_id>/', views.send_invoice_whatsapp, name='send_invoice_whatsapp'),
    path('members/<int:pk>/delete/', views.delete_member, name='delete_member'),
]