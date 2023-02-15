from annoying.fields import AutoOneToOneField
from django.db import models

from byro.common.models import Configuration, LogEntry, LogTargetMixin

class GroupMembers(models.Model, LogTargetMixin):


    LOG_TARGET_BASE = "byro.byro_groups"


    member = models.ForeignKey(
         to='members.Member',
         on_delete=models.CASCADE,
         related_name="group_members",
    )
    group = models.ForeignKey(
         to='Group',
         on_delete=models.CASCADE,
         related_name="groups",
    )
                    
class Group(models.Model):
    name = models.CharField(max_length=100)

class SubGroups(models.Model):
    groupid = models.IntegerField(null=True)
    subgroupid = models.IntegerField(null=True)

    def add(groupid, subgroupid):
        if SubGroups.objects.filter(groupid = groupid, subgroupid = subgroupid).count() >= 1:
            raise ValueError('Subgroup already exists')
        else:
            obj = SubGroups.objects.create(groupid = groupid, subgroupid = subgroupid)
            return obj
     