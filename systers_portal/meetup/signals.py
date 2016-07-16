from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from meetup.models import MeetupLocation
from meetup.constants import MEMBER, ORGANIZER
from meetup.utils import (create_groups, assign_permissions, remove_groups)
from users.models import SystersUser


@receiver(post_save, sender='meetup.MeetupLocation',
          dispatch_uid="manage_groups")
def manage_meetup_location_groups(sender, instance, created, **kwargs):
    """Manage user groups and user permissions for a particular MeetupLocation"""
    name = instance.name
    print("'name' assigned as", instance.name)
    if created:
        print("since 'created' was true")
        groups = create_groups(name)
        print("the following groups were created:", groups)
        assign_permissions(instance, groups)
        print("permissions were assigned")
        instance.save()
        print("and the instance was saved")


@receiver(post_delete, sender='meetup.MeetupLocation',
          dispatch_uid="remove_groups")
def remove_meetup_location_groups(sender, instance, **kwargs):
    """Remove user groups for a particular Meetup Location"""
    print("yayayayayayyayyayayayayyayayayayyaayayya")
    remove_groups(instance.name)


@receiver(m2m_changed, sender=MeetupLocation.members.through,
          dispatch_uid="add_members")
def add_meetup_location_members(sender, **kwargs):
    """Add permissions to a user when she is added as a Meetup Location member"""
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', None)
    if action == "pre_add":
        systersuser = SystersUser.objects.get(pk=list(pk_set)[0])
        members_group = get_object_or_404(Group, name=MEMBER.format(instance.name))
        if not systersuser.is_group_member(members_group.name):
            systersuser.join_group(members_group)
