from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.utils import timezone
from cities_light.models import City, Country

from meetup.models import Meetup, MeetupLocation
from users.models import SystersUser


class MeetupLocationViewBaseTestCase(object):
    def setUp(self):
        self.user = User.objects.create_user(username='foo', password='foobar')
        self.systers_user = SystersUser.objects.get()
        country = Country.objects.create(name='Bar', continent='AS')
        self.location = City.objects.create(name='Baz', display_name='Baz', country=country)
        self.meetup_location = MeetupLocation.objects.create(
            name="Foo Systers", slug="foo", location=self.location,
            description="It's a test meetup location", sponsors="BarBaz")
        self.meetup_location.members.add(self.systers_user)
        self.meetup_location.organizers.add(self.systers_user)

        self.meetup = Meetup.objects.create(title='Foo Bar Baz', slug='foo-bar-baz',
                                            date=timezone.now().date(),
                                            time=timezone.now().time(),
                                            description='This is test Meetup',
                                            meetup_location=self.meetup_location,
                                            created_by=self.systers_user,
                                            last_updated=timezone.now())


class MeetupLocationAboutViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_view_meetup_location_about_view(self):
        """Test Meetup Location about view for correct http response"""
        url = reverse('about_meetup_location', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/about.html')
        self.assertEqual(response.context['meetup_location'], self.meetup_location)

        nonexistent_url = reverse('about_meetup_location', kwargs={'slug': 'bar'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)


class MeetupLocationListViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_view_meetup_location_list_view(self):
        """Test Meetup Location list view for correct http response and
        all meetup locations in a list"""
        url = reverse('list_meetup_location')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/list_location.html")
        self.assertContains(response, "Foo Systers")
        self.assertContains(response, "google.maps.Map")

        self.meetup_location2 = MeetupLocation.objects.create(
            name="Bar Systers", slug="bar", location=self.location,
            description="It's a test meetup location")
        url = reverse('list_meetup_location')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/list_location.html")
        self.assertContains(response, "Foo Systers")
        self.assertContains(response, "Bar Systers")
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertContains(response, "google.maps.Map")


class MeetupViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_view_meetup(self):
        """Test Meetup view for correct response"""
        url = reverse('view_meetup', kwargs={'slug': 'foo', 'meetup_slug': 'foo-bar-baz'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/meetup.html')
        self.assertEqual(response.context['meetup_location'], self.meetup_location)
        self.assertEqual(response.context['meetup'], self.meetup)

        nonexistent_url = reverse('view_meetup', kwargs={'slug': 'foo1',
                                  'meetup_slug': 'bazbar'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        self.meetup_location2 = MeetupLocation.objects.create(
            name="Bar Systers", slug="bar", location=self.location,
            description="It's a test meetup location")
        incorrect_pair_url = reverse('view_meetup', kwargs={'slug': 'bar',
                                     'meetup_slug': 'foo-bar-baz'})
        response = self.client.get(incorrect_pair_url)
        self.assertEqual(response.status_code, 404)


class MeetupLocationMembersViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_view_meetup_location_members_view(self):
        """Test Meetup Location members view for correct http response"""
        url = reverse('members_meetup_location', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/members.html')

        nonexistent_url = reverse('members_meetup_location', kwargs={'slug': 'bar'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)


class AddMeetupViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_get_add_meetup_view(self):
        """Test GET request to add a new meetup"""
        url = reverse('add_meetup', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.client.login(username='foo', password='foobar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/add_meetup.html')

    def test_post_add_meetup_view(self):
        """Test POST request to add a new meetup"""
        url = reverse("add_meetup", kwargs={'slug': 'foo'})
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        date = (timezone.now() + timezone.timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'BarTest', 'slug': 'bartest', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        new_meetup = Meetup.objects.get(slug='bartest')
        self.assertTrue(new_meetup.title, 'BarTest')
        self.assertTrue(new_meetup.created_by, self.systers_user)
        self.assertTrue(new_meetup.meetup_location, self.meetup_location)


class DeleteMeetupViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(DeleteMeetupViewTestCase, self).setUp()
        self.meetup2 = Meetup.objects.create(title='Fooba', slug='fooba',
                                             date=timezone.now().date(),
                                             time=timezone.now().time(),
                                             description='This is test Meetup',
                                             meetup_location=self.meetup_location,
                                             created_by=self.systers_user,
                                             last_updated=timezone.now())
        self.client = Client()

    def test_get_delete_meetup_view(self):
        """Test GET to confirm deletion of meetup"""
        url = reverse("delete_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'fooba'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm to delete")

    def test_post_delete_meetup_view(self):
        """Test POST to delete a meetup"""
        url = reverse("delete_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'fooba'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # One meetup deleted, another meetup left initialized in
        # MeetupLocationViewBaseTestCase
        self.assertSequenceEqual(Meetup.objects.all(), [self.meetup])


class EditMeetupView(MeetupLocationViewBaseTestCase, TestCase):
    def test_get_edit_meetup_view(self):
        """Test GET edit meetup"""
        wrong_url = reverse("edit_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'foo'})
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 403)

        url = reverse("edit_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'foo-bar-baz'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/edit_meetup.html')

    def test_post_edit_meetup_view(self):
        """Test POST edit meetup"""
        wrong_url = reverse("edit_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'foo'})
        response = self.client.post(wrong_url)
        self.assertEqual(response.status_code, 403)

        url = reverse("edit_meetup", kwargs={'slug': 'foo', 'meetup_slug': 'foo-bar-baz'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        date = (timezone.now() + timezone.timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'BarTes', 'slug': 'bartes', 'date': date, 'time': time,
                'description': "It's a edit test meetup."}
        self.client.login(username='foo', password='foobar')
        response = self.client.post(url, data=data)
        self.assertTrue(response.url.endswith('/meetup/foo/bartes/'))
        self.assertEqual(response.status_code, 302)


class UpcomingMeetupsViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(UpcomingMeetupsViewTestCase, self).setUp()
        self.meetup2 = Meetup.objects.create(title='Bar Baz', slug='bazbar',
                                             date=(timezone.now() + timezone.timedelta(2)).date(),
                                             time=timezone.now().time(),
                                             description='This is new test Meetup',
                                             meetup_location=self.meetup_location,
                                             created_by=self.systers_user,
                                             last_updated=timezone.now())

    def test_view_upcoming_meetup_list_view(self):
        """Test Upcoming Meetup list view for correct http response and
        all upcoming meetups in a list"""
        url = reverse('upcoming_meetups', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/upcoming_meetups.html")
        self.assertContains(response, "Foo Bar Baz")
        self.assertContains(response, "Bar Baz")
        self.assertEqual(len(response.context['meetup_list']), 2)


class PastMeetupListViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(PastMeetupListViewTestCase, self).setUp()
        self.meetup2 = Meetup.objects.create(title='Bar Baz', slug='bazbar',
                                             date=(timezone.now() + timezone.timedelta(2)).date(),
                                             time=timezone.now().time(),
                                             description='This is new test Meetup',
                                             meetup_location=self.meetup_location,
                                             created_by=self.systers_user,
                                             last_updated=timezone.now())
        self.meetup3 = Meetup.objects.create(title='Foo Baz', slug='foobar',
                                             date=(timezone.now() - timezone.timedelta(2)).date(),
                                             time=timezone.now().time(),
                                             description='This is new test Meetup',
                                             meetup_location=self.meetup_location,
                                             created_by=self.systers_user,
                                             last_updated=timezone.now())

    def test_view_past_meetup_list_view(self):
        """Test Past Meetup list view for correct http response and
        all past meetups in a list"""
        url = reverse('past_meetups', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/past_meetups.html")
        self.assertEqual(len(response.context['meetup_list']), 1)


class MeetupLocationSponsorsViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_view_meetup_location_sponsors_view(self):
        """Test Meetup Location sponsors view for correct http response"""
        url = reverse('sponsors_meetup_location', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/sponsors.html")
        self.assertEqual(response.context['meetup_location'], self.meetup_location)

        nonexistent_url = reverse('sponsors_meetup_location', kwargs={'slug': 'bar'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)


class RemoveMeetupLocationMemberViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(RemoveMeetupLocationMemberViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.members.add(self.systers_user2)
        self.meetup_location.organizers.add(self.systers_user2)
        self.user3 = User.objects.create_user(username='bar', password='barbar')
        self.systers_user3 = SystersUser.objects.get(user=self.user3)
        self.meetup_location.members.add(self.systers_user3)

    def test_view_remove_meetup_location_member_view(self):
        """
        Test remove Meetup Location member view for 3 cases:

        * removing only a member
        * removing one of two members who are organizers
        * removing member who is the only organizer
        """
        url = reverse("remove_member_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'bar'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse("remove_member_meetup_location",
                                  kwargs={'slug': 'foo', 'username': 'barbaz'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse("remove_member_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'bar'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 2)

        url = reverse("remove_member_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 1)
        self.assertEqual(len(self.meetup_location.organizers.all()), 1)

        url = reverse("remove_member_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 1)
        self.assertEqual(len(self.meetup_location.organizers.all()), 1)


class AddMeetupLocationMemberViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(AddMeetupLocationMemberViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)

    def test_get_add_meetup_location_member_view(self):
        url = reverse("add_member_meetup_location", kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/add_member.html')

    def test_post_add_meetup_location_member_view(self):
        url = reverse("add_member_meetup_location", kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        username = self.user2.get_username()
        data = {'username': username}
        self.client.login(username='foo', password='foobar')
        response = self.client.post(url, data=data)
        self.assertTrue(response.url.endswith('/meetup/foo/members/'))
        self.assertEqual(response.status_code, 302)


class RemoveMeetupLocationOrganizerViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(RemoveMeetupLocationOrganizerViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.members.add(self.systers_user2)
        self.meetup_location.organizers.add(self.systers_user2)

    def test_view_remove_meetup_location_organizer_view(self):
        """
        Test remove Meetup Location organizer view for 2 cases:

        * remove one of two organizers
        * remove the only organizer
        """
        url = reverse("remove_organizer_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse("remove_organizer_meetup_location",
                                  kwargs={'slug': 'foo', 'username': 'barbaz'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse("remove_organizer_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 2)
        self.assertEqual(len(self.meetup_location.organizers.all()), 1)

        url = reverse("remove_organizer_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 2)
        self.assertEqual(len(self.meetup_location.organizers.all()), 1)


class MakeMeetupLocationOrganizerViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(MakeMeetupLocationOrganizerViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.members.add(self.systers_user2)

    def test_view_make_meetup_location_organizer_view(self):
        """Test make Meetup Location organizer view for correct http response"""
        url = reverse("make_organizer_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse("make_organizer_meetup_location",
                                  kwargs={'slug': 'foo', 'username': 'barbaz'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse("make_organizer_meetup_location",
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/members/')
        self.assertEqual(len(self.meetup_location.members.all()), 2)
        self.assertEqual(len(self.meetup_location.organizers.all()), 2)


class JoinMeetupLocationViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(JoinMeetupLocationViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.join_requests.add(self.systers_user2)
        self.user3 = User.objects.create_user(username='bar', password='barbar')
        self.systers_user3 = SystersUser.objects.get(user=self.user3)

    def test_view_join_meetup_location_view(self):
        """
        Test join meetup location view for three cases:

        * User who is joining meetup location
        * User who has already requested to join
        * User who is already a member
        """
        url = reverse('join_meetup_location', kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        wrong_url = reverse('join_meetup_location', kwargs={'slug': 'foo', 'username': 'foba'})
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

        url = reverse('join_meetup_location', kwargs={'slug': 'foo', 'username': 'bar'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/about/')
        self.assertEqual(len(self.meetup_location.join_requests.all()), 2)
        for message in response.context['messages']:
            self.assertEqual(message.tags, "success")
            self.assertTrue(
                'Your request to join meetup location Foo Systers has been sent.'
                in message.message)

        url = reverse('join_meetup_location', kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/about/')
        self.assertEqual(len(self.meetup_location.join_requests.all()), 2)
        for message in response.context['messages']:
            self.assertEqual(message.tags, "warning")
            self.assertTrue(
                'You have already requested to join meetup location Foo Systers.'
                in message.message)

        url = reverse('join_meetup_location', kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/about/')
        self.assertEqual(len(self.meetup_location.join_requests.all()), 2)
        for message in response.context['messages']:
            self.assertEqual(message.tags, "warning")
            self.assertTrue(
                'You are already a member of meetup location Foo Systers.'
                in message.message)


class MeetupLocationJoinRequestsViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(MeetupLocationJoinRequestsViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.join_requests.add(self.systers_user2)

    def test_view_meetup_location_join_requests_view(self):
        """Test meetup location join requests view for correct http response"""
        url = reverse('join_requests_meetup_location', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse('join_requests_meetup_location', kwargs={'slug': 'bar'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse('join_requests_meetup_location', kwargs={'slug': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meetup/join_requests.html")
        self.assertEqual(len(response.context['requests']), 1)


class ApproveMeetupLocationJoinRequestsViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(ApproveMeetupLocationJoinRequestsViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.join_requests.add(self.systers_user2)

    def test_view_approve_meetup_location_join_requests_view(self):
        """Test approve meetup location join requests view for correct http response"""
        url = reverse('approve_join_request_meetup_location',
                      kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse('approve_join_request_meetup_location',
                                  kwargs={'slug': 'foo', 'username': 'foba'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse('approve_join_request_meetup_location',
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/join_requests/')
        self.assertEqual(len(self.meetup_location.join_requests.all()), 0)
        self.assertEqual(len(self.meetup_location.members.all()), 2)


class RejectMeetupLocationJoinRequestsViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def setUp(self):
        super(RejectMeetupLocationJoinRequestsViewTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.join_requests.add(self.systers_user2)

    def test_view_reject_meetup_location_join_requests_view(self):
        """Test reject meetup location join requests view for correct http response"""
        url = reverse('reject_join_request_meetup_location',
                      kwargs={'slug': 'foo', 'username': 'foo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        nonexistent_url = reverse('reject_join_request_meetup_location',
                                  kwargs={'slug': 'foo', 'username': 'foba'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

        url = reverse('reject_join_request_meetup_location',
                      kwargs={'slug': 'foo', 'username': 'baz'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, 'meetup/foo/join_requests/')
        self.assertEqual(len(self.meetup_location.join_requests.all()), 0)
        self.assertEqual(len(self.meetup_location.members.all()), 1)


class AddMeetupLocationViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
    def test_get_add_meetup_location_view(self):
        """Test GET request to add a new meetup location"""
        url = reverse('add_meetup_location')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetup/add_meetup_location.html')

    def test_post_add_meetup_location_view(self):
        """Test POST request to add a new meetup location"""
        url = reverse('add_meetup_location')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='foo', password='foobar')
        url = reverse('add_meetup_location')
        data = {'name': 'Bar Systers', 'slug': 'bar', 'location': self.location,
                'description': "It's a new meetup location", 'sponsors': 'BarBaz'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        new_meetup_location = MeetupLocation.objects.get(slug='bar')
        self.assertTrue(new_meetup_location.name, 'Bar Systers')


# class EditMeetupLocationViewTestCase(MeetupLocationViewBaseTestCase, TestCase):

# class DeleteMeetupLocationViewTestCase(MeetupLocationViewBaseTestCase, TestCase):
