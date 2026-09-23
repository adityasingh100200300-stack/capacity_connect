from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from profiles.models import Skill
from .models import TrainerCompetency
from .forms import TrainerCompetencyForm

User = get_user_model()


@login_required
def competency_map_view(request):
    """
    Shows a matrix of trainers and their top skills.
    Useful for identifying who to assign to a particular subject.
    Reads from TrainerCompetency (auto-synced from UserSkill via signals).
    """
    skills = Skill.objects.all()
    trainers = User.objects.filter(role='TRAINER', status='ACTIVE')

    # Build competency matrix using TrainerCompetency (not UserSkill directly)
    matrix = []
    for trainer in trainers:
        skills_map = {
            tc.skill.name: tc.score
            for tc in TrainerCompetency.objects.filter(trainer=trainer).select_related('skill')
        }
        matrix.append({'trainer': trainer, 'skills': skills_map})

    return render(request, 'competencies/map.html', {
        'matrix': matrix,
        'skills': skills,
    })


@login_required
def my_competencies_view(request):
    """
    Lets a trainer see and manually adjust their competency scores.
    """
    if request.user.role != 'TRAINER':
        messages.error(request, "Only trainers can access this page.")
        return redirect('competency_map')

    competencies = TrainerCompetency.objects.filter(
        trainer=request.user
    ).select_related('skill').order_by('-score')

    return render(request, 'competencies/my_competencies.html', {
        'competencies': competencies,
    })


@login_required
def competency_update_view(request, pk):
    """
    Lets a trainer manually update the score for one of their competencies.
    """
    competency = get_object_or_404(TrainerCompetency, pk=pk)

    if competency.trainer != request.user:
        messages.error(request, "You can only edit your own competencies.")
        return redirect('my_competencies')

    if request.method == 'POST':
        form = TrainerCompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated '{competency.skill.name}' score.")
            return redirect('my_competencies')
    else:
        form = TrainerCompetencyForm(instance=competency)

    return render(request, 'competencies/competency_form.html', {
        'form': form,
        'competency': competency,
    })
