from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Meta PRN"
    site_header = "Meta PRN"
    index_title = "Meta PRN"
    site_url = "/administration/"


meta_prn_admin = AdminSite(name="meta_prn_admin")
meta_prn_admin.disable_action("delete_selected")
