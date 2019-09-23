import os

import requests
from django.contrib.auth.models import User
from django.core import validators
from django.core.files.base import ContentFile
from django.db import models


class Post(models.Model):
    url = models.URLField(max_length=200, default="", blank=True)
    title = models.CharField(max_length=200)
    cover = models.FileField(upload_to="pdf/", validators=[validators.FileExtensionValidator(['pdf'],
	     message='file must be pdf')])
    # cover = models.ImageField(upload_to="images/", default=None, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def save(self, *args, **kwargs):
        if self.url and not self.cover:
            response = requests.get(self.url)
            if response.status_code == 200:
                self.cover.save(os.path.basename(self.url), ContentFile(response.content), save=True)
            else:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Operation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=200)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None)

