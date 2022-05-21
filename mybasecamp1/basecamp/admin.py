from django.contrib import admin

from .models import *

admin.site.register(Project)
admin.site.register(Discussion)
admin.site.register(DiscussionMessage)
admin.site.register(Task)
admin.site.register(Attachments)
admin.site.register(Permission)
