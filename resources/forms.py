from django import forms
from .models import Resource, Category


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'link', 'resource_type', 'categories', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categories'].queryset = Category.objects.filter(user=user)
