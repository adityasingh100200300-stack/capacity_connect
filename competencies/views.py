from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Avg

from profiles.models import Skill, UserSkill

User = get_user_model()


@login_required
def competency_map_view(request):
    """
    Shows a matrix of trainers and their top skills.
    Useful for identifying who to assign to a particular subject.
    """
    skills = Skill.objects.all()
    trainers = User.objects.filter(role='TRAINER', status='ACTIVE')

    # Build competency matrix: {trainer: {skill_name: proficiency}}
    matrix = []
    for trainer in trainers:
        skills_map = {
            us.skill.name: us.proficiency
            for us in UserSkill.objects.filter(user=trainer).select_related('skill')
        }
        matrix.append({'trainer': trainer, 'skills': skills_map})

    return render(request, 'competencies/map.html', {
        'matrix': matrix,
        'skills': skills,
    })
