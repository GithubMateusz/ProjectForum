from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from ..forms import TopicForm, ReplyForm
from ..models import Topic, Category, Reply


@method_decorator(login_required, 'dispatch')
class AddTopicView(CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'forum/topic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['reply'] = ReplyForm(self.request.POST)
        else:
            context['reply'] = ReplyForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        reply_form = ReplyForm(self.request.POST, instance=Reply())
        if form.is_valid() and reply_form.is_valid():
            self.form_valid(form, reply_form)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, reply=reply_form))

    def form_valid(self, form, reply_form):
        form.instance.author = self.request.user
        reply_form.instance.author = self.request.user
        category = Category.objects.get(
            pk=self.kwargs['pk'])

        self.object = form.save(commit=False)
        self.object.category = category
        self.object.save()

        reply = reply_form.save(commit=False)
        reply.topic = self.object
        reply.save()

    def form_invalid(self, form, reply_form):
        return self.render_to_response(
            self.get_context_data(form=form, reply=reply_form)
        )

    def get_success_url(self):
        return reverse('category', args=[
            self.object.category.parent.slug,
            self.object.category.slug])
