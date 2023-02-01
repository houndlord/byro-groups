from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from byro.members.models import Member
from byro.office.views.members import MemberView

from .models import Group, GroupMembers


class GroupForm(forms.Form):
    groups = forms.ChoiceField()

    def __init__(self, *args, member, **kwargs):
        super().__init__(*args, **kwargs)
        names = Group.objects.exclude(groupp__member=member).values_list(
            "name", flat=True
        )
        self.fields["groups"].choices = [(n, n) for n in names]

class GroupCreationForm(forms.Form):
    name = forms.CharField()

    def return_data(self):
        return self.cleaned_data['name']

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
        ctx["lists"] = member.groups.all()
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
            #group = Group
            #group.add_member(self.get_object())
            GroupMembers.objects.get_or_create(member=self.get_object(), group=Group.objects.filter(name=form.data.get('groups')).first())
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
        group = Group.objects.filter(pk=list_id).first()
        try:
            GroupMembers.objects.filter(group=group).delete()
            messages.success(request, _("Member removed from the group."))
            return redirect(
            reverse(
                "plugins:byro_groups:members.groups.groups",
                kwargs={"pk": self.kwargs["pk"]},
                )
            )
        except Exception:
            raise

class GroupsView(TemplateView):
    template_name = "byro_groups/groups.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["lists"] = Group.objects.all()
        ctx["form"] = GroupCreationForm()
        return ctx



class GroupAdd(GroupsView):
    def post(self, request):
        form = GroupCreationForm(request.POST)
        if not form.is_valid():
            messages.error(request, _("Error."))
            return redirect(
                reverse("plugins:byro_groups:groups.groups")
            )
        try:
            group = Group.objects
            group.create(**form.cleaned_data)
            messages.success(request, _("Group added succesfully"))
        except Exception as e:
            messages.error(
                request, _("Error creating the group: ") + str(e)
            )
        return redirect(
            reverse(
                "plugins:byro_groups:groups.list",)
        )

class GroupRemove(GroupsView):
    def post(self, request, list_id):
        group = Group.objects.filter(pk=list_id).first()
        try:
            group.delete()
            messages.success(request, _("Group deleted succesfully."))
            return redirect(
                reverse(
                    "plugins:byro_groups:groups.list",)
                )
        except Exception as e:
            messages.error(
                request, _("Error deleting the group: ") + str(e)
            )
            return redirect(
                reverse(
                    "plugins:byro_groups:groups.list",)
                )