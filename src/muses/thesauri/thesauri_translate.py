import requests
# from requests.auth import HTTPBasicAuth

from muses.cached_api_calls.models import ThesauriTranslation

from .constants import API_TERM_PATTERN, API_LOOKUP_PATTERN


__all__ = (
    'ThesauriClient',
)


class ThesauriClient(object):
    """Thesauri client."""

    def __init__(self, user="", password=""):
        """Constructor.

        :param user:
        :param password:
        :type user: str
        :type password: str
        """
        self.user = user
        self.password = password

    def lookup_key(self, source_language, term):
        """Lookup the key of a specific term

        Example:

        >>> client = ThesauriClient(user='user', password='secret')
        >>> key = client.lookup_key('en', "scarabee")

        :param source_language:
        :param term:
        :type source_language: str
        :type term: str
        :return:
        :rtype: str
        """
        response = requests.get(API_LOOKUP_PATTERN.format(term))

        if response.ok and response.text != u'null':
            result = response.json()
            if isinstance(result['result'], dict):
                result['result'] = [result['result']]
            for item in result['result']:
                if item['value'].lower() == term and item['id']:
                    key = item['id'].split('/')[-1]

                    # The following request does not require authentication.
                    # Moreover, if authentication provided, 401 response is
                    # given back.
                    response_trans = requests.get(
                        API_TERM_PATTERN.format(key, source_language),
                        # auth=HTTPBasicAuth(self.user, self.password)
                    )
                    if response_trans.ok:
                        result_trans = response_trans.text
                        source_word = result_trans.lower().strip()
                        if source_word == term:
                            return key

    def translate(self, source_language, target_language, term, use_cache=False):
        """Translate given term using Thesauri.

        Search thesauri and return valid translation from source_language
        to target_language.
        source_language and target_language should be ISO-639 language codes.

        Valid languages are English, French, German and Dutch

        Example:

        >>> client = ThesaurusClient(user='user', password='secret')
        >>> key = client.translate(
        >>>     source_language='nl',
        >>>     target_language='en',
        >>>     term="scarabee",
        >>>     use_cache=True
        >>> )

        :param source_language: Language to translate from
        :param target_language: Language to translate to
        :param term: Term to translate
        :param use_cache:
        :type source_language: str
        :type target_language: str
        :type term: str
        :type use_cache: bool
        :return:
        :rtype: str
        """
        term = term.lower()
        if use_cache:
            try:
                translation = ThesauriTranslation.objects.get(
                    original=term,
                    source_language=source_language,
                    target_language=target_language
                )
                if translation.translation_exists:
                    return translation.translation
                else:
                    return None
            except ThesauriTranslation.DoesNotExist:
                pass

        key = self.lookup_key(source_language, term)

        if key:
            # The following request does not require authentication.
            # Moreover, if authentication provided, 401 response is
            # given back.
            response = requests.get(
                API_TERM_PATTERN.format(key, target_language),
                # auth=HTTPBasicAuth(self.user, self.password)
            )

            if response.ok:
                result = response.text.lower()
                if use_cache:
                    ThesauriTranslation.objects.create(
                        original=term,
                        translation=result,
                        source_language=source_language,
                        target_language=target_language,
                        translation_exists=bool(result)
                    )
                return result

        if use_cache:
            ThesauriTranslation.objects.create(
                original=term,
                source_language=source_language,
                target_language=target_language,
                translation_exists=False
            )

    def translate_nl_to_en(self, term, use_cache=False):
        """Translate a term from Dutch to English

        :param term:
        :param use_cache:
        :type term: str
        :type use_cache: bool
        :return:
        :rtype: str
        """
        return self.translate('nl', 'en', term, use_cache)

    def translate_en_to_nl(self, term, use_cache=False):
        """Translate a term from English to Dutch

        :param term:
        :param use_cache:
        :type term: str
        :type use_cache: bool
        :return:
        :rtype: str
        """
        return self.translate('en', 'nl', term, use_cache)

    def translate_from_key(self, target_language, key):
        """Translate an item with a known key to a target_language

        :param target_language:
        :param key: thesauri key associated with the concept
        :type target_language: str
        :type key: str
        :return:
        :rtype: str
        """
        response = requests.get(
            API_TERM_PATTERN.format(key, target_language),
            # auth=HTTPBasicAuth(self.user, self.password)
        )

        if response.ok:
            result = response.text.lower()
            return result
