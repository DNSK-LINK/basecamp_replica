from importlib.resources import _

from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


def validate_project_title(input_title):
    if Project.objects.filter(title=input_title):
        raise ValidationError(_('%(input_name)s is exist'),
                              params={'input_name': input_title},
                              )


class Project(models.Model):
    title = models.CharField(max_length=255, validators=[validate_project_title])
    description = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    related_groups = models.ManyToManyField(Group)
    time_create = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Permission.objects.filter(codename=('view_'+str(self.id))):
            group_admin = Group.objects.create(name=str(self.id) + '-admin')
            group = Group.objects.create(name=str(self.id))
            self.related_groups.add(group, group_admin)
            user_permission = Permission.objects.create(
                codename='view_' + str(self.id),
                name='Can view ' + str(self.id),
                content_type=ContentType.objects.get_for_model(Project)
            )
            admin_permission = Permission.objects.create(
                codename='change_' + str(self.id),
                name='Can change ' + str(self.id),
                content_type=ContentType.objects.get_for_model(Project)
            )
            group.permissions.add(user_permission)
            group_admin.permissions.add(admin_permission)
            self.created_by.groups.add(group_admin, group)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('basecamp:detail', kwargs={'pk': self.pk})


class Discussion(models.Model):
    disc_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.disc_name


class DiscussionMessage(models.Model):
    user = models.CharField(max_length=100)
    message_text = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    related_discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)

    def __str__(self):
        return self.message_text


class Task(models.Model):
    task_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    is_solved = models.BooleanField(default=False)
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_name


class Attachments(models.Model):
    files = models.FileField(upload_to="files/%Y/%m/%d/")
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.files.name
