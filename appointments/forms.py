from django import forms
from django.contrib.auth.models import User
from .models import Profile, Doctor, Nurse, Appointment, Medicine, Prescription, PrescribedMedicine

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'bio', 'experience']

class NurseProfileForm(forms.ModelForm):
    class Meta:
        model = Nurse
        fields = ['department', 'shift']

class StaffRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    SPECIALIZATION_CHOICES = [
        ('General Physician', 'General Physician'),
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Pediatrician', 'Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Surgeon', 'Surgeon'),
        ('Gynecologist', 'Gynecologist'),
        ('Orthopedic', 'Orthopedic'),
        ('Ophthalmologist', 'Ophthalmologist'),
    ]
    role = forms.ChoiceField(choices=(('doctor', 'Doctor'), ('nurse', 'Nurse')), widget=forms.Select(attrs={'class': 'form-control'}))
    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'General instructions...'}),
        }

class PrescribedMedicineForm(forms.ModelForm):
    class Meta:
        model = PrescribedMedicine
        fields = ['medicine', 'dosage', 'duration']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1-0-1'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 days'}),
        }

from django.forms import inlineformset_factory
PrescriptionFormSet = inlineformset_factory(
    Prescription, PrescribedMedicine, form=PrescribedMedicineForm, extra=3, can_delete=True
)

class AdminRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@healthcare.pro'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class AppointmentForm(forms.ModelForm):
    TIME_SLOTS = [
        ('09:00', '09:00 AM'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '01:00 PM'),
        ('13:30', '01:30 PM'),
        ('14:00', '02:00 PM'),
        ('14:30', '02:30 PM'),
        ('15:00', '03:00 PM'),
        ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
    ]
    time = forms.ChoiceField(choices=TIME_SLOTS, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if doctor and date and time:
            if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
                raise forms.ValidationError("This time slot is already booked for this doctor. Please choose another time.")
        return cleaned_data


