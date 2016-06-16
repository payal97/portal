from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import timedelta
from cities_light.models import City, Country


from meetup.forms import AddMeetupForm, EditMeetupForm, AddMeetupLocationForm
from meetup.models import Meetup, MeetupLocation
from users.models import SystersUser


class MeetupFormTestCaseBase:
    def setUp(self):
        User.objects.create_user(username='foo', password='foobar')
        self.systers_user = SystersUser.objects.get()
        country = Country.objects.create(name='Bar', continent='AS')
        self.location = City.objects.create(name='Baz', display_name='Baz', country=country)
        self.meetup_location = MeetupLocation.objects.create(
            name="Foo Systers", slug="foo", location=self.location,
            description="It's a test meetup location", sponsors="BarBaz")

        self.meetup = Meetup.objects.create(title='Foo Bar Baz', slug='foobarbaz',
                                            date=timezone.now().date(),
                                            time=timezone.now().time(),
                                            description='This is test Meetup',
                                            meetup_location=self.meetup_location,
                                            created_by=self.systers_user,
                                            last_updated=timezone.now())


class AddMeetupFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_meetup_form(self):
        """Test add Meetup form"""
        invalid_data = {'title': 'abc', 'date': timezone.now().date()}
        form = AddMeetupForm(data=invalid_data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())

        date = (timezone.now() + timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertTrue(form.is_valid())
        form.save()
        new_meetup = Meetup.objects.get(slug='foo')
        self.assertTrue(new_meetup.title, 'Foo')
        self.assertTrue(new_meetup.created_by, self.systers_user)
        self.assertTrue(new_meetup.meetup_location, self.meetup_location)


class EditMeetupFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_edit_meetup_form(self):
        """Test edit meetup"""
        incomplete_data = {'slug': 'slug', 'date': timezone.now().date()}
        form = EditMeetupForm(data=incomplete_data)
        self.assertFalse(form.is_valid())

        date = (timezone.now() + timedelta(2)).date()
        time = timezone.now().time()

        data = {'slug': 'foobar', 'title': 'Foo Bar', 'date': date, 'time': time,
                'description': "It's a test meetup.", 'venue': 'test address'}
        form = EditMeetupForm(instance=self.meetup, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        meetup = Meetup.objects.get()
        self.assertEqual(meetup.title, 'Foo Bar')
        self.assertEqual(meetup.slug, 'foobar')
        self.assertEqual(meetup.created_by, self.systers_user)
        self.assertEqual(meetup.meetup_location, self.meetup_location)

'''
class AddMeetupLocationMemberFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        self.user2 = User.objects.create_user(username='baz', password='bazbar')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)

    def test_add_meetup_location_member_form(self):
'''

class AddMeetupLocationFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_meetup_location_form(self):
        """Test add Meetup Location form"""
        invalid_data = {'name': 'def', 'location': 'Baz, Bar, AS'}
        form = AddMeetupLocationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        data = {'name': 'Bar Systers', 'slug': 'bar', 'location': 'Baz, Bar',
                'description': 'test test test.', 'sponsors': 'BaaBaa'}
        form = AddMeetupLocationForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        new_meetup_location = MeetupLocation.objects.get(slug='bar')
        self.assertTrue(new_meetup_location.name, 'Bar Systers')

# class EditMeetupLocationFormTestCase(MeetupFormTestCaseBase, TestCase):
