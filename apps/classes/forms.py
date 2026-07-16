
from django import forms
from .models import Classroom, AcademicYear, School


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['school', 'academic_year', 'name', 'grade', 'homeroom_teacher', 'monthly_dues', 'description']