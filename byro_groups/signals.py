from django.dispatch import receiver
import django.dispatch
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from byro.members.signals import new_member
from byro.office.signals import member_view, nav_event

from .models import Group, GroupMemberRelation


@receiver(member_view)
def groups_member_view(sender, signal, **kwargs):
    member = sender
    count = Group.objects.filter(group__member=member).count()
    return {
        "label": _("Groups ({count})").format(count=count),
        "url": reverse(
            "plugins:byro_groups:members.groups.groups", kwargs={"pk": member.pk}
        ),
        "url_name": "plugins:byro_groups:members.groups.groups",
    }


@receiver(nav_event)
def groups_sidebar(sender, **kwargs):
    request = sender
    if hasattr(request, "user") and not request.user.is_anonymous:
        return {
            "icon": "users",
            "label": _("Groups"),
            "url": reverse("plugins:byro_groups:groups.list"),
            "active": "byro_groups" in request.resolver_match.namespace
            and "member" not in request.resolver_match.url_name,
        }


new_group = django.dispatch.Signal()

group_deletion = django.dispatch.Signal()

new_group_member = django.dispatch.Signal()

group_member_leave = django.dispatch.Signal()

group_rename = django.dispatch.Signal()


def send_new_group_signal(sender):
    new_group.send_robust(sender=sender)


def send_new_group_member_signal(sender):
    new_group_member.send_robust(sender=sender)


def send_group_deletion_signal(sender):
    group_deletion.send_robust(sender)


def send_group_member_leave_signal(sender):
    group_member_leave.send_robust(sender=sender)


def send_group_rename_signal(sender):
    group_rename.send_robust(sender=sender)
