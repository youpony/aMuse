from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from muse.rest.models import Tour, Post
from muse.papacastoro import forms


def tour(request, public_id):
    t = get_object_or_404(Tour, public_id=public_id)
    p = t.post_set.all()
    return render(request,
                  'papacastoro/index.html',
                  {'tour': t, 'posts': p, 'host': request.get_host()})


class PostList(ListView):
    model = Post
    template_name = 'papacastoro/post/posts_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.tour = get_object_or_404(
            Tour, private_id=self.kwargs['private_id']
        )

        return Post.objects.filter(tour=self.tour)

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['tour_private_id'] = self.kwargs['private_id']
        return context


class PostDelete(DeleteView):
    model = Post
    template_name = 'papacastoro/post/post_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('posts_list', args=[self.kwargs['private_id']])

    def get_context_data(self, **kwargs):
        context = super(PostDelete, self).get_context_data(**kwargs)

        context['undo_url'] = reverse(
            'posts_list', args=[self.kwargs['private_id']]
        )
        return context

    def delete(self, request, *args, **kwargs):
        tour = get_object_or_404(Tour, private_id=self.kwargs['private_id'])
        index = self.get_object().ordering_index
        result = super(PostDelete, self).delete(request, *args, **kwargs)

        posts = Post.objects.filter(tour=tour)[index:]

        for post in posts:
            post.ordering_index -= 1
            post.save()

        return result


class PostComment(UpdateView):
    model = Post
    form_class = forms.PostCommentForm
    template_name = 'papacastoro/post/post_comment.html'

    def get_success_url(self):
        return reverse_lazy('posts_list', args=[self.kwargs['private_id']])

    def get_context_data(self, **kwargs):
        context = super(PostComment, self).get_context_data(**kwargs)

        post = self.get_object()
        context['itemimages'] = (
            post.item.itemimage_set.all() if post.item else None
        )
        context['userimage'] = post.image
        return context


class PostAddPersonal(CreateView):
    model = Post
    form_class = forms.AddPersonalPostForm
    template_name = 'papacastoro/post/post_personal.html'

    def get_success_url(self):
        return reverse_lazy('posts_list', args=[self.kwargs['private_id']])

    def form_valid(self, form):
        self.tour = get_object_or_404(
            Tour, private_id=self.kwargs['private_id']
        )

        ordering_index = 1
        latest_post = self.tour.post_set.latest('ordering_index')
        if latest_post:
            ordering_index = latest_post.ordering_index + 1

        self.object = form.save(commit=False)
        self.object.tour = self.tour
        self.object.ordering_index = ordering_index
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
