
from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'classroom', 'nis', 'nisn', 'full_name', 'gender',
            'birth_date', 'birth_place', 'address', 'phone', 'photo',
            'parent_name', 'parent_phone', 'parent_email', 'notes', 'is_active'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }