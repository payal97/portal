from django.conf.urls import url

from meetup.views import (MeetupLocationAboutView, MeetupLocationList, MeetupView,
                          MeetupLocationMembersView, AddMeetupView, DeleteMeetupView,
                          EditMeetupView, UpcomingMeetupsView, PastMeetupListView,
                          MeetupLocationSponsorsView, RemoveMeetupLocationMemberView,
                          AddMeetupLocationMemberView, RemoveMeetupLocationOrganizerView,
                          MakeMeetupLocationOrganizerView)

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/about/$', MeetupLocationAboutView.as_view(),
        name='about_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/upcoming/$', UpcomingMeetupsView.as_view(),
        name='upcoming_meetups'),
    url(r'^(?P<slug>[\w-]+)/past/$', PastMeetupListView.as_view(),
        name='past_meetups'),
    url(r'^(?P<slug>[\w-]+)/members/$', MeetupLocationMembersView.as_view(),
        name='members_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/add/$', AddMeetupView.as_view(), name='add_meetup'),
    url(r'^(?P<slug>[\w-]+)/(?P<meetup_slug>[\w-]+)/delete/$', DeleteMeetupView.as_view(),
        name='delete_meetup'),
    url(r'^(?P<slug>[\w-]+)/(?P<meetup_slug>[\w-]+)/edit/$', EditMeetupView.as_view(),
        name="edit_meetup"),
    url(r'locations/$', MeetupLocationList.as_view(), name='list_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/sponsors/$', MeetupLocationSponsorsView.as_view(),
        name='sponsors_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/remove/(?P<username>[\w.@+-]+)/$',
        RemoveMeetupLocationMemberView.as_view(),
        name='remove_member_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/add_member/$', AddMeetupLocationMemberView.as_view(),
        name='add_member_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/remove_organizer/(?P<username>[\w.@+-]+)/$',
        RemoveMeetupLocationOrganizerView.as_view(),
        name='remove_organizer_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/make_organizer/(?P<username>[\w.@+-]+)/$',
        MakeMeetupLocationOrganizerView.as_view(),
        name='make_organizer_meetup_location'),
    url(r'^(?P<slug>[\w-]+)/(?P<meetup_slug>[\w-]+)/$', MeetupView.as_view(), name="view_meetup"),
]
