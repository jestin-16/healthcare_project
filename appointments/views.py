from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserRegistrationForm, DoctorProfileForm, NurseProfileForm, StaffRegistrationForm, AdminRegistrationForm, AppointmentForm
from .models import Profile, Doctor, Nurse, Appointment
from django.core.exceptions import PermissionDenied

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
            
            # Profile is created by signal, force patient role
            user.profile.role = 'patient'
            user.profile.save()
            
            login(request, user)
            messages.success(request, f"Account created for {user.username} as a Patient!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def add_staff(request):
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
                Doctor.objects.create(user=user, specialization="General Physician")
            elif role == 'nurse':
                Nurse.objects.create(user=user, department="General")
            
            messages.success(request, f"{role.capitalize()} {user.username} added successfully!")
            return redirect('admin_dashboard') # Assuming an admin dashboard exists or just redirect somewhere
    else:
        form = StaffRegistrationForm()
    return render(request, 'appointments/add_staff.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def add_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            # Admins don't strictly need a profile role, but let's set it to 'staff' or similar if needed
            # For now, superuser status is enough for the admin_dashboard redirect
            
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
        appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
        return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})
    elif role == 'doctor':
        # Ensure Doctor profile exists
        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile:
             messages.error(request, "Doctor profile not found.")
             return redirect('home')
        appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('-date')
        return render(request, 'appointments/doctor_dashboard.html', {'appointments': appointments})
    elif role == 'nurse':
        # Nurses might see a general dashboard for now
        return render(request, 'appointments/nurse_dashboard.html')
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    doctors_count = Doctor.objects.count()
    nurses_count = Nurse.objects.count()
    patients_count = Profile.objects.filter(role='patient').count()
    total_appointments = Appointment.objects.count()
    
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    
    context = {
        'doctors_count': doctors_count,
        'nurses_count': nurses_count,
        'patients_count': patients_count,
        'total_appointments': total_appointments,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'appointments/admin_dashboard.html', context)

@login_required
@role_required(allowed_roles=['patient'])
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            try:
                appointment.save()
                messages.success(request, "Appointment booked successfully! Waiting for approval.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, "This slot is already booked for this doctor.")
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@role_required(allowed_roles=['doctor'])
def manage_appointment(request, appointment_id, action):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    if action == 'approve':
        appointment.status = 'approved'
        messages.success(request, "Appointment approved.")
    elif action == 'reject':
        appointment.status = 'rejected'
        messages.success(request, "Appointment rejected.")
    appointment.save()
    return redirect('dashboard')

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})
