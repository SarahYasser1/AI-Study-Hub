from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count

from planner.models import Task
from notes.models import Note
from resources.models import Resource
from core.models import ActivityLog


@login_required
def home(request):
    user = request.user
    tasks = Task.objects.filter(user=user)
    notes = Note.objects.filter(user=user)
    resources = Resource.objects.filter(user=user)
    activities = ActivityLog.objects.filter(user=user)[:10]

    priority_counts = tasks.values('priority').annotate(count=Count('id'))
    priority_data = {row['priority']: row['count'] for row in priority_counts}

    context = {
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(is_completed=True).count(),
        'pending_tasks': tasks.filter(is_completed=False).count(),
        'total_notes': notes.count(),
        'total_resources': resources.count(),
        'activities': activities,
        'upcoming_tasks': tasks.filter(is_completed=False).order_by('due_date')[:5],
        'recent_notes': notes.order_by('-updated_at')[:5],
        'priority_low': priority_data.get('low', 0),
        'priority_medium': priority_data.get('medium', 0),
        'priority_high': priority_data.get('high', 0),
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def export_tasks_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm

    tasks = Task.objects.filter(user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_tasks.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    p.setFont('Helvetica-Bold', 16)
    p.drawString(2 * cm, y, 'AI Study Hub — My Tasks')
    y -= 1 * cm
    p.setFont('Helvetica', 9)
    p.drawString(2 * cm, y, f'Exported for: {request.user.username}')
    y -= 1 * cm

    p.setFont('Helvetica-Bold', 10)
    p.drawString(2 * cm, y, 'Title')
    p.drawString(9 * cm, y, 'Due date')
    p.drawString(12 * cm, y, 'Priority')
    p.drawString(15 * cm, y, 'Status')
    y -= 0.5 * cm
    p.line(2 * cm, y, 19 * cm, y)
    y -= 0.5 * cm

    p.setFont('Helvetica', 9)
    for task in tasks:
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm
        p.drawString(2 * cm, y, task.title[:45])
        p.drawString(9 * cm, y, str(task.due_date) if task.due_date else '-')
        p.drawString(12 * cm, y, task.get_priority_display())
        p.drawString(15 * cm, y, 'Done' if task.is_completed else 'Pending')
        y -= 0.6 * cm

    p.showPage()
    p.save()
    return response
