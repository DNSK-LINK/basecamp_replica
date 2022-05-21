from abc import ABC

from django.contrib.auth.mixins import UserPassesTestMixin

from .models import *


class ProjectDataMixin:

    def get_user_context(self, **kwargs):
        user = self.request.user
        project = Project.objects.get(id=self.kwargs['pk'])
        project_group = list(project.related_groups.exclude(name__endswith='-admin'))[0]
        project_admin_group = project.related_groups.get(name__endswith='-admin')
        members = User.objects.filter(groups=project_group)
        admins = User.objects.filter(groups=project_admin_group)
        creator = project.created_by
