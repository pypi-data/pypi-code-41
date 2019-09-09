__version__ = '0.1.0'

import requests
import re


class MonicaException(Exception): pass
class MonicaSearchFailure(MonicaException): pass


class _MonicaAPIBase:
    def __init__(self,
                 access_token,
                 api_base='https://app.monicahq.com/api'):
        self._token = access_token
        self._api_base = api_base.rstrip('/')

    def _call_api(self, endpoint, method, params=None, request_data=None):
        method = method.lower()
        assert method in ('get', 'post', 'put', 'delete')
        r = getattr(requests, method)(
                self._api_base + '/' + endpoint.lstrip('/'),
                params=params,
                json=request_data,
                headers={
                    'Authorization': 'Bearer '+self._token,
                },
            )
        r.raise_for_status()
        return r.json()


class _MonicaAPITags(_MonicaAPIBase):

    def _all_tags(self):
        resp = self._call_api('/tags', 'get')
        return {i['name'].lower(): i['id'] for i in resp['data']}

    def _refresh_tag_cache(self):
        self._cached_all_tags = self._all_tags()
        
    @property
    def all_tags(self):
        if not hasattr(self, '_cached_all_tags'):
            self._refresh_tag_cache()
        return self._cached_all_tags

    def _refresh_cache_if_unseen(self, tags_list):
        """
        If an unknown tag is encountered, this will prompt a cache refresh
        from the API. It takes no further action, so other methods should
        still account for the possibility that a tag does not exist.
        """
        if set(map(str.lower, tags_list)).difference(self.all_tags):
            self._refresh_tag_cache()

    def resolve_tags(self, tags_list):
        self._refresh_cache_if_unseen(tags_list)
        ids = []
        for t in map(str.lower, tags_list):
            if not t in self.all_tags:
                raise KeyError(f'Unknown Tag: {t}')
            ids.append(self.all_tags[t])
        return ids

    
class _MonicaAPIGenders(_MonicaAPIBase):

    def _all_genders(self):
        resp = self._call_api('/genders', 'get')
        return {i['name']: i['id'] for i in resp['data']}
        

    @property
    def all_genders(self):
        if not hasattr(self, '_cached_all_genders'):
            self._cached_all_genders = self._all_genders()
        return self._cached_all_genders


class _MonicaAPICacheableFields(_MonicaAPITags,
                                 _MonicaAPIGenders):
    def _precache_fields(self):
        """
        Precache customisable, refer-by-id fields like Gender and Tags.
        This permits things like knowing when it is necessary to make
        a new tag, or when to prompt that a gender is unknown.
        """
        self.all_genders
        self.all_tags


class MonicaAPI(_MonicaAPICacheableFields):

    def search_contacts(self, query, page=1, limit=25):
        next_page = lambda: self.search_contacts(query, page=page+1, limit=limit)
        resp = self._call_api('/contacts', 'get', params={'query': query})
        is_last = resp['meta']['current_page'] == resp['meta']['last_page']
        return resp['data'], None if is_last else next_page

    def add_contact(self,
                    first_name,
                    last_name=None,
                    nickname=None,
                    gender=None,
                    birthdate_day=None,
                    birthdate_month=None,
                    birthdate_year=None,
                    is_deceased=False,
                    is_deceased_date_known=False,
                    ):
        """
        Add a contact. Most of the fields are self-explanatory. Except:

        gender: This should be a plaintext version of a gender known to the API. This will be checked against a locally-held cache: genders will not be created on-the-fly when an unknown gender is encountered.
        tags: Not Implemented Yet
        """
        gender_id = self.all_genders[gender]
        is_birthdate_known=bool(birthdate_day
                                and birthdate_month
                                and birthdate_year)
        contact_data = dict(
                    first_name=first_name,
                    last_name=last_name,
                    nickname=nickname,
                    gender=gender,
                    birthdate_day=birthdate_day,
                    birthdate_month=birthdate_month,
                    birthdate_year=birthdate_year,
                    is_birthdate_known=is_birthdate_known,
                    is_deceased=is_deceased,
                    is_deceased_date_known=is_deceased_date_known,
        )
        return self._call_api('/contacts/', 'post', request_data=contact_data)

    def resolve_contact_id(self, contact_id_or_query):
        """
        Returns the query if it is an int.
        If it is a string, it runs a search and returns the _first result_.
        """
        assert isinstance(contact_id_or_query, (str, int))
        if isinstance(contact_id_or_query, int):
            return contact_id_or_query
        results, _ = self.search_contacts(contact_id_or_query, limit=1)
        if not results:
            raise MonicaSearchFailure(contact_id_or_query)
        first = results[0]
        return first['id']
        
    def tag_contact(self, contact_id_or_query, tags_list):
        contact_id = self.resolve_contact_id(contact_id_or_query)
        data = { 'tags': tags_list }
        endpoint = '/contacts/{}/setTags'.format(contact_id)
        resp = self._call_api(endpoint, 'post', request_data=data)
        if not resp['data'].get('id', None) == contact_id:
            raise MonicaException('Contact ID returned by API was not the target contact ID: {} requested, {} returned'.format(contact_id, resp['data'].get('id')))

    def untag_contact(self, contact_id_or_query, tags_list):
        contact_id = self.resolve_contact_id(contact_id_or_query)
        tag_ids = self.resolve_tags(tags_list)  # TODO
        data = { 'tags': tag_ids }
        endpoint = '/contacts/{}/unsetTag'.format(contact_id)
        resp = self._call_api(endpoint, 'post', request_data=data)
        if not resp['data'].get('id', None) == contact_id:
            raise MonicaException('Contact ID returned by API was not the target contact ID: {} requested, {} returned'.format(contact_id, resp['data'].get('id')))

    def task_add(self,
                 contact_id_or_query,
                 title:str,
                 *,
                 description:str=None,
                 completed:bool=False,
                 completed_at:str=None,
                 ):
        assert(isinstance(title, str) and len(title) <= 255)
        assert(isinstance(completed, bool))
        if description is not None:
            assert(isinstance(description, str) and len(title) <= 1000000)
        if completed_at is not None:
            assert(isinstance(completed_at, str) and
                   re.match(r'\d\d\d\d-\d\d-\d\d', completed_at))
        contact_id = self.resolve_contact_id(contact_id_or_query)
        data = {
            'title': title,
            'completed': int(completed),
            'contact_id': contact_id,
        }
        if description:
            data['description'] = description
        if completed_at:
            data['completed_at'] = completed_at
        resp = self._call_api('/tasks/', 'post', request_data=data)
