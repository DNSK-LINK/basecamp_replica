from importlib.resources import _
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *


def validate_project_title(input_title):
    if Project.objects.filter(title=input_title):
        raise ValidationError(_('%(input_name)s is exist'),
                              params={'input_name': input_title},
                              )


def validate_user(input_name):
    if not User.objects.filter(username=input_name):
        raise ValidationError(_('%(input_name)s is not exist'),
                              params={'input_name': input_name},
                              )


class AddUserForm(forms.Form):
    user = forms.CharField(max_length=50, validators=[validate_user])
    project_pk = forms.IntegerField()
    option = forms.CharField(max_length=30)

    user.widget.attrs.update({'class': 'form-widget', 'size': '54'})

    def change_user_status(self):
        received_user = User.objects.get(username=self.cleaned_data['user'])
        project = Project.objects.get(id=self.cleaned_data['project_pk'])
        project_group = list(project.related_groups.exclude(name__endswith='-admin'))[0]
        project_admin_group = project.related_groups.get(name__endswith='-admin')
        option = self.cleaned_data['option']
        if option == 'Add user':
            received_user.groups.add(project_group)
        elif option == 'Add to admins':
            received_user.groups.add(project_admin_group)
        elif option == 'Delete user':
            if project.created_by != received_user:
                received_user.groups.remove(project_group, project_admin_group)
        else:
            if project.created_by != received_user:
                received_user.groups.remove(project_admin_group)


class AddDiscussionForm(forms.Form):
    title = forms.CharField(max_length=255)
    user_id = forms.IntegerField(required=False)
    project_pk = forms.IntegerField()
    discussion_id = forms.IntegerField(required=False)
    file = forms.FileField(required=False)
    option = forms.CharField(max_length=30)

    file.widget.attrs.update({'class': 'form-widget'})

    def serve_discussion_form(self):
        project = Project.objects.get(id=self.cleaned_data['project_pk'])
        name = self.cleaned_data['title']
        option = self.cleaned_data['option']
        if option == 'Add discussion':
            Discussion.objects.create(disc_name=name, related_project=project)
        elif option == 'Send':
            received_user = User.objects.get(id=self.cleaned_data['user_id'])
            discussion = Discussion.objects.get(id=self.cleaned_data['discussion_id'])
            DiscussionMessage.objects.create(user=received_user.username,
                                             message_text=name, related_discussion=discussion)
        elif option == 'Add new task':
            Task.objects.create(task_name=name, related_project=project)
        elif option == 'Add attachment':
            file = self.cleaned_data['file']
            Attachments.objects.create(files=file, related_project=project)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(size=108)
        self.fields['title'].widget.attrs.update({'class': 'form-widget'})
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 3, 'cols': 100})
        self.fields['description'].widget.attrs.update({'class': 'form-widget'})

    class Meta:
        model = Project
        fields = ['title', 'description']


class UserInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-widget'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-widget'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-widget'})
        self.fields['email'].widget.attrs.update({'class': 'form-widget'})

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class EditProjectForm(forms.Form):
    title = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 80, 'class': 'form-widget'}))
    description = forms.CharField(max_length=255, required=False,
                                  widget=forms.Textarea(attrs={'rows': 3, 'cols': 80, 'class': 'form-widget'}))
    project_pk = forms.IntegerField()
    option = forms.CharField(max_length=30)
    member = forms.CharField(max_length=100, required=False, validators=[validate_user],
                             widget=forms.TextInput(attrs={'class': 'form-widget', 'size': '60'}))
    admin = forms.BooleanField(required=False)
