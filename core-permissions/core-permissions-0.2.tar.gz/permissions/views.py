from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views.static import serve




def _get_user_documents(user):
    """Utililty method to list all documents that can be accessed by a user.
    A return value of '*' means access to all documents.
    """
    try:
        from humanresources.models import ContractFile
        from humanresources.models import PrivateInfo
        from orders.models import OrderFile
    except:
        pass

    documents = []

    if user.groups.filter(name=settings.PROFILE_HUMAN_RESOURCES).exists():
        return '*'

    person = user.person_user.first()

    # contract files
    contract_files = ContractFile.objects.filter(
        Q(contract__person=person) | Q(contract__supervisor=person))
    contract_files = [obj.contractfile_file.name for obj in contract_files]
    documents += contract_files

    # CV is present both in PrivateInfo and Person tables (!)
    try:
        privateinfo = PrivateInfo.objects.get(person=person)
    except PrivateInfo.DoesNotExist:
        privateinfo_cv = ''
    else:
        privateinfo_cv = privateinfo.privateinfo_cv.name

    cv_files = [privateinfo_cv, person.person_cv.name]
    documents += list(filter(None, cv_files))

    # Orders attachments
    if user.groups.filter(name=settings.APP_PROFILE_ALL_ORDERS).exists():
        order_files = OrderFile.objects.all()
    else:
        order_files = OrderFile.objects.filter(createdby=user)
    documents += list(of.file.name for of in order_files)

    return documents


@login_required
def media_access(request, path, document_root=None):
    """
    Protect all media files by default.

    Add the root of a path to `public_media_paths` to allow to everyone.

    Add the root of a path to `protected_media_paths` to allow check if
    the user has access to it.
    """

    public_media_paths = (
        'cache',
        'uploads/image',
        'uploads/person/person_img',
        'uploads/group/group_img',
        'uploads/publication/publication_file',
    )

    user = request.user

    access_granted = False

    if user.is_superuser or path.startswith(public_media_paths):
        access_granted = True

    else:
        user_documents = _get_user_documents(user)

        if user_documents == '*' or path in user_documents:
            access_granted = True

    if access_granted:
        return serve(request, path, document_root)
    else:
        raise PermissionDenied()