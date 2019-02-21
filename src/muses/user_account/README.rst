Account settings
================
All settings and custom fields that did not fit into the user model, as well
as other things related to that.

Models
------
`AccountSettings` contains all customisations.

Fields
------
For now the following custom fields are added:

- language: Language preference of the user.

Serializers
-----------
`CustomUserDetailsSerializer` serializer is used as a `USER_DETAILS_SERIALIZER`
for `django-rest-auth`. It takes care of the additional settings we have
done in the `AccountSettings` model.
