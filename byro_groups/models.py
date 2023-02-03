from annoying.fields import AutoOneToOneField
from django.db import models

class GroupMembers(models.Model):
    member = models.ForeignKey(
         to='members.Member',
         on_delete=models.CASCADE,
         related_name="groups",
    )
    group = models.ForeignKey(
         to='Group',
         on_delete=models.CASCADE,
         related_name="groupp",
    )

class Group(models.Model):
    name = models.CharField(max_length=100)

class SubGroups(models.Model):
    group_id = Group.id
    subgroup_id = Group.id


def delg(pk):
    obj = Group.objects.filter(pk=pk)
    obj.delete()