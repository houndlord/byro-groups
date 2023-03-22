from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from byro.members.models import Member
from byro.office.views.members import MemberView

from .models import Group, GroupMemberRelation, SubGroupRelation
from . import signals
from .utils import check_if_relation_exists


class GroupForm(forms.Form):
    groups = forms.ChoiceField()

    def __init__(self, *args, member, **kwargs):
        super().__init__(*args, **kwargs)
        names = Group.objects.exclude(group__member=member).values_list(
            "name", flat=True
        )
        self.fields["groups"].choices = [(n, n) for n in names]


class GroupCreationForm(forms.Form):
    name = forms.CharField()

    def return_data(self):
        return self.cleaned_data["name"]


class GroupRenameForm(forms.Form):
    name = forms.CharField()

    def return_data(self):
        return self.cleaned_data["name"]


class SubgroupForm(forms.Form):
    groups = forms.ChoiceField()

    def __init__(self, *args, pk, **kwargs):
        super().__init__(*args, **kwargs)
        names = Group.objects.exclude(pk=pk).values_list("name", flat=True)
        self.fields["groups"].choices = [(n, n) for n in names]


class GroupMemberInsertionForm(forms.Form):
    member = forms.ChoiceField()

    def __init__(self, *args, pk, **kwargs):
        super().__init__(*args, **kwargs)
        names = Member.objects.exclude(pk=pk).values_list("name", flat=True)
        self.fields["member"].choices = [(n, n) for n in names]


class GroupNewMemberForm(forms.Form):
    name = forms.ChoiceField()

    def __init__(self, *args, group, **kwargs):
        super().__init__(*args, **kwargs)
        names = Member.objects.exclude(member__group == group).values_list(
            "name", flat=True
        )
        self.fields["name"].choices = [(n, n) for n in names]


class MemberGroups(MemberView, TemplateView):
    template_name = "byro_groups/member_groups.html"

    @property
    def object(self):
        return self.get_object()

    def get_object(self):
        return Member.all_objects.get(pk=self.kwargs["pk"])

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        member = self.get_object()
        ctx["lists"] = member.group_members.all()
        ctx["form"] = GroupForm(member=member)
        return ctx


class MemberAdd(MemberGroups):
    def post(self, request, pk):
        member = self.get_object()
        form = GroupForm(request.POST, member=member)
        if not form.is_valid():
            messages.error(request, _("Error."))
            return redirect(
                reverse(
                    "plugins:byro_groups:members.groups.groups",
                    kwargs={"pk": self.kwargs["pk"]},
                )
            )
        try:
            group = Group.objects.filter(name=form.data.get("groups")).first()
            obj = GroupMemberRelation.objects.create(member=member, group=group)
            member.log(self, ".add")
            signals.send_new_group_member_signal(obj)
            messages.success(request, _("Member added to the group."))
        except Exception as e:
            messages.error(
                request, _("Error adding the member to the group: ") + str(e)
            )
        return redirect(
            reverse(
                "plugins:byro_groups:members.groups.groups",
                kwargs={"pk": self.kwargs["pk"]},
            )
        )


class MemberRemove(MemberGroups):
    def get(self, request, pk, list_id):
        member = self.get_object()
        group = Group.objects.filter(pk=list_id).first()
        try:
            obj = GroupMemberRelation.objects.filter(group=group, member=member)
            signals.send_group_member_leave_signal(obj)
            obj.delete()
            member.log(self, ".remove")
            messages.success(request, _("Member removed from the group."))
            return redirect(
                reverse(
                    "plugins:byro_groups:members.groups.groups",
                    kwargs={"pk": self.kwargs["pk"]},
                )
            )
        except Exception as e:
            messages.error(request, _("Error removing the member: ") + str(e))


class GroupsView(TemplateView):
    template_name = "byro_groups/groups.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["lists"] = Group.objects.all()
        ctx["form"] = GroupCreationForm()
        ctx["renameform"] = GroupRenameForm()
        return ctx


class GroupMembersView(TemplateView):
    template_name = "byro_groups/group_members.html"

    @property
    def object(self):
        return self.get_object()

    def get_object(self):
        return Group.objects.filter(pk=self.kwargs.get("pk"))

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        pk = self.kwargs.get("pk")
        group = Group.objects.get(pk=pk)
        ctx["group_members"] = group.group.all()
        ctx["subgroupform"] = SubgroupForm(pk=pk)
        ctx["subgroups"] = group.main_group.all()
        ctx["group"] = group
        return ctx


class SubgroupAdd(GroupMembersView):
    def post(self, request, pk):
        form = SubgroupForm(request.POST, pk=pk)
        if not form.is_valid():
            messages.error(request, _("Error."))
            return redirect(
                reverse(
                    "plugins:byro_groups:groups.members.list",
                    kwargs={"pk": self.kwargs["pk"]},
                )
            )
        if (
            check_if_relation_exists(
                self.get_object()[0],
                Group.objects.filter(name=form.data.get("groups")).first(),
            )
            == False
        ):
            try:
                subgroup = Group.objects.filter(name=form.data.get("groups")).first()
                SubGroupRelation.objects.get_or_create(
                    main_group=self.get_object()[0], subgroup=subgroup
                )
                messages.success(request, _("Group added as subgroup succesfully"))
            except Exception as e:
                messages.error(
                    request, _("Error adding the group as subgroup: ") + str(e)
                )
        else:
            messages.error(request, "Creating cycles of subgroups is not allowed!")
        return redirect(
            reverse(
                "plugins:byro_groups:groups.members.list",
                kwargs={"pk": self.kwargs["pk"]},
            )
        )


class SubgroupRemove(GroupMembersView):
    def get(self, request, list_id, pk):
        try:
            group = Group.objects.get(pk=list_id)
            obj = SubGroupRelation.objects.filter(subgroup=group)
            obj.delete()
            messages.success(
                request, _("Group removed from lists of subgroups succesfully")
            )
        except Exception as e:
            messages.error(
                request, _("Error removing the group as subgroup: ") + str(e)
            )
        return redirect(
            reverse(
                "plugins:byro_groups:groups.members.list",
                kwargs={"pk": self.kwargs["pk"]},
            )
        )


class GroupMembersRemove(GroupMembersView):
    def get(self, request, list_id, pk):
        try:
            obj = GroupMemberRelation.objects.filter(member__pk=list_id, group__pk=pk)
            signals.send_group_member_leave_signal(obj)
            obj.delete()
            member = Member.all_objects.get(pk=list_id)
            member.log(self, ".remove")
            messages.success(request, _("Member removed from the group."))
        except Exception as e:
            messages.error(request, _("Error removing the member: ") + str(e))
        return redirect(
            reverse(
                "plugins:byro_groups:groups.members.list",
                kwargs={"pk": self.kwargs["pk"]},
            )
        )


class GroupAdd(GroupsView):
    def post(self, request):
        form = GroupCreationForm(request.POST)
        if not form.is_valid():
            messages.error(request, _("Error."))
            return redirect(reverse("plugins:byro_groups:groups.list"))
        try:
            group = Group.objects
            group.create(**form.cleaned_data)
            signals.send_new_group_signal(Group.objects.filter(**form.cleaned_data))
            messages.success(request, _("Group added succesfully"))
        except Exception as e:
            messages.error(request, _("Error creating the group: ") + str(e))
        return redirect(
            reverse(
                "plugins:byro_groups:groups.list",
            )
        )


class GroupRename(GroupsView):
    def post(self, request, list_id):
        form = GroupRenameForm(request.POST)
        if not form.is_valid():
            messages.error(request, _("Error."))
            return redirect(reverse("plugins:byro_groups:groups.list"))
        try:
            group = Group.objects.filter(pk=list_id)
            group.update(name=form.return_data())
            signals.send_group_rename_signal(group)
            messages.success(request, _("Group renamed succesfully"))
        except Exception as e:
            messages.error(request, _("Error renaming the group: ") + str(e))
        return redirect(
            reverse(
                "plugins:byro_groups:groups.list",
            )
        )


class GroupRemove(GroupsView):
    def get(self, request, list_id):
        try:
            group = Group.objects.filter(pk=list_id)
            signals.send_group_deletion_signal(group)
            group.delete()
            messages.success(request, _("Group deleted succesfully"))
        except Exception as e:
            messages.error(request, _("Error deleting the group: ") + str(e))
        return redirect(reverse("plugins:byro_groups:groups.list"))
