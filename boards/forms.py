from django import forms
from .models import Post,Board,Topic,User

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    class Meta:
        model = Topic
        fields = ['subject', 'message']

class NewBoard(forms.ModelForm):
    name = forms.CharField(max_length=100,help_text='the max length is 400')
    class  Meta:
        model = Board
        fields = ['name','description']

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'What is on your mind?'}), max_length=4000,help_text='The max length of the text is 4000.')

    class Meta:
        model = Topic
        fields = ['subject', 'message']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]