from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Meta Lists"
    site_header = "Meta Lists"
    index_title = "Meta Lists"
    site_url = "/administration/"


meta_lists_admin = AdminSite(name="meta_lists_admin")
meta_lists_admin.disable_action("delete_selected")
