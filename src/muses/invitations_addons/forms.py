from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from invitations.adapters import get_invitations_adapter
from invitations.exceptions import AlreadyAccepted, AlreadyInvited, UserRegisteredEmail
from invitations.utils import get_invitation_model

from multi_email_field.forms import MultiEmailField

Invitation = get_invitation_model()


__all__ = (
    'VALIDATION_ERRORS',
    'CleanEmailMixin',
    'MultipleInvitesForm',
)

VALIDATION_ERRORS = {
    # Already invited
    "already_invited": _(
        "This e-mail address {} has already been invited."
    ),
    "already_invited_plural": _(
        "These e-mail addresses {} have already been invited."
    ),

    # Already accepted
    "already_accepted": _(
        "This e-mail address {} has already accepted an invite."
    ),
    "already_accepted_plural": _(
        "These e-mail addresses {} have already accepted an invite."
    ),

    # Email in use
    "email_in_use": _(
        "An active user is using this e-mail address {}."
    ),
    "email_in_use_plural": _(
        "Active users are using these e-mail addresses {}"
    ),
}


class CleanEmailMixin(object):

    def validate_invitation(self, email):
        if Invitation.objects.all_valid().filter(email__iexact=email,
                                                 accepted=False):
            raise AlreadyInvited
        elif Invitation.objects.filter(email__iexact=email, accepted=True):
            raise AlreadyAccepted
        elif get_user_model().objects.filter(email__iexact=email):
            raise UserRegisteredEmail
        else:
            return True

    def clean_emails(self):
        # The idea is to display all errors that belong to a certain errors.
        already_invited_errors = []
        already_accepted_errors = []
        email_in_use_errors = []

        emails = self.cleaned_data["emails"]
        for email in emails:
            email = get_invitations_adapter().clean_email(email)
            try:
                self.validate_invitation(email)
            except AlreadyInvited:
                already_invited_errors.append(email)
            except AlreadyAccepted:
                already_accepted_errors.append(email)
            except UserRegisteredEmail:
                email_in_use_errors.append(email)

        # Goes as 1st
        if already_invited_errors:
            _error_type = 'already_invited_plural' \
                if len(already_invited_errors) > 1 \
                else 'already_invited'

            raise forms.ValidationError(
                VALIDATION_ERRORS[_error_type].format(
                    ', '.join(already_invited_errors)
                )
            )

        # Goes as 2nd
        if email_in_use_errors:
            _error_type = 'email_in_use_plural' \
                if len(email_in_use_errors) > 1 \
                else 'email_in_use'

            raise forms.ValidationError(
                VALIDATION_ERRORS[_error_type].format(
                    ', '.join(email_in_use_errors)
                )
            )

        # Goes as 3rd
        if already_accepted_errors:
            _error_type = 'already_accepted_multiple' \
                if len(already_accepted_errors) > 1 \
                else 'already_accepted'

            raise forms.ValidationError(
                VALIDATION_ERRORS[_error_type].format(
                    ', '.join(already_accepted_errors)
                )
            )

        return emails


def user_group_choices():
    from muses.user_account.models import UserGroup
    choices = list(UserGroup.objects.values_list('id', 'name'))
    return choices


class MultipleInvitesForm(forms.Form, CleanEmailMixin):

    user_group = forms.ChoiceField(choices=[])
    emails = MultiEmailField(
        label=_("E-mails"),
        required=True,
        widget=forms.Textarea(
            attrs={"rows": "10", "cols": "40"}), initial="")

    def __init__(self, *args, **kwargs):
        super(MultipleInvitesForm, self).__init__(*args, **kwargs)
        self.fields['user_group'].choices = user_group_choices()
