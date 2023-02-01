from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from byro.members.signals import new_member
from byro.office.signals import member_view, nav_event

from .models import Group, GroupMembers


@receiver(member_view)
def groups_member_view(sender, signal, **kwargs):
    member = sender
    count = Group.objects.filter(groupp__member=member).count()
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