from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Conversation, Message
from .services import chat_reply
from core.models import log_activity


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'ai_assistant/conversation_list.html', {'conversations': conversations})


@login_required
def conversation_detail(request, pk=None):
    if pk:
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    else:
        conversation = Conversation.objects.create(user=request.user, title='New conversation')
        return redirect('ai_assistant:conversation_detail', pk=conversation.pk)

    conversations = Conversation.objects.filter(user=request.user)
    messages_qs = conversation.messages.all()
    return render(request, 'ai_assistant/conversation_detail.html', {
        'conversation': conversation,
        'conversations': conversations,
        'chat_messages': messages_qs,
    })


@login_required
@require_POST
def send_message(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    Message.objects.create(conversation=conversation, role=Message.ROLE_USER, content=content)

    if conversation.title == 'New conversation':
        conversation.title = content[:60]
        conversation.save(update_fields=['title'])

    history = [
        {'role': m.role, 'content': m.content}
        for m in conversation.messages.all()
    ]
    reply = chat_reply(history)
    assistant_msg = Message.objects.create(conversation=conversation, role=Message.ROLE_ASSISTANT, content=reply)
    conversation.save()  # bump updated_at

    log_activity(request.user, 'ai_used', 'Chatted with the AI assistant')

    return JsonResponse({
        'reply': reply,
        'conversation_title': conversation.title,
        'message_id': assistant_msg.id,
    })


@login_required
def conversation_delete(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    if request.method == 'POST':
        conversation.delete()
        return redirect('ai_assistant:conversation_list')
    return render(request, 'ai_assistant/conversation_confirm_delete.html', {'conversation': conversation})
