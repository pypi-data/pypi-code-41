from collections import namedtuple


def mock_protected_route(view):
    def view_wrapper(request):
        UserInfo = namedtuple("UserInfo", "user_uuid permissions")

        user_info = UserInfo(
            user_uuid="subject_uuid", permissions="permissions"
        )

        return view(request=request, user_info=user_info)

    return view_wrapper
