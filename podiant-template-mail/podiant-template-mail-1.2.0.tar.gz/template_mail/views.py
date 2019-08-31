from django.db import transaction
from django.http.response import Http404
from django.views.generic.base import TemplateView
from .models import Tag


class TagUnsubscribeView(TemplateView):
    template_name = 'email/tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.method == 'GET':
            with transaction.atomic():
                try:
                    tag = Tag.objects.select_for_update().get(
                        hash=self.kwargs['hash']
                    )
                except Tag.DoesNotExist:
                    raise Http404('Tag matching query not found.')

                tag.unsubscribed = True
                tag.save()

            context['tag'] = tag

        return context
