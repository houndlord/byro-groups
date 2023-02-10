from django.urls import path

from . import views

urlpatterns = [
    path(
        "members/view/<int:pk>/groups",
        views.MemberGroups.as_view(),
        name="members.groups.groups",
    ),
    path(
        "members/view/<int:pk>/groups/add",
        views.MemberAdd.as_view(),
        name="members.groups.add",
    ),
    path(
        "members/view/<int:pk>/groups/<int:list_id>/remove",
        views.MemberRemove.as_view(),
        name="members.groups.remove",
    ),
    path("groups/", views.GroupAdd.as_view(), name="groups.list",),
    path("groups/<int:list_id>/remove", views.GroupRemove.as_view(), name="groups.list.remove",),
    path("groups/<int:list_id>/rename", views.GroupRename.as_view(), name="groups.list.rename",),
    path("groups/<int:pk>/members/", views.GroupMembersView.as_view(), name="groups.members.list",),
    path("groups/<int:pk>/members/add", views.SubgroupAdd.as_view(), name="groups.members.add",),
    path("groups/<int:pk>/members/<int:list_id>/add", views.SubgroupRemove.as_view(), name="groups.members.remove",),
    path("groups/<int:pk>/members/<int:list_id>/remove_member", views.GroupMembersRemove.as_view(), name="groups.members.removemember",),
]