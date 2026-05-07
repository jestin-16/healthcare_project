from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
import uuid

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .forms import (
    UserRegistrationForm, DoctorProfileForm, NurseProfileForm, 
    StaffRegistrationForm, AdminRegistrationForm, AppointmentForm, 
    MedicineForm, PrescriptionForm, PrescriptionFormSet,
    UserUpdateForm, ProfileUpdateForm
)
from .models import Profile, Doctor, Nurse, Appointment, Medicine, Prescription, PrescribedMedicine

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator

def home(request):
    return render(request, 'appointments/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            user.profile.role = 'patient'
            user.profile.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username} as a Patient!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def change_password(request):
    return PasswordChangeView.as_view(
        template_name='registration/change_password.html',
        success_url=reverse_lazy('dashboard')
    )(request)

@login_required
def add_staff(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']
            user.profile.role = role
            user.profile.save()
            if role == 'doctor':
                spec = form.cleaned_data.get('specialization') or "General Physician"
                Doctor.objects.create(user=user, specialization=spec)
            elif role == 'nurse':
                Nurse.objects.create(user=user, department="General")
            messages.success(request, f"{role.capitalize()} {user.username} added successfully!")
            return redirect('admin_dashboard')
    else:
        form = StaffRegistrationForm()
    return render(request, 'appointments/add_staff.html', {'form': form})

@login_required
def add_admin(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, f"Admin {user.username} created successfully!")
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'appointments/add_admin.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    role = request.user.profile.role
    if role == 'patient':
        appointments = Appointment.objects.filter(patient=request.user).select_related('doctor__user', 'prescription').order_by('-date')
        return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})
    elif role == 'doctor':
        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile:
             messages.error(request, "Doctor profile not found.")
             return redirect('home')
        appointments = Appointment.objects.filter(doctor=doctor_profile).select_related('patient', 'prescription').order_by('-date')
        return render(request, 'appointments/doctor_dashboard.html', {'appointments': appointments})
    elif role == 'nurse':
        low_stock_medicines = Medicine.objects.filter(stock__lte=10)
        total_medicines = Medicine.objects.count()
        return render(request, 'appointments/nurse_dashboard.html', {
            'low_stock': low_stock_medicines,
            'total_medicines': total_medicines
        })

    return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    context = {
        'doctors_count': Doctor.objects.count(),
        'nurses_count': Nurse.objects.count(),
        'patients_count': Profile.objects.filter(role='patient').count(),
        'total_appointments': Appointment.objects.count(),
        'recent_appointments': Appointment.objects.select_related('patient', 'doctor__user').order_by('-created_at')[:5],
    }
    return render(request, 'appointments/admin_dashboard.html', context)

@login_required
def medicine_list(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    medicines = Medicine.objects.all()
    return render(request, 'appointments/medicine_list.html', {'medicines': medicines})

@login_required
def add_medicine(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine added successfully!")
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'appointments/add_medicine.html', {'form': form})

@login_required
def edit_medicine(request, medicine_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f"{medicine.name} updated successfully!")
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'appointments/add_medicine.html', {'form': form, 'edit_mode': True})

@login_required
def delete_medicine(request, medicine_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    medicine = get_object_or_404(Medicine, id=medicine_id)
    name = medicine.name
    medicine.delete()
    messages.success(request, f"{name} removed from inventory.")
    return redirect('medicine_list')


@login_required
@role_required(allowed_roles=['doctor'])
def prescribe_medicine(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    prescription, created = Prescription.objects.get_or_create(appointment=appointment)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionFormSet(request.POST, instance=prescription)
        if form.is_valid() and formset.is_valid():
            prescription = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.prescription = prescription
                instance.save()
                
                # Reduce stock
                med = instance.medicine
                if med.stock >= 1:
                    med.stock -= 1
                    med.save()
                else:
                    messages.warning(request, f"Warning: {med.name} is out of stock!")
            
            # Save deletions if any
            for obj in formset.deleted_objects:
                obj.delete()
                
            messages.success(request, "Prescription saved successfully!")
            return redirect('dashboard')
    else:
        form = PrescriptionForm(instance=prescription)
        formset = PrescriptionFormSet(instance=prescription)
    return render(request, 'appointments/prescribe_medicine.html', {
        'form': form, 'formset': formset, 'appointment': appointment
    })

@login_required
@role_required(allowed_roles=['patient'])
def book_appointment(request):
    doctor_id = request.GET.get('doctor')
    initial_data = {}
    if doctor_id:
        initial_data['doctor'] = doctor_id
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            if appointment.appointment_type == 'virtual':
                appointment.meeting_room_id = f"ProHealth_{uuid.uuid4().hex[:12]}"
            appointment.save()
            messages.success(request, "Appointment booked successfully! Waiting for approval.")
            return redirect('dashboard')
    else:
        form = AppointmentForm(initial=initial_data)
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@role_required(allowed_roles=['doctor'])
def manage_appointment(request, appointment_id, action):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    if action == 'approve':
        appointment.status = 'approved'
        msg = "Appointment approved."
    elif action == 'reject':
        appointment.status = 'rejected'
        msg = "Appointment rejected."
    appointment.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': msg, 'new_status': appointment.status})
        
    messages.success(request, msg)
    return redirect('dashboard')

@login_required
@role_required('patient')
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if appointment.status in ['pending', 'approved']:
        appointment.delete()
        messages.success(request, "Your appointment has been successfully cancelled.")
    else:
        messages.error(request, "This appointment cannot be cancelled.")
    return redirect('dashboard')

def doctor_list(request):
    query = request.GET.get('q')
    spec = request.GET.get('specialization')
    doctors = Doctor.objects.all()
    
    if query:
        doctors = doctors.filter(user__first_name__icontains=query) | doctors.filter(user__username__icontains=query)
    
    if spec:
        doctors = doctors.filter(specialization=spec)
        
    specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
    
    return render(request, 'appointments/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations,
        'selected_spec': spec,
        'query': query
    })


@login_required
@role_required('doctor')
def patient_history(request, patient_id):
    patient = get_object_or_404(User, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
    return render(request, 'appointments/patient_history.html', {
        'patient': patient,
        'appointments': appointments
    })

@login_required
def profile_settings(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile_settings')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'appointments/profile_settings.html', {
        'u_form': u_form,
        'p_form': p_form
    })

def get_booked_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if doctor_id and date_str:
        booked_times = Appointment.objects.filter(
            doctor_id=doctor_id, 
            date=date_str
        ).values_list('time', flat=True)
        # Convert time objects to HH:MM strings
        booked_slots = [t.strftime('%H:%M') for t in booked_times]
        return JsonResponse({'booked_slots': booked_slots})
    return JsonResponse({'booked_slots': []})


# User Management CRUD for Admin
@login_required
def user_list(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    users = User.objects.all().select_related('profile').order_by('id')
    return render(request, 'appointments/user_list.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user_to_edit.first_name = request.POST.get('first_name')
        user_to_edit.last_name = request.POST.get('last_name')
        user_to_edit.email = request.POST.get('email')
        
        # Role update
        new_role = request.POST.get('role')
        user_to_edit.profile.role = new_role
        user_to_edit.profile.save()
        
        # Profile handling
        if new_role == 'doctor':
            spec = request.POST.get('specialization', 'General')
            Doctor.objects.update_or_create(user=user_to_edit, defaults={'specialization': spec})
            # Remove from nurse if exists
            Nurse.objects.filter(user=user_to_edit).delete()
        elif new_role == 'nurse':
            dept = request.POST.get('department', 'General')
            Nurse.objects.update_or_create(user=user_to_edit, defaults={'department': dept})
            # Remove from doctor if exists
            Doctor.objects.filter(user=user_to_edit).delete()
        else:
            # Patient - remove both if exist
            Doctor.objects.filter(user=user_to_edit).delete()
            Nurse.objects.filter(user=user_to_edit).delete()
            
        user_to_edit.save()
        messages.success(request, f"User {user_to_edit.username} updated successfully.")
        return redirect('user_management')
        
    return render(request, 'appointments/edit_user.html', {'user_to_edit': user_to_edit})

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own admin account.")
    else:
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"User {username} has been deleted.")
    return redirect('user_management')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

def ping(request):
    return JsonResponse({'status': 'alive'})

@login_required
def video_call(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Check if user is part of this appointment
    is_doctor = hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile
    is_patient = appointment.patient == request.user
    
    if not (is_doctor or is_patient or request.user.is_superuser):
        raise PermissionDenied
    
    if appointment.status != 'approved':
        messages.error(request, "Video call is only available for approved appointments.")
        return redirect('dashboard')
        
    if not appointment.meeting_room_id:
        appointment.meeting_room_id = f"ProHealth_{uuid.uuid4().hex[:12]}"
        appointment.save()

    return render(request, 'appointments/video_call.html', {
        'appointment': appointment,
        'room_name': appointment.meeting_room_id,
        'user_name': request.user.get_full_name() or request.user.username
    })
