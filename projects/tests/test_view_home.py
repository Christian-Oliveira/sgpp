from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User

from ..models import Project
from ..views import ProjectListView

class HomeTests(TestCase):
    
    def setUp(self):
        User.objects.create_user(username='test', email='teste@doe.com', password='123')
        self.client.login(username='test', password='123')        

    def test_home_view_status_code(self):
        url = reverse('project:index')
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)


class LoginRequiredHomeTests(TestCase):

    def setUp(self):
        self.url = reverse('home')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))