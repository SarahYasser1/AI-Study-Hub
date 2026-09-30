from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from notes.models import Note
from planner.models import Task
from resources.models import Resource


@login_required
def global_search(request):
    """Powers the JS live-search bar: searches Notes, Tasks and Resources at once."""
    query = request.GET.get('q', '').strip()
    results = {'notes': [], 'tasks': [], 'resources': []}

    if len(query) >= 2:
        notes = Note.objects.filter(user=request.user).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:5]
        tasks = Task.objects.filter(user=request.user).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        resources = Resource.objects.filter(user=request.user).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]

        results['notes'] = [{'id': n.id, 'title': n.title, 'url': n.get_absolute_url()} for n in notes]
        results['tasks'] = [{'id': t.id, 'title': t.title, 'url': '/planner/'} for t in tasks]
        results['resources'] = [{'id': r.id, 'title': r.title, 'url': r.get_absolute_url()} for r in resources]

    return JsonResponse(results)


def set_theme(request):
    """Toggle dark mode; stored as a cookie so it's remembered per browser."""
    theme = request.GET.get('theme', 'light')
    next_url = request.GET.get('next', '/')
    response = JsonResponse({'theme': theme}) if request.headers.get('x-requested-with') == 'XMLHttpRequest' else None
    from django.shortcuts import redirect
    if response is None:
        response = redirect(next_url)
    response.set_cookie('theme', theme, max_age=365 * 24 * 60 * 60)
    return response
