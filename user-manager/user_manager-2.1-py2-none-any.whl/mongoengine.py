from mongoengine import Document, StringField, BooleanField, ListField, DoesNotExist
from user_manager.user_manager import UserManager, GrantEvent, AuthenticationEvent, UserCreatedEvent, UserRemovedEvent, UserUpdatedEvent, RevokeEvent
import logging


class SimpleUser(Document):

    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    salt = StringField(required=True)
    enabled = BooleanField(default=True)
    roles = ListField()


class Permission(Document):

    role = StringField(required=True)
    resource = StringField(required=True)
    permission = StringField(required=True)
    resource_id = StringField(null=True)
    namespace = StringField(null=True)


class MongoUserManager(UserManager):
    
    def __init__(self, user_model=SimpleUser, permission_model=Permission):
        self.user_model = user_model
        self.permission_model = permission_model
        
    def authenticate(self, username, password):
        try:
            u = self.user_model.objects.get(username=username, enabled=True)

            if u.password == self.encode_password(password, u.salt):
                self.notify(AuthenticationEvent(success=True, username=username))
                return True

        except DoesNotExist:
            self.notify(AuthenticationEvent(success=False, username=username))
            return False

    def create(self, username, password, **kwargs):
        salt = self.generate_salt()
        u = self.user_model(username=username, password=self.encode_password(password, salt), salt=salt, **kwargs)
        u.save()
        self.notify(UserCreatedEvent(user=u))
        return u

    def update_password(self, user, password):
        user.salt = self.generate_salt()
        user.password = self.encode_password(password, user.salt)
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def update(self, user):
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def find(self, user_id):
        return self.user_model.objects.get(user_id)

    def find_by(self, **kwars):
        return self.user_model.objects(**kwars).first()

    def remove(self, user):
        user.remove()
        self.notify(UserRemovedEvent(user=user))

    def enable(self, user, status):
        user.enabled = status
        user.save()
        self.notify(UserUpdatedEvent(user=user))

    def grant(self, role, resource, permission, resource_id=None, namespace=None):
        p = self.permission_model(
            role=role,
            resource=resource,
            permission=permission,
            resource_id=resource_id,
            namespace=namespace
        )
        p.save()
        self.notify(GrantEvent(role=role, resource=resource, permission=permission))

    def revoke(self, role, resource, permission, resource_id=None, namespace=None):
        for p in self.permission_model.objects(
                role=role,
                resource=resource,
                permission=permission,
                resource_id=resource_id,
                namespace=namespace
        ):
            p.remove()
            self.notify(RevokeEvent(role=role, resource=resource, permission=permission))

    def is_granted(self, role, resource, permission, resource_id=None, namespace=None):
        query_filter = {
            "resource": resource,
            "permission": permission,
            "resource_id": resource_id,
            "namespace": namespace
        }

        if isinstance(role, list):
            query_filter["role__in"] = role
        else:
            query_filter["role"] = role

        return self.permission_model.objects(**query_filter).count() > 0

    def get_granted(self, role=None, resource=None, permission=None, resource_id=None, namespace=None, size=100, offset=0):
        query_filter = {}

        if isinstance(role, list):
            query_filter["role__in"] = role
        elif role is not None:
            query_filter["role"] = role

        if isinstance(resource, list):
            query_filter["resource__in"] = resource
        elif resource is not None:
            query_filter["resource"] = resource

        if isinstance(permission, list):
            query_filter[permission] = permission
        elif permission is not None:
            query_filter["permission"] = permission

        if isinstance(resource_id, list):
            query_filter["resource_id__in"] = resource_id
        elif resource_id is not None:
            query_filter["resource_id"] = resource_id

        if isinstance(namespace, list):
            query_filter["namespace__in"] = namespace
        elif namespace is not None:
            query_filter["namespace"] = namespace

        print(query_filter)
        return self.permission_model.objects(**query_filter)

    def role_permissions(self, role, namespace=None):
        return [{"resource": p.resource, "permission": p.permission} for p in self.permission_model.objects(role=role, namespace=namespace)]

    def resource_permissions(self, resource, resource_id=None, namespace=None):
        return [{"resource": p.resource, "permission": p.permission} for p in self.permission_model.objects(resource=resource, resource_id=resource_id, namespace=namespace)]

    def notify(self, event):
        logging.debug(event)
