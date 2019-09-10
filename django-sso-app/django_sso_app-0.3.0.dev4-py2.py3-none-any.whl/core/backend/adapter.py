import logging

from django.utils.translation import activate as activate_translation
from django.conf import settings
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter

from ..common import PROFILE_FIELDS

logger = logging.getLogger('backend')


class UserAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        cleaned_data = form.get_cleaned_data()
        logger.info('Saving new user {0} with email {1}'.format(cleaned_data.get('username'), cleaned_data.get('email')))

        for f in PROFILE_FIELDS:
            setattr(user, f, cleaned_data.get(f, None))

        new_user = super(UserAdapter, self).save_user(
            request, user, form, commit)

        return new_user

    def render_mail(self, template_prefix, email, context):
        user = context.get('user')
        user_language = user.language
        logger.info('Rendering mail for {0} with language {1}'.format(user, user_language))
        activate_translation(user_language)
        context.update({
            'EMAILS_DOMAIN': settings.EMAILS_DOMAIN,
            'EMAILS_SITE_NAME': settings.EMAILS_SITE_NAME
            })
        return super(UserAdapter, self).render_mail(template_prefix, email, context)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.
        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse(
            "account_confirm_email",
            args=[emailconfirmation.key])
        ret = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL + "://" + settings.EMAILS_DOMAIN + url
        return ret

