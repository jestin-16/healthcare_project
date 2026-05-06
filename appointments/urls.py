from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('add-admin/', views.add_admin, name='add_admin'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('manage/<int:appointment_id>/<str:action>/', views.manage_appointment, name='manage_appointment'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('change-password/', views.change_password, name='change_password'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('add-medicine/', views.add_medicine, name='add_medicine'),
    path('edit-medicine/<int:medicine_id>/', views.edit_medicine, name='edit_medicine'),
    path('delete-medicine/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    path('prescribe/<int:appointment_id>/', views.prescribe_medicine, name='prescribe_medicine'),
    path('users/', views.user_list, name='user_management'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('patient-history/<int:patient_id>/', views.patient_history, name='patient_history'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('ajax/get-booked-slots/', views.get_booked_slots, name='get_booked_slots'),
]




