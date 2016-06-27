from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from cities_light.models import City
from ckeditor.fields import RichTextField


from users.models import SystersUser


class MeetupLocation(models.Model):
    """Manage details of Meetup Location groups"""
    name = models.CharField(max_length=255, unique=True, verbose_name="Name")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    location = models.ForeignKey(City, verbose_name="Location")
    description = RichTextField(verbose_name="Description")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email")
    organizers = models.ManyToManyField(SystersUser,
                                        related_name="Organizers",
                                        verbose_name="Organizers")
    members = models.ManyToManyField(SystersUser, blank=True,
                                     related_name="Members",
                                     verbose_name="Members")
    sponsors = RichTextField(verbose_name="Sponsors", blank=True)
    join_requests = models.ManyToManyField(SystersUser,
                                           related_name="Join Requests",
                                           verbose_name="Join Requests",
                                           blank=True)

    class Meta:
        permissions = (
            ('add_meetup_location_member', 'Add meetup location member'),
            ('delete_meetup_location_member', 'Delete meetup location member'),
            ('add_meetup_location_organizer', 'Add meetup location organizer'),
            ('delete_meetup_location_organizer', 'Delete meetup location organizer'),
	        ('approve_meetup_location_joinrequest', 'Approve meetup location join request'),
            ('delete_meetup_location_joinrequest', 'Delete meetup location join request'),
        ) 

    def __str__(self):
        return self.name


class Meetup(models.Model):
    """Manage details of Meetups of MeetupLocations"""
    title = models.CharField(max_length=50, verbose_name="Title",)
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    date = models.DateField(verbose_name="Date")
    time = models.TimeField(verbose_name="Time", blank=True)
    venue = models.TextField(verbose_name="Venue", blank=True)
    description = RichTextField(verbose_name="Description")
    meetup_location = models.ForeignKey(MeetupLocation, verbose_name="Meetup Location")
    created_by = models.ForeignKey(SystersUser, null=True, verbose_name="Created By")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Update")

    def __str__(self):
        return self.title

    def clean_fields(self, *args, **kwargs):
        """Validate meetup date is not less than today's date and meetup time is not a time
        that has already passed."""
        if self.date < timezone.now().date():
            raise ValidationError("Date should not be less than today's date.")
        if self.time:
            if self.date == timezone.now().date() and self.time < timezone.now().time():
                raise ValidationError("Time should not be a time that has already passed.")


class Rsvp(models.Model):
    """ Users RSVP for particular meetup """
    user = models.ForeignKey(SystersUser, verbose_name="User")
    meetup = models.ForeignKey(Meetup, verbose_name="Meetup")
    coming = models.BooleanField(default=True)
    plus_one = models.BooleanField(default=False)

    def __str__(self):
        return "{0} RSVP for meetup {1}".format(self.user, self.meetup)
