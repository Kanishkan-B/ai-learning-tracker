from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    streak = models.IntegerField(default=0)
    last_log_date = models.DateField(null=True, blank=True)
    total_logs = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def update_streak(self, log_date):
        if self.last_log_date:
            delta = (log_date - self.last_log_date).days
            if delta == 1:
                self.streak += 1
            elif delta > 1:
                self.streak = 1
        else:
            self.streak = 1
        self.last_log_date = log_date
        self.save()

class LearningLog(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('csharp', 'C#'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('ruby', 'Ruby'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('php', 'PHP'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('sql', 'SQL'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('typescript', 'TypeScript'),
        ('r', 'R'),
        ('matlab', 'MATLAB'),
        ('bash', 'Bash/Shell'),
        ('powershell', 'PowerShell'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
        ('xml', 'XML'),
        ('markdown', 'Markdown'),
        ('other', 'Other'),
    ]
    
    record_id = models.CharField(max_length=6, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_logs')
    title = models.CharField(max_length=200)
    notes = models.TextField()
    code_snippet = models.TextField(blank=True, null=True)
    code_language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='python', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # File storage using Base64
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    file_base64 = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.record_id:
            self.record_id = self.generate_unique_id()
        super().save(*args, **kwargs)
        
        # Update user streak
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.update_streak(self.date)
        profile.total_logs = LearningLog.objects.filter(user=self.user).count()
        profile.save()
    
    def generate_unique_id(self):
        while True:
            record_id = ''.join(random.choices(string.digits, k=6))
            if not LearningLog.objects.filter(record_id=record_id).exists():
                return record_id
    
    def __str__(self):
        return f'{self.record_id} - {self.title}'

class MotivationalQuote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.text[:50]}...' if len(self.text) > 50 else self.text

class LearningActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.count} logs'


class Effort(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='efforts')
    learning_topic = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    comments = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.learning_topic} ({self.start_date} - {self.end_date})'
    
    def get_progress_percentage(self):
        """Progress = (today - start) / (end - start), capped at 100 if completed."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.status == 'completed':
            return 100
        if today <= self.start_date:
            return 0
        if today >= self.end_date:
            return 100
        total_days = (self.end_date - self.start_date).days
        if total_days <= 0:
            return 100
        elapsed = (today - self.start_date).days
        return min(100, round(100 * elapsed / total_days, 1))
    
    def days_remaining(self):
        """Days until end_date (negative if past)."""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.end_date - today).days
