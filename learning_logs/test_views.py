from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.conf import settings

from .models import Topic, Entry


class TopicListTests(TestCase):
    def setUp(self):
        """Setup for every test."""
        self.url = reverse("learning_logs:topics")
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="test@email.com", password="test"
        )
        Topic.objects.create(user=self.user, text="Test1", public=True)
        Topic.objects.create(user=self.user, text="Test2", public=True)
        Topic.objects.create(user=self.user, text="Test3", public=True)
        Topic.objects.create(user=self.user, text="Test4", public=False)

    def test_topic_list_view_unauthenticated(self):
        """Test topics response context for unauthenticated user."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["topics"]), 3)

    def test_topic_list_view_authenticated(self):
        """Test topics response context for authenticated user."""
        self.assertTrue(self.client.login(username="test", password="test"))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["topics"]), 4)


class TopicRetrieveTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="test@email.com", password="test"
        )
        topic1 = Topic.objects.create(user=self.user, text="Test1", public=True)
        topic2 = Topic.objects.create(user=self.user, text="Test2", public=True)
        topic3 = Topic.objects.create(user=self.user, text="Test3", public=False)

        Entry.objects.create(topic=topic1, text="Test entry 1")
        Entry.objects.create(topic=topic1, text="Test entry 2")
        Entry.objects.create(topic=topic1, text="Test entry 3")

        self.test_entries_topic = topic1
        self.first_private = Topic.objects.filter(public=False).first()

    def test_read_public_existing_topic_unauthenticated(self):
        url = reverse("learning_logs:topic", kwargs={"topic_id": self.test_entries_topic.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_public_nonexisting_topic_unauthenticated(self):
        url = reverse("learning_logs:topic", kwargs={"topic_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_read_private_existing_topic_unauthenticated(self):
        test_topic = Topic.objects.filter(public=False).first()
        url = reverse("learning_logs:topic", kwargs={"topic_id": test_topic.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_read_private_existing_topic_authenticated(self):
        self.assertTrue(self.client.login(username="test", password="test"))
        url = reverse("learning_logs:topic", kwargs={"topic_id": self.first_private.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_public_nonexisting_topic_authenticated(self):
        self.assertTrue(self.client.login(username="test", password="test"))
        url = reverse("learning_logs:topic", kwargs={"topic_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_topic_entries_all_are_shown(self):
        url = reverse(
            "learning_logs:topic", kwargs={"topic_id": self.test_entries_topic.id}
        )
        response = self.client.get(url)
        self.assertEqual(len(response.context["entries"]), 3)


class TopicCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="test@email.com", password="test"
        )

        self.url = reverse("learning_logs:new_topic")

    def test_create_topic_authenticated(self):
        self.assertTrue(self.client.login(username="test", password="test"))
        response = self.client.post(
            self.url,
            {"user": self.user.pk, "text": "Create topic via API", "public": True},
        )
        # Successful redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Topic.objects.count(), 1)

    def test_create_topic_unauthenticated(self):
        response = self.client.post(
            self.url,
            {"user": self.user.pk, "text": "Create topic via API", "public": True},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.headers["location"])
        self.assertEqual(Topic.objects.count(), 0)


class EntryCreateTests(TestCase):
    """
    Test entry create with:
    - authentication
    - topic existence
    - user is owner
    - valid data
    """

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(
            username="test", email="test@email.com", password="test"
        )
        user2 = User.objects.create_user(
            username="test2", email="test2@email.com", password="test2"
        )
        self.user = user
        self.user2 = user2
        topic1 = Topic.objects.create(user=self.user, text="Test1", public=True)
        topic2 = Topic.objects.create(user=self.user2, text="Test2", public=True)

        self.url_name = "learning_logs:new_entry"
        self.test_topic = topic1
        self.other_topic = topic2
        self.last_topic = Topic.objects.last()

    def test_positive(self):
        """User is authenticated and owner. Entry is valid. Topic for entry exists."""
        self._login()
        url = self._reverse_topic(self.test_topic.id)
        response = self.client.post(
            url,
            {"text": "Create topic via API"},
        )
        self.assertIn(reverse("learning_logs:topics"), response.headers["location"])
        self.assertEqual(response.status_code, 302)

    def test_create_entry_unauthenticated(self):
        url = self._reverse_topic(self.last_topic.id)
        response = self.client.post(
            url,
            {"text": "Create topic via API"},
        )
        self.assertIn(settings.LOGIN_URL, response.headers["location"])
        self.assertEqual(response.status_code, 302)

    def test_create_entry_for_unexisting_topic_authenticated(self):
        self._login()
        url = self._reverse_topic(self.last_topic.id + 1)
        response = self.client.post(
            url,
            {"text": "Create topic via API"},
        )
        self.assertEqual(response.status_code, 404)

    def test_create_entry_for_other_user_topic_authenticated(self):
        self._login()
        url = self._reverse_topic(self.other_topic.id)
        response = self.client.post(
            url,
            {"text": "Create topic via API"},
        )
        self.assertEqual(response.status_code, 404)

    def _reverse_topic(self, topic_id):
        url = reverse(self.url_name, kwargs={"topic_id": topic_id})
        return url

    def _login(self):
        self.assertTrue(self.client.login(username="test", password="test"))


class EntryEditTests(TestCase):
    """
    Test:
    - authenticated
    - exists (valid)
    - owner
    """

    #
    # Setup general attributes
    #
    def setUp(self):
        user = User.objects.create_user(
            username="test", email="test@email.com", password="test"
        )
        user2 = User.objects.create_user(
            username="test2", email="test2@email.com", password="test2"
        )
        topic1 = Topic.objects.create(user=user, text="Test1", public=True)
        topic2 = Topic.objects.create(user=user2, text="Test2", public=True)
        entry1 = Entry.objects.create(topic=topic1, text="Test entry 1")
        entry2 = Entry.objects.create(topic=topic2, text="Test entry 2")

        # Interface for tests
        self.client = Client()
        self.entry_mine_pk = entry1.pk
        self.entry_other = entry2

    @property
    def entry_mine(self):
        return Entry.objects.get(pk=self.entry_mine_pk)

    @property
    def entry_last(self):
        return Entry.objects.last()

    #
    # Setup general methods
    #
    def _reverse_edit_entry(self, entry_id):
        return reverse("learning_logs:edit_entry", kwargs={"entry_id": entry_id})

    def _login(self):
        self.assertTrue(self.client.login(username="test", password="test"))

    def _assert_login_response(self, response):
        self.assertIn(settings.LOGIN_URL, response.headers["location"])
        self.assertEqual(response.status_code, 302)

    #
    # Test positive behavior
    #
    def test(self):
        self._login()
        url = self._reverse_edit_entry(self.entry_mine.id)
        response = self.client.post(url, {"text": "New entry text"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("New entry text", self.entry_mine.text)

    #
    # Test negative behavior
    #
    def test_unauthenticated(self):
        url = self._reverse_edit_entry(self.entry_mine.id)
        response = self.client.post(url, {"text": "New entry text"})
        self._assert_login_response(response)

    def test_nonexistent_entry(self):
        self._login()
        url = self._reverse_edit_entry(self.entry_last.id + 1)
        response = self.client.post(url, {"text": "New entry text"})
        self.assertEqual(response.status_code, 404)

    def test_owner(self):
        self._login()
        url = self._reverse_edit_entry(self.entry_other.id)
        response = self.client.post(url, {"text": "New entry text"})
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("New entry text", self.entry_other.text)
