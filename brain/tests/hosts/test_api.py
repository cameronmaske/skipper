from django.test import TestCase
from django.core.urlresolvers import reverse

import json
from rest_framework.test import APIRequestFactory

from hosts.api.views import host_list

factory = APIRequestFactory()


class HostApiViewsTestCase(TestCase):
    def test_get_list(self):
        request = factory.get(reverse('api-v1:host_list'))
        response = host_list(request)
        response.render()
        # WIP
        self.assertEquals(len(json.loads(response.content)), 1)
