def theme(request):
    """Expose the user's saved dark-mode preference to all templates."""
    dark_mode = request.COOKIES.get('theme') == 'dark'
    return {'dark_mode': dark_mode}
