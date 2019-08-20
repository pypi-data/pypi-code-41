from pyforms_web.basewidget import BaseWidget


class ExternalLinkBaseWidget(BaseWidget):
    ORQUESTRA_MENU = 'bottom-left'
    ORQUESTRA_MENU_ORDER = 900
    ORQUESTRA_MENU_ICON = 'external alternate'



class PermissionMixin:

    @classmethod
    def has_permissions(cls, user):
        return (
            super().has_permissions(user) and
            (
                user.has_perm('finance.add_order') or
                user.has_perm('finance.change_order')
            )
        )


class WikiLink(ExternalLinkBaseWidget):
    UID = 'wiki-link'
    TITLE = 'Wiki'

    ORQUESTRA_URL = 'http://wiki.neuro.fchampalimaud.org'
    ORQUESTRA_TARGET = '_blank'


class RequisitionsLink(PermissionMixin, ExternalLinkBaseWidget):
    UID = 'requisition-link'
    TITLE = 'Requisition system'

    ORQUESTRA_URL = 'http://intranet.champalimaud.pt/ServicosPartilhados/RequisicoesDEV/SitePages/Inicio.asp'
    ORQUESTRA_TARGET = '_blank'


class QlikViewLink(PermissionMixin, ExternalLinkBaseWidget):
    UID = 'qlikview-link'
    TITLE = 'QlikView'

    ORQUESTRA_URL = 'http://pkpfch31.champalimaud.pt/QvAJAXZfc/opendoc.htm?document=Producao/GL_PRJ/FCH_Projectos_PRD_GL.qvw&host=QVS@pkpfch31'
    ORQUESTRA_TARGET = '_blank'


class NexBittLink(PermissionMixin, ExternalLinkBaseWidget):
    UID = 'nextbitt-link'
    TITLE = 'NexBitt'

    ORQUESTRA_URL = 'https://fch.nextbitt.net/account/login'
    ORQUESTRA_TARGET = '_blank'


class iLabLink(ExternalLinkBaseWidget):
    UID = 'ilab-link'
    TITLE = 'iLab'

    ORQUESTRA_URL = 'https://champalimaud.ilabsolutions.com/account/login'
    ORQUESTRA_TARGET = '_blank'


class FundingOpportunitiesLink(ExternalLinkBaseWidget):
    UID = 'funding-link'
    TITLE = 'Funding Opportunities'

    ORQUESTRA_URL = 'https://funding.fchampalimaud.org/'
    ORQUESTRA_TARGET = '_blank'
