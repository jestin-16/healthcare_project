from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm, DoctorProfileForm, NurseProfileForm, StaffRegistrationForm, AdminRegistrationForm, AppointmentForm, MedicineForm, PrescriptionForm, PrescriptionFormSet
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
        appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
        return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})
    elif role == 'doctor':
        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile:
             messages.error(request, "Doctor profile not found.")
             return redirect('home')
        appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('-date')
        return render(request, 'appointments/doctor_dashboard.html', {'appointments': appointments})
    elif role == 'nurse':
        return render(request, 'appointments/nurse_dashboard.html')
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
        'recent_appointments': Appointment.objects.order_by('-created_at')[:5],
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
@role_required(allowed_roles=['doctor'])
def prescribe_medicine(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    prescription, created = Prescription.objects.get_or_create(appointment=appointment)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionFormSet(request.POST, instance=prescription)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
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
        messages.success(request, "Appointment approved.")
    elif action == 'reject':
        appointment.status = 'rejected'
        messages.success(request, "Appointment rejected.")
    appointment.save()
    return redirect('dashboard')

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})

