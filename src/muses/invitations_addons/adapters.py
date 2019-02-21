from invitations.adapters import BaseInvitationsAdapter


class InvitationsAdapter(BaseInvitationsAdapter):
    """Invitations adapter."""

    def clean_email(self, email):
        """

        :param email:
        :return:
        """
