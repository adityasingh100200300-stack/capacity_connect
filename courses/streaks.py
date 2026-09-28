# New file: courses/streaks.py
# Call record_engagement(request.user) from any view where a trainee does
# something real: downloading a resource, attempting/submitting an assessment,
# posting or replying to a doubt. Safe to call multiple times a day — only
# the first call each day advances anything.

from datetime import timedelta

from django.utils import timezone

from .models import Achievement, TraineeAchievement, TraineeStreak

STREAK_MILESTONES = [3, 7, 14, 30, 60, 100]


def record_engagement(user):
    if getattr(user, 'role', None) != 'TRAINEE':
        return

    streak, _ = TraineeStreak.objects.get_or_create(trainee=user)
    today = timezone.localdate()

    if streak.last_active_date == today:
        return  # already counted today, nothing to do

    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1  # missed a day (or first-ever engagement) — reset

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_active_date = today
    streak.save()

    _check_streak_achievements(user, streak.current_streak)


def _check_streak_achievements(user, current_streak):
    if current_streak not in STREAK_MILESTONES:
        return
    code = f'streak_{current_streak}'
    achievement, _ = Achievement.objects.get_or_create(
        code=code,
        defaults={
            'title': f'{current_streak}-Day Streak',
            'description': f'Stayed active {current_streak} days in a row.',
            'icon': '🔥',
        }
    )
    TraineeAchievement.objects.get_or_create(trainee=user, achievement=achievement)