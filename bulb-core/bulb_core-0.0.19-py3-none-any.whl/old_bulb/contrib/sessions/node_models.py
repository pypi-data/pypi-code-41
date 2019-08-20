from bulb.contrib.sessions.exceptions import BULBSessionError, BULBSessionDoesNotExist, BULBSessionDoesNotHaveData
from bulb.db import node_models
from bulb.db.base import gdbh
from django.utils import timezone


class RelatedUserRelationship(node_models.Relationship):
    rel_type = "IS_SESSION_OF"
    direction = "from"
    start = "self"
    target = "User"
    auto = False
    on_delete = "PROTECT"
    unique = True


class AbstractBaseSession:

    def encode(self, session_dict):
        """
        Return the given session dictionary serialized and encoded as a string.
        """
        session_store_class = self.__class__.get_session_store_class()
        return session_store_class().encode(session_dict)

    def save(self, session_key, session_dict, expire_date):
        if session_dict:
            s = self.__class__(session_key, self.encode(session_dict), expire_date)
        else:
            raise BULBSessionDoesNotHaveData("The does'nt have datas ('session_dict'), failed to save it.")
        return s

    def __str__(self):
        return self.session_key

    @classmethod
    def get_session_store_class(cls):
        raise NotImplementedError

    def get_decoded(self):
        session_store_class = self.get_session_store_class()
        return session_store_class().decode(self.session_data)


class Session(node_models.Node, AbstractBaseSession):
    """
    Django provides full support for anonymous sessions. The session
    framework lets you store and retrieve arbitrary data on a
    per-site-visitor basis. It stores data on the server side and
    abstracts the sending and receiving of cookies. Cookies contain a
    session ID -- not the data itself.

    The Django sessions framework is entirely cookie-based. It does
    not fall back to putting session IDs in URLs. This is an intentional
    design decision. Not only does that behavior make URLs ugly, it makes
    your site vulnerable to session-ID theft via the "Referer" header.

    For complete documentation on using Sessions in your code, consult
    the sessions documentation that is shipped with Django (also available
    on the Django Web site).
    """

    session_key = node_models.Property(required=True,
                                       unique=True)  # TODO : add max_length = 40

    session_data = node_models.Property()

    expire_date = node_models.Property()  # TODO : add db_index = True

    related_user = RelatedUserRelationship()

    def __str__(self):
        return f'<Session object(session_key="{self.session_key}", expire_date="{self.expire_date}")>'

    def __repr__(self):
        return f'<Session object(session_key="{self.session_key}", expire_date="{self.expire_date}")>'

    @classmethod
    def get_session_store_class(cls):
        from bulb.contrib.sessions.backends.db import SessionStore
        return SessionStore

    @classmethod
    def get(cls, uuid=None, session_key=None, order_by=None, limit=None, skip=None, desc=False, only=None):
        """
        This method allow the retrieving of Session (or of one of its children classes) instances.


        :param uuid: The Universal Unique Identifier of a session to get an unique session instance.

        :param session_key: The session_key of a session to get an unique session instance.

        :param order_by: Must be the name of the property with which the returned datas will be sorted.
                         Examples : "datetime", "first_name", etc...

        :param limit: Must be an integer. This parameter defines the number of returned elements.

        :param skip: Must be an integer. This parameter defines the number of skipped elements. For example if
                     self.skip = 3, the 3 first returned elements will be skipped.

        :param desc: Must be a boolean. If it is False the elements will be returned in an increasing order, but it is
                     True, they will be returned in a descending order.

        :param only: Must be a list of field_names. If this parameter is filled, the return will not be Permission
                     instances, but a dict with "only" the mentioned fields.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """
        property_statement = ""
        order_by_statement = ""
        limit_statement = ""
        skip_statement = ""
        desc_statement = ""

        # Build the property_statement.
        if uuid is not None and session_key is not None:
            property_statement = "{uuid:'%s', session_key:'%s'}" % (uuid, session_key)

        elif uuid is not None:
            property_statement = "{uuid:'%s'}" % uuid

        elif session_key is not None:
            property_statement = "{session_key:'%s'}" % session_key

        # Build the match_statement.
        cyher_labels = node_models.DatabaseNode.format_labels_to_cypher(cls._get_labels())
        match_statement = f"MATCH (s:{cyher_labels} {property_statement})"

        # Build the with_statement.
        with_statement = "WITH s"

        # Build order_by statements.
        if order_by is not None:
            order_by_statement = f"ORDER BY s.{order_by}"

        # Build return_statement statements.
        if not only:
            return_statement = "RETURN (s)"

        else:
            only_statement_list = []

            for element in only:
                only_statement_list.append(f"s.{element}")

            only_statement = ", ".join(only_statement_list)

            return_statement = f"RETURN {only_statement}"

        # Build limit_statement.
        if limit is not None:
            if not isinstance(limit, str) and not isinstance(limit, int):
                raise BULBSessionError(
                    f"The 'limit' parameter of the get() method of {cls.__name__} must be a string or an integer.")

            else:
                limit_statement = f"LIMIT {limit}"

        # Build skip_statement and add its required variable.
        if skip is not None:
            if not isinstance(skip, str) and not isinstance(skip, int):
                raise BULBSessionError(
                    f"The 'skip' parameter of the get() method of {cls.__name__} must be a string or an integer.")

            else:
                skip_statement = f"SKIP {skip}"

        # Build desc_statement.
        if not isinstance(desc, bool):
            raise BULBSessionError(
                f"The 'desc' parameter of the get() method of {cls.__name__} must be a boolean.")

        else:
            if desc is True:
                desc_statement = "DESC"

        request_statement = """
             %s
             %s
             %s
             %s
             %s
             %s
             %s
             """ % (match_statement,
                    with_statement,
                    order_by_statement,
                    desc_statement,
                    limit_statement,
                    skip_statement,
                    return_statement)

        response = gdbh.r_transaction(request_statement)

        if response:
            if only is None:
                fake_instances_list = []

                for session_object in response:
                    fake_instances_list.append(cls.build_fake_instance(session_object["s"],
                                                                       forced_fake_instance_class=cls))

                if uuid is not None or session_key is not None:
                    return fake_instances_list[0]

                else:
                    return fake_instances_list

            else:
                return response

        else:
            return None

    @classmethod
    def exists(cls, session_key):
        response = cls.get(session_key=session_key)

        if response:
            return True

        else:
            return False

    @classmethod
    def delete_session(cls, session_key):
        response = cls.get(session_key=session_key)

        if response:
            gdbh.w_transaction("MATCH (s:Session {session_key:'%s'}) DETACH DELETE (s)" % session_key)

        else:
            raise BULBSessionDoesNotExist(f"No session with session_key = '{session_key}'. So it cannot be deleted.")

    @classmethod
    def clear_expired_sessions(cls):
        gdbh.r_transaction("""
            MATCH (s:Session) 
            WHERE s.expire_date < datetime('%s') 
            DETACH DELETE (s)
            """ % str(timezone.now()).replace(' ', 'T'))
