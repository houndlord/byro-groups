from .models import Group, GroupMemberRelation, SubGroupRelation
from . import signals


def remove_member(obj):
    signals.send_group_member_leave_signal(obj)
    obj.delete()


def get_group_members_by_id(id):
    """
    Takes group id as input parameter.
    Returns QuerySet of GroupMemberRelation objects, which consists of all Member objects for a given group.
    """
    group = Group.objects.get(pk=id)
    user_members = group.group.all()
    subgroups = group.main_group.all()
    for subgroup in subgroups:
        user_members = user_members & subgroup.subgroup.group.all()
    return user_members
