from django.views.generic import TemplateView

from home.models import ContactPage


class StudioLeasingView(TemplateView):
    template_name = 'home/studio-leasing.html'

    def get(self, request, *args, **kwargs):
        try:
            form_page = ContactPage.objects.get(slug='studio-leasing-getting-started')
        except ContactPage.DoesNotExist:
            pass
        else:
            self.extra_context = {
                'page': form_page,
                'form': form_page.get_form(page=form_page, user=request.user),
                'title': 'Lease a Studio',
            }
        return super().get(request, *args, **kwargs)
