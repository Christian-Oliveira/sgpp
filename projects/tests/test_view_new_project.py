from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.utils import timezone

import datetime
from dateutil.relativedelta import relativedelta

import random
from decimal import Decimal

from ..forms import NewProjectForm
from ..models import Project
from ..views import ProjectCreateView


class NewProjectTests(TestCase):

    def setUp(self):
        User.objects.create_user(username='test', email='teste@doe.com', password='123')
        self.client.login(username='test', password='123')
        self.url = reverse('project:create')

    def test_new_project_view_success_status_code(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_new_project_url_resolves_new_project_view(self):
        view = resolve('/project/create/')
        self.assertEquals(view.func.view_class, ProjectCreateView)

    def test_contains_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewProjectForm)

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_project_valid_post_data(self):
        User.objects.create_user(username='manager', email='manager@doe.com', password='123')
        six_months_advance = datetime.datetime.today() + relativedelta(months=+6)

        data = {
            'name': 'Project Test',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dicta porro illum voluptatum dolorum sit blanditiis voluptas quae sequi repudiandae culpa nostrum deserunt omnis repellat, quo, ab dolore officia optio rerum.',
            'manager': 2,
            'start_date': datetime.datetime.today().strftime('%d/%m/%Y'),
            'forecast_finish_date': six_months_advance.strftime('%d/%m/%Y'),
            'budget': float(Decimal(random.randrange(1,10000000))),
            'status': 1,
            'rating': random.randrange(1,4)
        }

        self.client.post(self.url, data)
        self.assertTrue(Project.objects.exists())

    def test_new_project_invalid_post_data(self):
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_project_invalid_post_data_empty_fields(self):
        data = {
            'name': '',
            'description': '',
            'manager': '',
            'start_date': '',
            'forecast_finish_date': '',
            'budget': '',
            'status': '',
            'rating': ''
        }

        response = self.client.post(self.url, data)
        form = response.context.get('form')
        
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

class LoginRequiredHomeTests(TestCase):

    def setUp(self):
        self.url = reverse('project:create')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))