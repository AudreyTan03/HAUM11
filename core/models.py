from django.db import models
from django.forms import TextInput
from django.utils import timezone

from dashboard import admin


# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100)
    comment = models.TextField(null=True, blank=True)
    subject = models.TextField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

#
# class LoginHistoryAdmin(admin.ModelAdmin):
#     list_display = ('user', 'login_time', 'logout_time')
#     list_filter = ('user', 'login_time')
#
#
# class LoginHistory:
#     pass