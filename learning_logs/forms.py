from django import forms
from .models import Topic, Entry

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        # Model fields used in form
        fields = ['text', 'public']
        labels = {'text': 'Topic name', 'public': 'Public reading'}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': 'Entry text:'}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
