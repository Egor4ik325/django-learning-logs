from django.db import models
from django.contrib.auth.models import User
# django -> database -> models

# Create your models here.

class Topic(models.Model):
    # Model attributes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(False)

    # Model representation
    def __str__(self):
        return self.text

class Entry(models.Model):
    # Model relations
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    # Model attributes
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    # Additional model attributes
    class Meta:
        verbose_name_plural = 'entries'

    # Model representation (title)
    def __str__(self):
        if len(self.text) >= 50:
            return f"{self.text[:50]}..."
        else:
            return self.text
