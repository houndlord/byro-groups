from .models import Group, GroupMemberRelation, SubGroupRelation
from . import signals
from collections.abc import Iterable


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


def append_relations(src, dst):
    """Helper function."""
    for elem in src:
        dst.append(elem)


def check_if_relation_exists(maingroup, subgroup):
    """
    Checks SubGroupRelation for possible cycles. If insertion (maingroup, subgroup) relation to table
    will create cycle returns True.
    """
    relations = []
    q = subgroup.main_group.all()
    append_relations(q, relations)
    for relation in relations:
        if isinstance(relation, Iterable):
            for elem in relation:
                if elem.subgroup == maingroup:
                    return True
                append_relations(elem.subgroup.main_group.all(), relations)
        else:
            if relation.subgroup == maingroup:
                return True
            append_relations(relation.subgroup.main_group.all(), relations)
    return False
