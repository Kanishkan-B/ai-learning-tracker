from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import urllib.request
import urllib.error
from .models import LearningLog, UserProfile, MotivationalQuote, LearningActivity, Effort, JobApplication
from .forms import LearningLogForm, SearchForm, EffortForm, CompleteEffortForm, MotivationalQuoteForm, JobApplicationForm

def is_admin(user):
    return user.is_superuser

def login_view(request):
    # If already logged in, go straight to dashboard
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'tracker/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tracker/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get recent logs
    recent_logs = LearningLog.objects.filter(user=user)[:5]
    
    # Get all users with profiles for leaderboard
    leaderboard = UserProfile.objects.select_related('user').order_by('-streak')[:10]
    
    # Get activity data for heatmap (last 365 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    activities = LearningActivity.objects.filter(
        user=user, 
        date__gte=start_date
    ).values('date', 'count')
    
    # Convert to dict for easy JavaScript access
    activity_map = {str(a['date']): a['count'] for a in activities}
    
    # Get next quote in sequence
    quotes_count = MotivationalQuote.objects.count()
    quote = None
    if quotes_count > 0:
        # Get current position from session, default to 0
        current_position = request.session.get('quote_position', 0)
        
        # Get all quotes ordered by ID for consistency
        quotes = list(MotivationalQuote.objects.all().order_by('id'))
        
        # Get the quote at current position
        quote = quotes[current_position % quotes_count]
        
        # Update position for next request
        request.session['quote_position'] = (current_position + 1) % quotes_count
    
    context = {
        'profile': profile,
        'recent_logs': recent_logs,
        'leaderboard': leaderboard,
        'activity_map': json.dumps(activity_map),
        'quote': quote,
    }
    
    return render(request, 'tracker/dashboard.html', context)

@login_required
def create_log(request):
    if request.method == 'POST':
        form = LearningLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            
            # Update activity count
            activity, created = LearningActivity.objects.get_or_create(
                user=request.user,
                date=log.date,
                defaults={'count': 1}
            )
            if not created:
                activity.count += 1
                activity.save()
            
            return redirect('dashboard')
    else:
        form = LearningLogForm(initial={'date': timezone.now().date()})
    
    return render(request, 'tracker/create_log.html', {'form': form})


@login_required
def edit_log(request, record_id):
    log = get_object_or_404(LearningLog, record_id=record_id, user=request.user)
    if request.method == 'POST':
        form = LearningLogForm(request.POST, request.FILES, instance=log)
        if form.is_valid():
            form.save()
            return redirect('my_magics')
    else:
        form = LearningLogForm(instance=log)
    
    return render(request, 'tracker/edit_log.html', {'form': form, 'log': log})

@login_required
def view_log(request, record_id):
    log = get_object_or_404(LearningLog, record_id=record_id, user=request.user)
    return render(request, 'tracker/view_log.html', {'log': log})

@login_required
def download_file(request, record_id):
    log = get_object_or_404(LearningLog, record_id=record_id, user=request.user)
    
    if not log.file_url:
        return HttpResponse('No file attached', status=404)
    
    # Fetch bytes from Supabase Storage URL.
    try:
        with urllib.request.urlopen(log.file_url) as resp:
            file_data = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError):
        return HttpResponse('Unable to fetch attached file', status=502)
    
    # Create HTTP response with file
    response = HttpResponse(file_data, content_type=log.file_type or 'application/octet-stream')
    filename = (log.file_name or 'download').replace('"', "")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def my_magics(request):
    """View all learning entries for the current user"""
    logs_with_files = LearningLog.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')
    attachments_count = logs_with_files.exclude(file_url__isnull=True).exclude(file_url='').count()
    
    context = {
        'logs_with_files': logs_with_files,
        'attachments_count': attachments_count,
    }
    
    return render(request, 'tracker/my_magics.html', context)


@login_required
def my_efforts(request):
    """List user's learning efforts."""
    efforts = Effort.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tracker/my_efforts.html', {'efforts': efforts})


@login_required
def create_effort(request):
    """Create a new effort."""
    if request.method == 'POST':
        form = EffortForm(request.POST)
        if form.is_valid():
            effort = form.save(commit=False)
            effort.user = request.user
            effort.save()
            return redirect('my_efforts')
    else:
        form = EffortForm(initial={
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=7),
        })
    return render(request, 'tracker/create_effort.html', {'form': form})


@login_required
def complete_effort(request, pk):
    """Mark effort as completed with comments and approval (POST from modal)."""
    effort = get_object_or_404(Effort, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CompleteEffortForm(request.POST, instance=effort)
        if form.is_valid():
            effort = form.save(commit=False)
            effort.status = 'completed'
            effort.save()
            return redirect('my_efforts')
    return redirect('my_efforts')


@login_required
def user_entries(request, username):
    """Read-only view of another user's learning entries"""
    target_user = get_object_or_404(User, username=username)
    logs = LearningLog.objects.filter(
        user=target_user
    ).order_by('-date', '-created_at')
    attachments_count = logs.exclude(file_url__isnull=True).exclude(file_url='').count()
    
    context = {
        'target_user': target_user,
        'logs': logs,
        'attachments_count': attachments_count,
    }
    return render(request, 'tracker/user_entries.html', context)


@login_required
def view_log_public(request, record_id):
    """View any user's log in read-only mode (used from shared views)"""
    log = get_object_or_404(LearningLog, record_id=record_id)
    return render(request, 'tracker/view_log.html', {'log': log})


@login_required
def download_file_public(request, record_id):
    """Download any user's attachment (used from shared views)"""
    log = get_object_or_404(LearningLog, record_id=record_id)
    
    if not log.file_url:
        return HttpResponse('No file attached', status=404)
    
    try:
        with urllib.request.urlopen(log.file_url) as resp:
            file_data = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError):
        return HttpResponse('Unable to fetch attached file', status=502)

    response = HttpResponse(file_data, content_type=log.file_type or 'application/octet-stream')
    filename = (log.file_name or 'download').replace('"', "")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def search_logs(request):
    form = SearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            # Search by record_id across ALL users (so you can find friends' logs)
            id_results = LearningLog.objects.filter(
                Q(record_id__icontains=query)
            )
            # Search by title/tags/notes only in current user's logs
            own_results = LearningLog.objects.filter(
                Q(user=request.user),
                Q(title__icontains=query) |
                Q(tags__icontains=query) |
                Q(notes__icontains=query)
            )
            # Combine and deduplicate
            results = (id_results | own_results).distinct()
    
    return render(request, 'tracker/search.html', {'form': form, 'results': results})

@login_required
def get_random_quote(request):
    """API endpoint for getting next quote in sequence"""
    quotes_count = MotivationalQuote.objects.count()
    if quotes_count > 0:
        # Get current position from session, default to 0
        current_position = request.session.get('quote_position', 0)
        
        # Get all quotes ordered by ID for consistency
        quotes = list(MotivationalQuote.objects.all().order_by('id'))
        
        # Get the quote at current position
        quote = quotes[current_position % quotes_count]
        
        # Update position for next request (cycle through all quotes)
        request.session['quote_position'] = (current_position + 1) % quotes_count
        
        return JsonResponse({
            'text': quote.text,
            'author': quote.author
        })
    return JsonResponse({'text': 'Keep learning!', 'author': 'Anonymous'})

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    total_logs = LearningLog.objects.count()
    total_quotes = MotivationalQuote.objects.count()
    
    # Get logs per user
    user_stats = User.objects.annotate(log_count=Count('learning_logs')).order_by('-log_count')
    
    context = {
        'users': users,
        'total_logs': total_logs,
        'total_quotes': total_quotes,
        'user_stats': user_stats,
    }
    
    return render(request, 'tracker/admin_dashboard.html', context)

@user_passes_test(is_admin)
def manage_quotes(request):
    if request.method == 'POST':
        form = MotivationalQuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_quotes')
    else:
        form = MotivationalQuoteForm()
    
    quotes = MotivationalQuote.objects.all().order_by('-created_at')
    return render(request, 'tracker/manage_quotes.html', {'quotes': quotes, 'form': form})

@user_passes_test(is_admin)
def delete_quote(request, quote_id):
    quote = get_object_or_404(MotivationalQuote, id=quote_id)
    quote.delete()
    return redirect('manage_quotes')

@user_passes_test(is_admin)
def export_data_json(request):
    """Export all system data as JSON"""
    data = {
        'users': [],
        'learning_logs': [],
        'quotes': [],
        'activities': [],
        'export_date': timezone.now().isoformat()
    }
    
    # Export users with profiles
    for user in User.objects.all():
        profile = UserProfile.objects.filter(user=user).first()
        data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
            'profile': {
                'streak': profile.streak if profile else 0,
                'total_logs': profile.total_logs if profile else 0,
                'last_log_date': profile.last_log_date.isoformat() if profile and profile.last_log_date else None
            }
        })
    
    # Export learning logs
    for log in LearningLog.objects.all():
        data['learning_logs'].append({
            'record_id': log.record_id,
            'user': log.user.username,
            'title': log.title,
            'notes': log.notes,
            'code_snippet': log.code_snippet,
            'tags': log.tags,
            'date': log.date.isoformat(),
            'created_at': log.created_at.isoformat(),
            'file_name': log.file_name,
            'file_type': log.file_type,
            'has_file': bool(log.file_url)
        })
    
    # Export quotes
    for quote in MotivationalQuote.objects.all():
        data['quotes'].append({
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'created_at': quote.created_at.isoformat()
        })
    
    # Export activities
    for activity in LearningActivity.objects.all():
        data['activities'].append({
            'user': activity.user.username,
            'date': activity.date.isoformat(),
            'count': activity.count
        })
    
    # Create response with JSON file
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="ai_learning_tracker_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    return response


@login_required
def my_jobs(request):
    """Display all job applications grouped by date"""
    # Get all job applications for the current user, ordered by date
    jobs = JobApplication.objects.filter(user=request.user)
    
    # Group jobs by date
    jobs_by_date = {}
    for job in jobs:
        date_str = job.date
        if date_str not in jobs_by_date:
            jobs_by_date[date_str] = []
        jobs_by_date[date_str].append(job)
    
    context = {
        'jobs_by_date': jobs_by_date,
    }
    return render(request, 'tracker/my_jobs.html', context)


@login_required
def create_job(request):
    """Create multiple job applications for a single date"""
    if request.method == 'POST':
        # Check if we're adding jobs for a date
        date = request.POST.get('date')
        
        if not date:
            # First step: just get the date
            return render(request, 'tracker/create_job.html', {})
        
        # Process multiple job entries
        jobs_created = 0
        for i in range(20):  # Maximum 20 entries
            job_link = request.POST.get(f'job_link_{i}')
            organization = request.POST.get(f'organization_{i}')
            role = request.POST.get(f'role_{i}')
            status = request.POST.get(f'status_{i}')
            
            # Skip if any field is empty
            if not all([job_link, organization, role, status]):
                continue
            
            # Create the job application
            JobApplication.objects.create(
                user=request.user,
                date=date,
                job_link=job_link,
                organization=organization,
                role=role,
                status=status
            )
            jobs_created += 1
        
        if jobs_created > 0:
            return redirect('my_jobs')
        else:
            # No jobs were created, show form again with date
            context = {
                'date': date,
                'error': 'Please add at least one job application.'
            }
            return render(request, 'tracker/create_job.html', context)
    
    return render(request, 'tracker/create_job.html', {})


@login_required
def delete_job(request, job_id):
    """Delete a job application"""
    job = get_object_or_404(JobApplication, id=job_id, user=request.user)
    job.delete()
    return redirect('my_jobs')


@login_required
def edit_job(request, job_id):
    """Edit a job application"""
    job = get_object_or_404(JobApplication, id=job_id, user=request.user)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('my_jobs')
    else:
        form = JobApplicationForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'tracker/edit_job.html', context)
