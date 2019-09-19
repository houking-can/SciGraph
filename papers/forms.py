from django import forms
from .models import Post


class UploadForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "cover", "url"]

    def clean(self):
        super().clean()
