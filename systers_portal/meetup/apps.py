from django.apps import AppConfig
from django.db.models.signals import post_migrate
from meetup.signals import handlers

class MeetupConfig(AppConfig):
    name = 'meetup'
    verbose_name = 'Meetup'

    def ready(self):
        post_migrate.connect(handlers.create_notice_types, sender=self)
