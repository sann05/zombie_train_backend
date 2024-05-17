from datetime import datetime

from django.db.models import Max
from django.shortcuts import render

from api.models import Score


def leaderboard(request):
    today = datetime.now().date()
    scores = (
        Score.objects.filter(score_ts__date=today)
        .values('user__username')
        .annotate(daily_max_points=Max('points'))
        .order_by('-daily_max_points')
    )
    context = {
        'scores': scores,
        'date': today,
    }
    return render(request, 'leaderboard.html', context)
