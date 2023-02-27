from django.db import models

from byro.common.models import Configuration, LogEntry, LogTargetMixin


class GroupMemberRelation(models.Model, LogTargetMixin):
    LOG_TARGET_BASE = "byro_groups.group_member"

    member = models.ForeignKey(
        to="members.Member",
        on_delete=models.CASCADE,
        related_name="group_members",
    )
    group = models.ForeignKey(
        to="Group",
        on_delete=models.CASCADE,
        related_name="group",
    )


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)


class SubGroupRelation(models.Model):
    main_group = models.ForeignKey(
        to="Group",
        on_delete=models.CASCADE,
        related_name="main_group",
    )
    subgroup = models.ForeignKey(
        to="Group",
        on_delete=models.CASCADE,
        related_name="sub_group",
    )
