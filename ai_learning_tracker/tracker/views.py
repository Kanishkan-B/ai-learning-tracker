from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import base64
import json
from .models import LearningLog, UserProfile, MotivationalQuote, LearningActivity
from .forms import LearningLogForm, SearchForm

def is_admin(user):
    return user.is_superuser

def login_view(request):
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
    
    # Get random quote
    quotes_count = MotivationalQuote.objects.count()
    quote = None
    if quotes_count > 0:
        quote = MotivationalQuote.objects.all()[0]
    
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
def view_log(request, record_id):
    log = get_object_or_404(LearningLog, record_id=record_id, user=request.user)
    return render(request, 'tracker/view_log.html', {'log': log})

@login_required
def download_file(request, record_id):
    log = get_object_or_404(LearningLog, record_id=record_id, user=request.user)
    
    if not log.file_base64:
        return HttpResponse('No file attached', status=404)
    
    # Decode Base64 to binary
    file_data = base64.b64decode(log.file_base64)
    
    # Create HTTP response with file
    response = HttpResponse(file_data, content_type=log.file_type)
    response['Content-Disposition'] = f'attachment; filename="{log.file_name}"'
    
    return response

@login_required
def my_magics(request):
    """View all uploads/files for the current user"""
    logs_with_files = LearningLog.objects.filter(
        user=request.user, 
        file_base64__isnull=False
    ).exclude(file_base64='').order_by('-date', '-created_at')
    
    context = {
        'logs_with_files': logs_with_files,
    }
    
    return render(request, 'tracker/my_magics.html', context)

@login_required
def search_logs(request):
    form = SearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            results = LearningLog.objects.filter(
                Q(user=request.user),
                Q(record_id__icontains=query) |
                Q(title__icontains=query) |
                Q(tags__icontains=query) |
                Q(notes__icontains=query)
            )
    
    return render(request, 'tracker/search.html', {'form': form, 'results': results})

@login_required
def get_random_quote(request):
    """API endpoint for getting random quote"""
    quotes_count = MotivationalQuote.objects.count()
    if quotes_count > 0:
        import random
        random_index = random.randint(0, quotes_count - 1)
        quote = MotivationalQuote.objects.all()[random_index]
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
        text = request.POST.get('text')
        author = request.POST.get('author', '')
        if text:
            MotivationalQuote.objects.create(text=text, author=author)
            return redirect('manage_quotes')
    
    quotes = MotivationalQuote.objects.all().order_by('-created_at')
    return render(request, 'tracker/manage_quotes.html', {'quotes': quotes})

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
            'has_file': bool(log.file_base64)
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
