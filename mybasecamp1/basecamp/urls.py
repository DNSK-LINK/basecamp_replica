from django.contrib.auth.views import LogoutView, PasswordChangeView, LoginView
from django.urls import path

from .views import *

app_name = 'basecamp'
urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginView.as_view(extra_context={'next': 'basecamp:project', 'title': 'Login', 'logo': True},
                                     redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(next_page='basecamp:home'), name='logout'),
    path('password_change/', PasswordChangeView.as_view(template_name='basecamp/password_change.html',
                                                        extra_context={'title': 'Password change', 'logo': True}),
         name='password_change'),
    path('userinfo/<int:pk>/', UserInfo.as_view(), name='userinfo'),
    path('project/', ProjectList.as_view(), name='project'),
    path('project/<int:pk>/', ProjectDetail.as_view(), name='detail'),
    path('delete/<int:pk>/', UserDelete.as_view(), name='delete'),
    path('create_project/', CreateProject.as_view(), name='create_project'),
    path('delete_project/<int:pk>/', DeleteProject.as_view(), name='delete_project'),
    path('project/<int:pk>/membership/', Membership.as_view(), name='membership'),
    path('project/<int:pk>/add-info', CreateDiscussion.as_view(), name='add_info_project_detail'),
    path('edit_project/<int:pk>', EditProject.as_view(), name='edit_project'),
]
