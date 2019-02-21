from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_group', 'sent', 'accepted')

    def get_queryset(self, request):
        return super(InvitationAdmin, self) \
            .get_queryset(request) \
            .select_related('user_group')
