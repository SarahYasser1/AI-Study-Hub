from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Task
from .forms import TaskForm
from core.models import log_activity


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    query = request.GET.get('q', '')
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))

    status = request.GET.get('status', '')
    if status == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status == 'pending':
        tasks = tasks.filter(is_completed=False)

    priority = request.GET.get('priority', '')
    if priority:
        tasks = tasks.filter(priority=priority)

    paginator = Paginator(tasks, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'planner/task_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'priority': priority,
    })


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            log_activity(request.user, 'task_created', f'Created task "{task.title}"')
            messages.success(request, 'Task created.')
            return redirect('planner:task_list')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'planner/task_form.html', {'form': form, 'title': 'New Task'})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated.')
            return redirect('planner:task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'planner/task_form.html', {'form': form, 'title': 'Edit Task'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('planner:task_list')
    return render(request, 'planner/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    if task.is_completed:
        log_activity(request.user, 'task_completed', f'Completed task "{task.title}"')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_completed': task.is_completed})
    return redirect('planner:task_list')
