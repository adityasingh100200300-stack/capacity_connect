import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404

from courses.models import Course, Enrollment
from .models import Resource
from .forms import ResourceUploadForm


@login_required
def resource_list_view(request):
    """
    Lists resources. Trainers see their own uploads; trainees see resources
    for courses they're enrolled in.
    """
    if request.user.role == 'TRAINER':
        resources = Resource.objects.filter(uploaded_by=request.user).select_related('course')
    elif request.user.role == 'ADMIN':
        resources = Resource.objects.all().select_related('course', 'uploaded_by')
    else:
        # Trainees: only resources from enrolled courses
        enrolled_course_ids = Enrollment.objects.filter(
            trainee=request.user
        ).values_list('course_id', flat=True)
        resources = Resource.objects.filter(course_id__in=enrolled_course_ids).select_related('course')

    return render(request, 'library/list.html', {'resources': resources})


@login_required
def upload_resource_view(request):
    """Trainer-only: upload a file to a course's library."""
    if request.user.role not in ('TRAINER', 'ADMIN'):
        messages.error(request, 'Only trainers can upload resources.')
        return redirect('resource_list')

    # Pre-select course if passed as query param
    course_id = request.GET.get('course')
    initial_course = None
    if course_id:
        initial_course = get_object_or_404(Course, id=course_id)

    # Limit course dropdown to trainer's own courses (or all for admin)
    if request.user.role == 'ADMIN':
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(trainer=request.user)

    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        selected_course_id = request.POST.get('course_id')
        selected_course = get_object_or_404(Course, id=selected_course_id)

        if form.is_valid():
            resource = form.save(commit=False)
            resource.course = selected_course
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, f'"{resource.title}" uploaded to {selected_course.title}.')
            return redirect('course_detail', course_id=selected_course.id)
    else:
        form = ResourceUploadForm()

    return render(request, 'library/upload.html', {
        'form': form,
        'courses': courses,
        'initial_course': initial_course,
    })


@login_required
def download_resource_view(request, resource_id):
    """
    Serves the file if the user is enrolled (or is Trainer/Admin).
    Prevents direct URL access by unenrolled trainees.
    """
    resource = get_object_or_404(Resource, id=resource_id)

    if request.user.role == 'TRAINEE':
        enrolled = Enrollment.objects.filter(
            trainee=request.user, course=resource.course
        ).exists()
        if not enrolled:
            raise Http404("You are not enrolled in this course.")

    if not resource.file:
        raise Http404("File not found.")

    file_path = resource.file.path
    if not os.path.exists(file_path):
        raise Http404("File not found on disk.")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
