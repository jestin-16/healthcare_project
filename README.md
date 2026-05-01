# 🏥 Healthcare Appointment Booking System

A production-ready Django application for managing doctor appointments with role-based access control.

## 🚀 Features

- **Patient Role**: Register, view doctors, book appointments, and track status.
- **Doctor Role**: Manage incoming appointment requests (Approve/Reject).
- **Admin**: Full control via Django Admin panel.
- **Security**: Role-based access control (RBAC) and data validation.
- **Deployment Ready**: Configured for Render with Whitenoise and Gunicorn.

## 🛠️ Local Setup

1. **Clone the repository** (if applicable)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
5. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

## 🌐 Deployment (Render)

1. Connect your GitHub repository to Render.
2. Select **Web Service**.
3. Set **Build Command**: `./build.sh`
4. Set **Start Command**: `gunicorn healthcare_project.wsgi`
5. Add **Environment Variables**:
   - `SECRET_KEY`: Your secret key
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app.onrender.com`
   - `DATABASE_URL`: Your PostgreSQL connection string

## 📁 Project Structure

- `appointments/`: Core application logic, models, and views.
- `healthcare_project/`: Project settings and main URL routing.
- `templates/`: Global templates (base, auth).
- `static/`: Static assets.
