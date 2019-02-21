import logging

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from invitations.views import (
    AcceptInvite as DefaultAcceptInvite,
    SendInvite as DefaultSendInvite
)
from invitations.utils import get_invitation_model

from .decorators import superuser_required
from .forms import MultipleInvitesForm

Invitation = get_invitation_model()
# InviteForm = get_invite_form()

LOGGER = logging.getLogger(__name__)

__all__ = (
    'SendMultipleInvites',
    'SendMultipleInvitesSuccess',
    'AcceptInvite',
)


class SendInvite(DefaultSendInvite):
    """Send invite.

    We simply restrict usage to superuser.
    """

    @method_decorator(superuser_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SendInvite, self).dispatch(request, *args, **kwargs)


class SendMultipleInvites(FormView):
    """Send multiple invites.

    Restricted to the superuser.
    """
    template_name = 'invitations/forms/_invites.html'
    success_url = 'invitations_addons:send-invites-success'
    form_class = MultipleInvitesForm

    @method_decorator(superuser_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SendMultipleInvites, self).dispatch(request,
                                                         *args,
                                                         **kwargs)

    def get_success_url(self):
        """Get success URL.

        :return:
        """
        return reverse(self.success_url)

    def form_valid(self, form):
        LOGGER.debug('form_valid')
        emails = form.cleaned_data["emails"]
        for email in emails:
            try:
                invite = Invitation.create(
                    email=email,
                    inviter=self.request.user,
                    user_group_id=form.cleaned_data['user_group']
                )
                invite.save()
                invite.send_invitation(self.request)
            except Exception:
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        LOGGER.debug('form_invalid')
        return self.render_to_response(self.get_context_data(form=form))


class SendMultipleInvitesSuccess(TemplateView):
    """Send multiple invites success."""

    template_name = 'invitations/forms/_invites_success.html'


class AcceptInvite(DefaultAcceptInvite):
    """Accept invite."""

    def get_signup_redirect(self):
        signup_redirect = super(AcceptInvite, self).get_signup_redirect()
        email = self.object.email
        return "{}?email={}".format(signup_redirect, email)
