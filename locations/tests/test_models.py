from django.test import TestCase

from locations.models import LocationsIndexPage


class LocationsIndexPageTests(TestCase):

    fixtures = ['location_pages']

    def test_index_page_renders_correctly(self):
        page = LocationsIndexPage.objects.get(pk=4)

        response = self.client.get(page.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Locations")
        self.assertContains(response, "My Beautiful Salon")
