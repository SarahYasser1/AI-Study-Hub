from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Resource, ResourceType
from .forms import ResourceForm
from core.models import log_activity


@login_required
def resource_list(request):
    resources = Resource.objects.filter(user=request.user)
    query = request.GET.get('q', '')
    if query:
        resources = resources.filter(Q(title__icontains=query) | Q(description__icontains=query))
    type_id = request.GET.get('type', '')
    if type_id:
        resources = resources.filter(resource_type_id=type_id)

    paginator = Paginator(resources.distinct(), 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    resource_types = ResourceType.objects.all()

    return render(request, 'resources/resource_list.html', {
        'page_obj': page_obj, 'query': query, 'resource_types': resource_types,
        'selected_type': type_id,
    })


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    return render(request, 'resources/resource_detail.html', {'resource': resource})


@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.save()
            form.save_m2m()
            log_activity(request.user, 'resource_added', f'Added resource "{resource.title}"')
            messages.success(request, 'Resource added.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'New Resource'})


@login_required
def resource_update(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(instance=resource, user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Edit Resource'})


@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted.')
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})
