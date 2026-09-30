"""
Thin wrapper around an OpenAI-compatible chat completion API.

Configure AI_API_KEY / AI_API_URL / AI_MODEL in your .env file (see README.md).
Works out of the box with OpenAI, and with any OpenAI-compatible endpoint
(Groq, OpenRouter, local Ollama server with an OpenAI-compatible route, etc.)
by just changing AI_API_URL and AI_MODEL.

If no API key is configured, falls back to a clearly-labelled offline stub
so the rest of the app keeps working during development/demos.
"""
import requests
from django.conf import settings


class AIServiceError(Exception):
    pass


def _call_ai(messages, max_tokens=500):
    if not settings.AI_API_KEY:
        # Offline fallback — keeps the app usable without an API key.
        last_user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        return (
            "[AI is not configured yet — add AI_API_KEY to your .env file] "
            f"Here's a placeholder response to: \"{last_user_msg[:120]}\""
        )

    headers = {
        'Authorization': f'Bearer {settings.AI_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': settings.AI_MODEL,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': 0.6,
    }
    try:
        response = requests.post(settings.AI_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.RequestException as exc:
        raise AIServiceError(f'AI request failed: {exc}') from exc
    except (KeyError, IndexError) as exc:
        raise AIServiceError(f'Unexpected AI response format: {exc}') from exc


def chat_reply(conversation_history):
    """
    conversation_history: list of {'role': 'user'|'assistant', 'content': str}
    Returns the assistant's reply as a string.
    """
    system_prompt = {
        'role': 'system',
        'content': (
            'You are the AI Study Assistant inside AI Study Hub, a student '
            'productivity app. Help the user with their studies: answer '
            'questions, explain concepts, and help them plan their work. '
            'Keep answers concise and well-formatted.'
        ),
    }
    messages = [system_prompt] + conversation_history
    try:
        return _call_ai(messages)
    except AIServiceError as exc:
        return f"Sorry, I couldn't reach the AI service right now. ({exc})"


def summarize_text(text):
    messages = [
        {'role': 'system', 'content': 'Summarize the given study note in 2-4 concise bullet points.'},
        {'role': 'user', 'content': text},
    ]
    try:
        return _call_ai(messages, max_tokens=250)
    except AIServiceError as exc:
        return f"Sorry, I couldn't generate a summary right now. ({exc})"
