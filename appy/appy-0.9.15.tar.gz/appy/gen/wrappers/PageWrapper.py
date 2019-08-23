# ------------------------------------------------------------------------------
from appy.gen import Show
from appy.gen.wrappers import AbstractWrapper

# ------------------------------------------------------------------------------
EXPRESSION_ERROR = 'error while evaluating page expression: %s'

# ------------------------------------------------------------------------------
class PageWrapper(AbstractWrapper):

    def validate(self, new, errors):
        '''Inter-field validation.'''
        return self._callCustom('validate', new, errors)

    def showSubPages(self):
        '''Show the sub-pages.'''
        if self.user.hasRole('Manager'): return 'view'

    def showPortlet(self):
        '''Do not show the portlet for a page'''
        return

    def showExpression(self):
        '''Show the expression to managers only'''
        # Do not show it on "view" if empty
        if self.isEmpty('expression'): return Show.V_
        return self.user.hasRole('Manager')

    def mayView(self):
        '''In addition to the workflow, evaluating p_self.expression, if
           defined, determines p_self's visibility.'''
        expression = self.expression
        if not expression: return True
        user = self.user
        try:
            return eval(expression)
        except Exception, err:
            self.log(EXPRESSION_ERROR % str(err), type='error')
            return

    def onEdit(self, created):
        return self._callCustom('onEdit', created)
# ------------------------------------------------------------------------------
