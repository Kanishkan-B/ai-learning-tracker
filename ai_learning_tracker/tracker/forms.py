from django import forms
from .models import LearningLog, Effort, MotivationalQuote, JobApplication
import os

from .supabase_storage import upload_to_supabase_storage

class LearningLogForm(forms.ModelForm):
    file_upload = forms.FileField(required=False, label='Upload Document (Optional)')
    
    class Meta:
        model = LearningLog
        fields = ['title', 'notes', 'code_snippet', 'code_language', 'tags', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter title...'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Document your learning...'}),
            'code_snippet': forms.Textarea(attrs={'class': 'form-input', 'rows': 10, 'placeholder': 'Paste your code here...'}),
            'code_language': forms.Select(attrs={'class': 'form-input'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'python, machine-learning, neural-networks'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle file upload and upload to Supabase Storage.
        # Store the returned URL in `instance.file_url`.
        uploaded_file = self.files.get('file_upload')
        if uploaded_file and uploaded_file.size > 0:
            if not instance.record_id:
                instance.record_id = instance.generate_unique_id()

            instance.file_name = uploaded_file.name
            instance.file_type = uploaded_file.content_type

            # Use a deterministic object name per log record.
            # If the user replaces the file, we overwrite the same path.
            _, ext = os.path.splitext(uploaded_file.name or "")
            ext = ext.lower() if ext else ""
            object_path = f"learning_logs/{instance.record_id}/file{ext}"

            instance.file_url = upload_to_supabase_storage(
                file_obj=uploaded_file,
                object_path=object_path,
                content_type=uploaded_file.content_type,
            )
        
        if commit:
            instance.save()
        return instance

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Search by ID, title, tags, or keywords...'
        })
    )


class EffortForm(forms.ModelForm):
    class Meta:
        model = Effort
        fields = ['learning_topic', 'start_date', 'end_date']
        widgets = {
            'learning_topic': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g. Django REST API, Machine Learning basics',
            }),
            'start_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }
    
    def clean(self):
        data = super().clean()
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date must be on or after start date.')
        return data


class CompleteEffortForm(forms.ModelForm):
    class Meta:
        model = Effort
        fields = ['comments', 'approved']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'What did you learn? Key takeaways...',
            }),
        }


class MotivationalQuoteForm(forms.ModelForm):
    class Meta:
        model = MotivationalQuote
        fields = ['text', 'author']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Enter motivational quote...',
                'required': True,
            }),
            'author': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Author name (optional)',
            }),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['date', 'job_link', 'organization', 'role', 'status']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date',
            }),
            'job_link': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://company.com/careers/job-id',
            }),
            'organization': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g. Google, Microsoft, Amazon',
            }),
            'role': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g. Software Engineer, Data Scientist',
            }),
            'status': forms.Select(attrs={
                'class': 'input',
            }),
        }
