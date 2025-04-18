from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from .models import ScamReport, ScamEvidence, ReportComment, UserProfile, ReportEvidence, Donation
from .forms import (
    ScamReportForm, ScamEvidenceForm, CommentForm, EvidenceForm, DonationForm,
    CustomLoginForm, CustomSignUpForm, CustomPasswordResetForm
)
from .utils import analyze_url, extract_metadata
import os
from django.conf import settings
from django.http import JsonResponse
import time
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

@login_required
def secure_page(request):
    return render(request, 'secure_page.html')

@login_required
def submit_report(request):
    if request.method == 'POST':
        form = ScamReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.is_blacklisted = False
            report.is_public = True
            report.status = 'pending'
            report.save()
            messages.success(request, 'Report submitted successfully!')
            return redirect('my_reports')
    else:
        form = ScamReportForm()
    return render(request, 'submit_report.html', {'form': form})

@login_required
def upload_evidence(request, report_id):
    report = get_object_or_404(ScamReport, id=report_id)
    
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.report = report
            evidence.user = request.user
            evidence.save()
            messages.success(request, 'Your evidence added successfully.')
            return redirect('view_report', report_id=report.id)
    else:
        form = EvidenceForm()
    
    return render(request, 'upload_evidence.html', {
        'form': form,
        'report': report
    })

def view_report(request, report_id):
    report = get_object_or_404(ScamReport, id=report_id)
    
    # Increment view count
    report.views += 1
    report.save()
    
    # Analyze URL
    url_analysis = analyze_url(report.scam_url)
    
    # Handle evidence submission
    if request.method == 'POST' and request.user.is_authenticated:
        evidence_form = EvidenceForm(request.POST, request.FILES)
        if evidence_form.is_valid():
            evidence = evidence_form.save(commit=False)
            evidence.report = report
            evidence.user = request.user
            evidence.save()
            messages.success(request, 'Evidence submitted successfully.')
            return redirect('view_report', report_id=report.id)
    else:
        evidence_form = EvidenceForm()
    
    context = {
        'report': report,
        'evidence_form': evidence_form,
        'url_analysis': url_analysis,
    }
    return render(request, 'view_report.html', context)

@login_required
def my_reports(request):
    reports = ScamReport.objects.filter(reporter=request.user).order_by('-submission_date')
    return render(request, 'my_reports.html', {'reports': reports})

def public_reports(request):
    reports = ScamReport.objects.filter(is_public=True).order_by('-submission_date')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(report_type__icontains=search_query)
        )
    
    context = {
        'reports': reports,
        'search_query': search_query
    }
    return render(request, 'public_reports.html', context)

def scam_websites(request):
    query = request.GET.get('q', '')
    report_type = request.GET.get('type', '')
    
    reports = ScamReport.objects.filter(is_public=True)
    
    if query:
        reports = reports.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(scam_url__icontains=query)
        )
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    reports = reports.order_by('-submission_date')
    
    context = {
        'reports': reports,
        'query': query,
        'selected_type': report_type
    }
    return render(request, 'scam_websites.html', context)

@login_required
def profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile
    }
    return render(request, 'profile.html', context)

@login_required
def add_comment(request, report_id):
    report = get_object_or_404(ScamReport, id=report_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.report = report
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comments has been added successfully.')
            return redirect('view_report', report_id=report.id)
    else:
        form = CommentForm()
    return render(request, 'view_report.html', {'report': report, 'comment_form': form})

@login_required
def add_evidence(request, report_id):
    report = get_object_or_404(ScamReport, id=report_id)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.report = report
            evidence.user = request.user
            evidence.save()
            messages.success(request, 'Your evidence has been added successfully..')
            return redirect('view_report', report_id=report.id)
    else:
        form = EvidenceForm()
    return render(request, 'view_report.html', {'report': report, 'evidence_form': form})

@login_required
def verify_comment(request, comment_id):
    if request.user.is_staff:
        comment = get_object_or_404(ReportComment, id=comment_id)
        comment.is_verified = True
        comment.verified_by = request.user
        comment.save()
        messages.success(request, 'Your comments has been verified successfully.')
    return redirect('view_report', report_id=comment.report.id)

@login_required
def verify_evidence(request, evidence_id):
    if request.user.is_staff:
        evidence = get_object_or_404(ReportEvidence, id=evidence_id)
        evidence.is_verified = True
        evidence.verified_by = request.user
        evidence.save()
        messages.success(request, 'Your evidence has been verified successfully.')
    return redirect('view_report', report_id=evidence.report.id)

@login_required
def donate(request, report_id=None):
    if report_id:
        report = get_object_or_404(ScamReport, id=report_id)
    else:
        report = None

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            # Create donation record
            donation = Donation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                amount=form.cleaned_data['amount'],
                currency=form.cleaned_data['currency'],
                payment_status='completed',  
                is_anonymous=request.POST.get('is_anonymous', False),
                message=request.POST.get('message', ''),
                transaction_id=f"DEMO-{timezone.now().timestamp()}",  
                report=report 
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid form data'})
    else:
        form = DonationForm()
    
    return render(request, 'donate.html', {
        'form': form,
        'report': report
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}!')
            return redirect('home')
    else:
        form = CustomSignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

def password_reset_view(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No user found with that email address.')
                return redirect('password_reset')


            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            

            reset_link = request.build_absolute_uri(
                f'/reset-password-confirm/{uid}/{token}/'
            )
            

            subject = 'Password Reset Request'
            message = render_to_string('auth/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            
            send_mail(
                subject,
                message,
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'auth/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'auth/password_reset_confirm.html')
    else:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('password_reset')
