from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Note, Category
from .forms import NoteForm, CategoryForm
from core.models import log_activity
from ai_assistant.services import summarize_text


@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user)
    query = request.GET.get('q', '')
    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(content__icontains=query))
    category_id = request.GET.get('category', '')
    if category_id:
        notes = notes.filter(categories__id=category_id)

    paginator = Paginator(notes.distinct(), 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.filter(user=request.user)

    return render(request, 'notes/note_list.html', {
        'page_obj': page_obj, 'query': query, 'categories': categories,
        'selected_category': category_id,
    })


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()
            log_activity(request.user, 'note_created', f'Created note "{note.title}"')
            messages.success(request, 'Note created.')
            return redirect('notes:note_detail', pk=note.pk)
    else:
        form = NoteForm(user=request.user)
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'New Note'})


@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'note_updated', f'Updated note "{note.title}"')
            messages.success(request, 'Note updated.')
            return redirect('notes:note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note'})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect('notes:note_list')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})


@login_required
def note_summarize(request, pk):
    """AI feature: summarize a note's content on demand."""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    summary = summarize_text(note.content)
    note.ai_summary = summary
    note.save(update_fields=['ai_summary'])
    log_activity(request.user, 'ai_used', f'Summarized note "{note.title}" with AI')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'summary': summary})
    messages.success(request, 'AI summary generated.')
    return redirect('notes:note_detail', pk=note.pk)


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added.')
            return redirect('notes:category_list')
    else:
        form = CategoryForm()
    return render(request, 'notes/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('notes:category_list')
