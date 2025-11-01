from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import PatientSignUpForm, DoctorSignUpForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user and user.role == 'admin':
                login(request, user)
                messages.success(request, 'Welcome back, Admin!')
                return redirect('admin_dashboard')
            messages.error(request, 'Only admin users can sign in here.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/admin_login.html', {'form': form})


def doctor_login(request):
    """Doctor login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.role == 'doctor':
                login(request, user)
                messages.success(request, f'Welcome back, Dr. {user.get_full_name()}!')
                return redirect('dashboard')
            elif user is not None:
                messages.error(request, 'Only doctors can login here. Please use patient login.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/doctor_login.html', {'form': form})

def patient_signup(request):
    """Patient signup view"""
    is_admin_user = request.user.is_authenticated and request.user.role == 'admin'
    if request.user.is_authenticated and not is_admin_user:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if is_admin_user:
                messages.success(request, 'Patient account created successfully!')
                return redirect('admin_dashboard')
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome aboard.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PatientSignUpForm()
    
    return render(request, 'accounts/patient_signup.html', {'form': form})

def doctor_signup(request):
    """Doctor signup view"""
    is_admin_user = request.user.is_authenticated and request.user.role == 'admin'
    if request.user.is_authenticated and not is_admin_user:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if is_admin_user:
                messages.success(request, 'Doctor account created successfully!')
                return redirect('admin_dashboard')
            messages.success(request, 'Application submitted successfully! Your account is pending approval.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DoctorSignUpForm()
    
    return render(request, 'accounts/doctor_signup.html', {'form': form})

@login_required(login_url='login')
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required(login_url='login')
def profile_view(request):
    """User profile view"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'accounts/profile.html', context)

def about(request):
    """About page"""
    return render(request, 'about.html')

def services(request):
    """Services page"""
    return render(request, 'services.html')

def contact(request):
    """Contact page"""
    return render(request, 'contact.html')