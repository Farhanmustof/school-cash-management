
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from .models import Classroom, AcademicYear, School
from .forms import ClassroomForm


@method_decorator(login_required, name='dispatch')
class ClassroomListView(View):
    def get(self, request):
        classrooms = Classroom.objects.select_related('academic_year', 'homeroom_teacher')
        return render(request, 'classes/list.html', {'classrooms': classrooms})


@method_decorator(login_required, name='dispatch')
class ClassroomCreateView(View):
    def get(self, request):
        form = ClassroomForm()
        return render(request, 'classes/form.html', {'form': form, 'title': 'Tambah Kelas'})

    def post(self, request):
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f'Kelas {classroom.name} berhasil ditambahkan.')
            return redirect('classes:list')
        return render(request, 'classes/form.html', {'form': form, 'title': 'Tambah Kelas'})


@method_decorator(login_required, name='dispatch')
class ClassroomDetailView(View):
    def get(self, request, pk):
        classroom = get_object_or_404(Classroom, pk=pk)
        students = classroom.students.filter(is_active=True)
        return render(request, 'classes/detail.html', {'classroom': classroom, 'students': students})