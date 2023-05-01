from django.db import models
from django.db.models import BooleanField
from django.http import HttpResponseNotAllowed, HttpResponse
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, StreamFieldPanel
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.templatetags.wagtailcore_tags import richtext


class HomePage(Page):
    subpage_types = [
        'locations.LocationsIndexPage',
        'home.ContactPage',
        'home.StandardPage',
    ]


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    visible = BooleanField(default=True)

    landing_message = RichTextField(default='')

    parent_page_type = ['home.HomePage']

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('form_fields', label="Form fields"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], 'Email'),
        FieldPanel('landing_message', help_text="Message to show the user after form submission"),
    ]

    settings_panels = AbstractEmailForm.settings_panels + [
        FieldPanel('visible'),
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for bound_field in form:
            bound_field.field.widget.attrs['placeholder'] = bound_field.label
            bound_field.field.widget.attrs['class'] = 'form-control'
            if bound_field.widget_type == 'textarea':
                bound_field.field.widget.attrs['rows'] = '2'
        return form

    def render_landing_page(self, request, *args, **kwargs):
        if request.GET.get('embeded') == 'true':
            return HttpResponse(richtext(self.landing_message))
        return super().render_landing_page(request, *args, **kwargs)

    def serve(self, request, *args, **kwargs):
        if not self.visible and request.method == 'GET':
            return HttpResponseNotAllowed(['POST'])
        return super().serve(request, *args, **kwargs)


class StandardPage(Page):
    body = StreamField([
        ('richtext', RichTextBlock()),
    ])

    subpage_types = ['home.StandardPage']

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
