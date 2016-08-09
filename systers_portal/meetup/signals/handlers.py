from pinax.notifications.models import NoticeType

def create_notice_types(sender, **kwargs):
    print('Creating notices for meetup')
    NoticeType.create("new_join_request", ("New Join Request"),
                      ("a user has requested to join the meetup location"))
    NoticeType.create("joined_meetup_location", ("Joined Meetup Location"),
                      ("you have joined a meetup location"))
    NoticeType.create("made_organizer", ("Made Organizer"),
                      ("you have been made an organizer of a meetup location"))
    NoticeType.create("new_meetup", ("New Meetup"),
                      ("a new meetup has been added"))
    NoticeType.create("new_support_request", ("New Support Request"),
                      ("a user has added a support request"))
    NoticeType.create("support_request_approved", ("Support Request Approved"),
                      ("your support request has been approved"))
    NoticeType.create("support_request_comment", ("Comment on Support Request"),
                      ("a user has commented on the support request"))
