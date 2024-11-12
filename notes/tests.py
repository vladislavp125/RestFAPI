import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Note

User = get_user_model()


class NoteTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.note_user = Note.objects.create(title="test", description="test description", user=self.user)
        self.admin_user = get_user_model().objects.create_superuser(username="admintest", password="admintest")
        self.note_admin = Note.objects.create(title="test_admin", description="test description_admin", user=self.admin_user)

    def test_get_note_as_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse('note-list'))

        self.assertEqual(response.status_code, 200)

    def test_post_note_as_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post('/api/notes/', data={"title": "test1", "description": "test description"})

        self.assertEqual(response.status_code, 201)

        new_note = Note.objects.get(title="test1")

        self.assertEqual(new_note.title, "test1")
        self.assertEqual(new_note.description, "test description")
        self.assertEqual(new_note.user, self.user)

    def test_put_note_as_user(self):
        self.client.login(username="testuser", password="testpassword")
        self.assertEqual(self.note_user.user, self.user)
        response = self.client.put(reverse('note-detail', args=[self.note_user.pk]),
                                   data=json.dumps({
                                       "title": "New title",
                                       "description": "New description"
                                   }),
                                   content_type="application/json")

        update_note_user = Note.objects.get(pk=self.note_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(update_note_user.title, "New title")
        self.assertEqual(update_note_user.description, "New description")

    def test_delete_note_as_user(self):
        self.client.login(username="testuser", password="testpassword")
        new_note_user = Note.objects.create(title="test1", description="test description1", user=self.user)
        response = self.client.delete(reverse('note-detail', args=[new_note_user.pk]))

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=new_note_user.pk)

    def test_get_note_as_admin(self):
        self.client.login(username="admintest", password="admintest")
        response = self.client.get(reverse('note-list'))

        self.assertEqual(response.status_code, 200)

    def test_create_note_as_admin(self):
        self.client.login(username="admintest", password="admintest")
        response = self.client.post("/api/notes/",
                                    data={"title": "test_admin", "description": "test description_admin"})
        created_note = Note.objects.get(title="test_admin")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(created_note.description, "test description_admin")
        self.assertEqual(created_note.user, self.admin_user)

    def test_put_note_as_admin(self):
        self.client.login(username="admintest", password="admintest")
        response = self.client.put(reverse('note-detail', args=[self.note_admin.pk]),
                                   data=json.dumps({
                                       "title": "new title",
                                       "description": "New description"
                                   }),
                                   content_type="application/json")
        update_note_admin = Note.objects.get(pk=self.note_admin.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(update_note_admin.title, "new title")
        self.assertEqual(update_note_admin.description, "New description")

    def test_delete_note_as_admin(self):
        self.client.login(username="admintest", password="admintest")
        response = self.client.delete(reverse('note-detail', args=[self.note_admin.pk]))

        self.assertEqual(response.status_code, 204)

        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=self.note_admin.pk)
