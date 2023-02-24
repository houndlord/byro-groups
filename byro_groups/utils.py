from .models import Group, GroupMemberRelation, SubGroupRelation
from . import signals


def remove_member(obj):
    signals.send_group_member_leave_signal(obj)
    obj.delete()
