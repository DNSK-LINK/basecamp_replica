from abc import ABC

from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.edit import FormView

from basecamp.forms import *


def home(request):
    return render(request, 'basecamp/home.html', {'title': 'BASECAMP', 'logo': True})


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'basecamp/register.html'
    extra_context = {'title': 'Registration'}

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('basecamp:project')


class UserInfo(UserPassesTestMixin, UpdateView, ABC):
    form_class = UserInfoForm
    template_name = 'basecamp/userinfo.html'
    success_url = reverse_lazy('basecamp:project')

    def test_func(self, **kwargs):
        return self.request.user.id == self.kwargs['pk']

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        new_context = {'title': 'Userinfo', 'pk': self.kwargs['pk'],
                       'current_user_id': self.request.user.id}
        context.update(new_context)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('basecamp:project')


class UserDelete(UserPassesTestMixin, DeleteView, ABC):
    model = User
    template_name = 'basecamp/delete.html'
    success_url = reverse_lazy('basecamp:logout')

    def test_func(self, **kwargs):
        return self.request.user.id == self.kwargs['pk']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        new_context = {'title': 'Delete user', 'pk': self.kwargs['pk']}
        context.update(new_context)
        return context

    def delete(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['pk'])
        projects = Project.objects.filter(created_by=user)
        for project in projects:
            project.related_groups.all().delete()
            Permission.objects.filter(codename=('view_' + str(project.id))).delete()
            Permission.objects.filter(codename=('change_' + str(project.id))).delete()
            project.delete()
        return super().delete(self, request, *args, **kwargs)


class ProjectDetail(UserPassesTestMixin, DetailView, ABC):
    model = Project
    context_object_name = 'project'

    def test_func(self, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return False
        return self.request.user.has_perm('basecamp.view_' + str(project.id))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        project = context['project']
        creator = project.created_by
        user_admin = self.request.user.has_perm('basecamp.change_' + str(project.id))
        user_group = list(project.related_groups.exclude(name__endswith='-admin'))[0]

        discussions = Discussion.objects.filter(related_project=project)

        messages = list(DiscussionMessage.objects.filter(related_discussion__in=discussions).values('message_text',
                                                                                                    'related_discussion', 'user'))
        tasks = Task.objects.filter(related_project=project)
        files = Attachments.objects.filter(related_project=project)

        new_context = {'members': User.objects.filter(groups=user_group), 'creator': creator,
                       'user_admin': user_admin, 'title': project.title, 'discussions': discussions,
                       'messages': messages, 'tasks': tasks, 'pk': self.kwargs['pk'], 'files': files}
        context.update(new_context)
        return context


class ProjectList(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'project'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_groups = self.request.user.groups.exclude(name__endswith='-admin')

        project_list = []
        my_project_list = []
        shared_project_list = []
        if user_groups:
            for i in range(len(user_groups)):
                project_list.append([])
                project = Project.objects.get(related_groups=user_groups[i])
                project_list[i].append(project)
                project_list[i].append(len(User.objects.filter(groups=user_groups[i])))
                discussions = set(Discussion.objects.filter(related_project=project))
                project_list[i].append(len(DiscussionMessage.objects.filter(related_discussion__in=discussions)))
        for project in project_list:
            if project[0].created_by == self.request.user:
                my_project_list.append(project)
            else:
                shared_project_list.append(project)
        new_context = {'project_list': project_list, 'my_project_list': my_project_list,
                       'shared_project_list': shared_project_list, 'title': 'Projects list'}
        context.update(new_context)
        return context


class CreateProject(LoginRequiredMixin, CreateView):
    form_class = CreateProjectForm
    template_name = 'basecamp/project_create.html'
    success_url = reverse_lazy('basecamp:project')
    extra_context = {'title': 'New Project'}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class DeleteProject(UserPassesTestMixin, DeleteView, ABC):
    model = Project
    context_object_name = 'project'
    success_url = reverse_lazy('basecamp:project')
    extra_context = {'title': 'Delete project'}

    def test_func(self, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return False
        return self.request.user.has_perm('basecamp.change_' + str(project.id))

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=self.kwargs['pk'])
        project.related_groups.all().delete()
        Permission.objects.filter(codename=('view_'+str(project.id))).delete()
        Permission.objects.filter(codename=('change_'+str(project.id))).delete()
        return super().delete(self, request, *args, **kwargs)


class Membership(UserPassesTestMixin, FormView, ABC):
    form_class = AddUserForm
    template_name = 'basecamp/membership.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('basecamp:membership', kwargs={'pk': pk})

    def test_func(self, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return False
        return self.request.user.has_perm('basecamp.change_' + str(project.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['pk'])
        project_group = list(project.related_groups.exclude(name__endswith='-admin'))[0]
        members = User.objects.filter(groups=project_group)
        admins = [admin for admin in members if admin.has_perm('basecamp.change_' + str(project.id))]
        new_context = {'members': members, 'admins': admins, 'title': 'Membership', 'pk': self.kwargs['pk']}
        context.update(new_context)
        return context

    def form_valid(self, form):
        form.change_user_status()
        return super().form_valid(form)


class CreateDiscussion(UserPassesTestMixin, FormView, ABC):
    form_class = AddDiscussionForm
    template_name = 'basecamp/project_detail.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('basecamp:detail', kwargs={'pk': pk})

    def test_func(self, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return False
        return self.request.user.has_perm('basecamp.view_' + str(project.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = Project.objects.get(id=self.kwargs['pk'])
        project_group = list(project.related_groups.exclude(name__endswith='-admin'))[0]
        members = User.objects.filter(groups=project_group)
        admins = [admin for admin in members if admin.has_perm('basecamp.change_' + str(project.id))]
        new_context = {'members': members, 'admins': admins, 'title': 'Membership', 'pk': self.kwargs['pk']}
        context.update(new_context)
        return context

    def form_valid(self, form):
        form.serve_discussion_form()
        return super().form_valid(form)

    def form_invalid(self, form):
        pk = form.cleaned_data['project_pk']
        return HttpResponseRedirect(reverse('basecamp:detail', kwargs={'pk': pk}))


class EditProject(UserPassesTestMixin, FormView, ABC):
    form_class = EditProjectForm
    template_name = 'basecamp/edit_project.html'
    success_url = reverse_lazy('basecamp:project')

    def test_func(self, **kwargs):
        try:
            project = Project.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return False
        return self.request.user.has_perm('basecamp.change_' + str(project.id))

    def get_initial(self, **kwargs):
        project = Project.objects.get(id=self.kwargs['pk'])
        initial = {'title': project.title, 'description': project.description}
        return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        new_context = {'title': 'Edit project', 'pk': self.kwargs['pk']}
        context.update(new_context)
        return context

    def form_valid(self, form):
        option = form.cleaned_data['option']
        project = Project.objects.get(id=form.cleaned_data['project_pk'])
        group = Group.objects.get(name=str(form.cleaned_data['project_pk']))
        admin_group = Group.objects.get(name=(str(form.cleaned_data['project_pk']) + '-admin'))
        if option == 'Add':
            user = User.objects.get(username=form.cleaned_data['member'])
            user.groups.add(group)
            if form.cleaned_data['admin']:
                user.groups.add(admin_group)
            return HttpResponseRedirect(reverse('basecamp:project'))
        elif option == 'Update_description':
            project.description = form.cleaned_data['description']
            project.save()
        else:
            project.title = form.cleaned_data['title']
            project.save()
        return super().form_valid(form)
