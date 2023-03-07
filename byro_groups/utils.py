from .models import Group, GroupMemberRelation, SubGroupRelation
from . import signals
from collections.abc import Iterable


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
        user_members = user_members | subgroup.subgroup.group.all()
    return user_members

def check_if_relation_exists(maingroup, subgroup):
    relations = subgroup.main_group.all()
    for relation in relations:
        while relation:
            if isinstance(relation, Iterable):
                for elem in relation:
                    if elem.subgroup == maingroup:
                        return True
                    relation = relation.subgroup.main_group.all()
            else:
                if relation.subgroup == maingroup:
                    return True
                relation = relation.subgroup.main_group.all()
    return False
