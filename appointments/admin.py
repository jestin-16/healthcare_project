from django.contrib import admin
from .models import Profile, Doctor, Appointment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience')
    search_fields = ('user__username', 'specialization')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__username', 'doctor__user__username')
    actions = ['approve_appointments', 'reject_appointments']

    def approve_appointments(self, request, queryset):
        queryset.update(status='approved')
    approve_appointments.short_description = "Approve selected appointments"

    def reject_appointments(self, request, queryset):
        queryset.update(status='rejected')
    reject_appointments.short_description = "Reject selected appointments"
