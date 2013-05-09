from django.forms import ModelForm

from muse.rest.models import Post


class AddPersonalPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('image', 'text')


class PostCommentForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text',)
