import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, TemplateView, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from braces.views import LoginRequiredMixin
from django.contrib.auth.models import User

from meetup.forms import AddMeetupForm, EditMeetupForm, AddMeetupLocationMemberForm, AddMeetupLocationOrganiserForm
from meetup.mixins import MeetupLocationMixin
from meetup.models import Meetup, MeetupLocation
from users.models import SystersUser


class MeetupLocationAboutView(MeetupLocationMixin, TemplateView):
    """Meetup Location about view, show about description of Meetup Location"""
    model = MeetupLocation
    template_name = "meetup/about.html"

    def get_meetup_location(self):
        return get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])


class MeetupLocationList(ListView):
    template_name = "meetup/list_location.html"
    model = MeetupLocation
    paginate_by = 20


class MeetupView(MeetupLocationMixin, DetailView):
    template_name = "meetup/meetup.html"
    model = MeetupLocation

    def get_context_data(self, **kwargs):
        context = super(MeetupView, self).get_context_data(**kwargs)
        context['meetup'] = get_object_or_404(Meetup, slug=self.kwargs['meetup_slug'],
                                              meetup_location=self.object)
        return context

    def get_meetup_location(self):
        return self.object


class MeetupLocationMembersView(MeetupLocationMixin, DetailView):
    """Meetup Location members view, show members list of Meetup Location"""
    model = MeetupLocation
    template_name = "meetup/members.html"
    paginate_by = 50

    def get_meetup_location(self):
        return get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])


class AddMeetupView(LoginRequiredMixin, MeetupLocationMixin, CreateView):
    """Add new meetup"""
    template_name = "meetup/add_meetup.html"
    model = Meetup
    form_class = AddMeetupForm
    raise_exception = True

    def get_success_url(self):
        """Supply the redirect URL in case of successful submit"""
        return reverse("view_meetup", kwargs={"slug": self.meetup_location.slug,
                                              "meetup_slug": self.object.slug})

    def get_form_kwargs(self):
        """Add request user and meetup location object to the form kwargs.
        Used to autofill form fields with created_by and meetup_location without
        explicitly filling them up in the form."""
        kwargs = super(AddMeetupView, self).get_form_kwargs()
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])
        kwargs.update({'created_by': self.request.user})
        kwargs.update({'meetup_location': self.meetup_location})
        return kwargs

    def get_meetup_location(self):
        return self.meetup_location
   

class DeleteMeetupView(LoginRequiredMixin, MeetupLocationMixin, DeleteView):
    """Delete existing Meetup"""
    template_name = "meetup/meetup_confirm_delete.html"
    model = Meetup
    slug_url_kwarg = "meetup_slug"
    raise_exception = True

    def get_success_url(self):
        """Supply the redirect URL in case of successful deletion"""
        self.get_meetup_location()
        return reverse("about_meetup_location",
                       kwargs={"slug": self.meetup_location.slug})

    def get_meetup_location(self):
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])
        return self.meetup_location


class EditMeetupView(LoginRequiredMixin, UpdateView):
    """Edit an existing meetup"""
    template_name = "meetup/edit_meetup.html"
    model = Meetup
    slug_url_kwarg = "meetup_slug"
    form_class = EditMeetupForm
    raise_exception = True

    def get_success_url(self):
        """Supply the redirect URL in case of successful submit"""
        return reverse("view_meetup", kwargs={"slug": self.object.meetup_location.slug,
                       "meetup_slug": self.object.slug})

    def get_context_data(self, **kwargs):
        """Add Meetup object to the context"""
        context = super(EditMeetupView, self).get_context_data(**kwargs)
        self.meetup = get_object_or_404(Meetup, slug=self.kwargs['meetup_slug'])
        context['meetup'] = self.meetup
        context['meetup_location'] = self.meetup.meetup_location
        return context


class UpcomingMeetupsView(MeetupLocationMixin, ListView):
    """List upcoming meetups of a meetup location"""
    template_name = "meetup/upcoming_meetups.html"
    model = Meetup
    paginate_by = 10

    def get_queryset(self, **kwargs):
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])
        meetup_list = Meetup.objects.filter(
            meetup_location=self.meetup_location,
            date__gte=datetime.date.today()).order_by('date', 'time')
        return meetup_list

    def get_meetup_location(self):
        return self.meetup_location


class PastMeetupListView(MeetupLocationMixin, ListView):
    """List past meetups of a meetup location"""
    template_name = "meetup/past_meetups.html"
    model = Meetup
    paginate_by = 10

    def get_queryset(self, **kwargs):
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])
        meetup_list = Meetup.objects.filter(
            meetup_location=self.meetup_location,
            date__lt=datetime.date.today()).order_by('date', 'time')
        return meetup_list

    def get_meetup_location(self):
        return self.meetup_location


class MeetupLocationSponsorsView(MeetupLocationMixin, DetailView):
    """View sponsors of a meetup location"""
    template_name = "meetup/sponsors.html"
    model = MeetupLocation

    def get_meetup_location(self):
        return get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])


class RemoveMeetupLocationMemberView(LoginRequiredMixin, MeetupLocationMixin, RedirectView):
    """Remove a member from a meetup location"""
    model = MeetupLocation
    permanent = False
    raise_exception = True

    def get_redirect_url(self, *args, **kwargs):
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug']) 
        user = get_object_or_404(User, username=kwargs.get('username'))
        systersuser = get_object_or_404(SystersUser, user=user)
        self.meetup_location.members.remove(systersuser)
        return reverse('members_meetup_location', kwargs={'slug': self.meetup_location.slug}) 

    def get_meetup_location(self):
        return self.meetup_location


class AddMeetupLocationMemberView(LoginRequiredMixin, MeetupLocationMixin, UpdateView):
    """Add new member to meetup location"""
    template_name = "meetup/add_member.html"
    model = MeetupLocation
    form_class = AddMeetupLocationMemberForm
    raise_exception = True

    def get_success_url(self):
        """Supply the redirect URL in case of successful addition"""
        self.get_meetup_location()
        return reverse('members_meetup_location', kwargs={'slug': self.meetup_location.slug})

    def get_meetup_location(self):
        self.meetup_location = get_object_or_404(MeetupLocation, slug=self.kwargs['slug'])
        return self.meetup_location
