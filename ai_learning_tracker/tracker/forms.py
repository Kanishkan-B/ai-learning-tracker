from django import forms
from .models import LearningLog
import base64

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
        
        # Handle file upload and convert to Base64
        if 'file_upload' in self.files:
            uploaded_file = self.files['file_upload']
            instance.file_name = uploaded_file.name
            instance.file_type = uploaded_file.content_type
            
            # Read and encode file to Base64
            file_content = uploaded_file.read()
            instance.file_base64 = base64.b64encode(file_content).decode('utf-8')
        
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
