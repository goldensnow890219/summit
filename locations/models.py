from django.db import models
from django.forms import CheckboxSelectMultiple
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.core.models import Orderable
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel

from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class Service(models.Model):
    name = models.CharField(max_length=100)

    panels = [
        FieldPanel('name'),
    ]
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Space(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    wide = models.BooleanField(default=False)

    panels = [ImageChooserPanel('image'), FieldPanel('wide')]


class StudioSpace(Orderable, Space):
    page = ParentalKey(
        'locations.LocationsIndexPage', on_delete=models.CASCADE, related_name='studio_spaces'
    )


class LocationsIndexPage(Page):
    subpage_types = ['locations.LocationPage']
    parent_page_type = ['home.HomePage']

    content_panels = Page.content_panels + [
        InlinePanel('studio_spaces', label="Our studio spaces"),
    ]

    @property
    def locations(self):
        return self.get_children().live().specific()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        services = Service.objects.all()
        return {**context, 'services': services}


class Professional(index.Indexed, Orderable, ClusterableModel):
    name = models.CharField(max_length=30)
    business_name = models.CharField(max_length=100, blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    studio = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=50, blank=True)
    booking_link = models.URLField(blank=True)
    website = models.URLField(blank=True)
    social_media_link_1 = models.URLField(blank=True)
    social_media_link_2 = models.URLField(blank=True)
    services = ParentalManyToManyField('locations.Service', blank=True)

    page = ParentalKey(
        'locations.LocationPage', null=True, on_delete=models.CASCADE, related_name='professionals'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('business_name'),
        ImageChooserPanel('photo'),
        FieldPanel('studio'),
        FieldPanel('phone_number'),
        FieldPanel('email'),
        FieldPanel('password'),
        FieldPanel('booking_link'),
        FieldPanel('website'),
        FieldPanel('social_media_link_1'),
        FieldPanel('social_media_link_2'),
        FieldPanel('services', widget=CheckboxSelectMultiple)
    ]

    search_fields = [
        index.SearchField('name', partial_match=True, boost=10),
        index.SearchField('business_name', partial_match=True, boost=10),
        index.SearchField('studio'),
        index.FilterField('page'),
#        index.FilterField('live'),
#        index.SearchField('live'),
#        index.SearchField('services'),
        index.RelatedFields('services', [
            index.SearchField('name')
        ])
    ]

    class Meta:
        ordering = ['studio']

    def __str__(self):
        return self.name


class LocationPage(Page):
    parent_page_type = ['locations.LocationsIndexPage']

    address_line = models.CharField(max_length=30, blank=True)
    address_optional = models.CharField(max_length=30, blank=True, default="")
    shopping_name = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=7, blank=True)
    state_code = models.CharField(max_length=2, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('address_line'),
                FieldPanel('address_optional'),
                FieldPanel('shopping_name'),
                FieldPanel('city'),
                FieldPanel('state_code'),
                FieldPanel('zip_code'),
                FieldPanel('phone_number'),
                FieldPanel('email'),
            ],
            heading="Address Info",
        ),
        InlinePanel('professionals', label="Professionals"),
    ]

    @property
    def services(self):
        """
        :return: Available services
        """
        # Only Services available in the location are displayed
        # return Service.objects.filter(
        #     professional__in=self.professionals.values_list('id')
        # ).distinct()
        return Service.objects.all()
