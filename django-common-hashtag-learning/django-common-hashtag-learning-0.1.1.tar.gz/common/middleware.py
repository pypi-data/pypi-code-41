from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse


"""
Middleware to test if the user account has expired
Need to check they are not anonymous (i.e. not logged in) - by returning response this will automatically return to
    login
Need to check they are not staff - staff should never expire, or admin
If the user is none of the above, compare the dates and if the expiry date is in the past call account-expired
"""
class AccountExpiry:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_user = request.user
        response = self.get_response(request)
        expiry_path = reverse('schools:account-expired')
        logout_path = reverse('account_logout')

        if current_user.is_anonymous is False:
            if current_user.is_superuser is False and current_user.is_staff is False and current_user.school is not None:

                # use this to ensure we don't end up in a continual loop of redirects
                if request.path not in [expiry_path, logout_path]:
                    expiry_date = current_user.school.account_expiry
                    todays_date = datetime.today().date()
                    if todays_date > expiry_date:
                        return HttpResponseRedirect(expiry_path)
        return response
