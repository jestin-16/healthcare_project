from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, DoctorProfileForm, AppointmentForm
from .models import Profile, Doctor, Appointment
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
            
            # Profile is created by signal, just update role
            role = form.cleaned_data['role']
            user.profile.role = role
            user.profile.save()
            
            if role == 'doctor':
                # If doctor, we might need extra info, but for now we just mark it
                # Realistically we should redirect to a doctor profile setup page
                Doctor.objects.create(user=user, specialization="General Physician")
            
            login(request, user)
            messages.success(request, f"Account created for {user.username} as {role}!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
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
    return redirect('home')

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
