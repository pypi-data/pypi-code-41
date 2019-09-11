""" Implements various models.

:author: Michel Bierlaire
:date: Fri Mar 29 17:13:14 2019
"""

from biogeme.expressions import *

def logit(V,av,i):
    """The logit model 

    The model is defined as 
    
    .. math:: \\frac{a_i e^{V_i}}{\\sum_{i=1}^J a_j e^{V_j}}

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param av: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type av: dict(int:biogeme.expressions.Expression)

    :param i: id of the alternative for which the probability must be
              calculated.
    :type i: int

    :return: choice probability of alternative number i.
    :rtype: biogeme.expressions.Expression

    """
    if av is None:
        return exp(bioLogLogitFullChoiceSet(V,av=None,choice=i))
    else:
        return exp(bioLogLogit(V,av,i))


def boxcox(x,l):
    """Box-Cox transform 

    .. math:: B(x,\\ell) = \\frac{x^{\\ell}-1}{\\ell}. 

    It has the property that 

    .. math:: \\lim_{\\ell \\to 0} B(x,\\ell)=\\log(x).

    :param x: a variable to transform.
    :type x: biogeme.expressions.Expression
    :param l: parameter of the transformation.
    :type l: biogeme.expressions.Expression
    
    :return: the Box-Cox transform
    :rtype: biogeme.expressions.Expression
    """
    return (x**l-1.0)/l

def piecewise(variable,thresholds):
    """Generate the variables to include in a piecewise linear specification.

    If there are K thresholds, K+1 variables are generated. If :math:`t`
    is the variable of interest, for each interval :math:`[a:a+b[`, we define a variable defined as:
  
    .. math:: x_{Ti} =\\left\\{  \\begin{array}{ll} 0 & \\text{if } t < a \\\\ t-a & \\text{if } a \\leq t < a+b \\\\ b  & \\text{otherwise}  \\end{array}\\right. \\;\\;\\;x_{Ti} = \\max(0,\\min(t-a,b)) 

    :param variable: variable for which we need the piecewise linear
       transform.  
    :type variable: biogeme.expressions.Expression

    :param thresholds: list of thresholds
    :type thresholds: list(float)

    :return: list of variables to for the piecewise linear specification.
    :rtype: list(biogeme.expressions.Expression)

    """
    n = len(thresholds)
    results = [bioMin(variable,thresholds[0])]
    for i in range(0,n-1):
        b = thresholds[i+1]-thresholds[i]
        results += [bioMax(Numeric(0),bioMin(variable - thresholds[i],b))]
    results += [bioMax(0,variable - thresholds[-1])]
    return results
    

def logmev(V,logGi,av,choice) :
    """ Log of the choice probability for a MEV model.
    
    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param logGi: a dictionary mapping each alternative id with the function

    .. math:: \\ln \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J})
        
    where :math:`G` is the MEV generating function. If an alternative :math:`i` is not available, then :math:`G_i = 0`.

    :type logGi: dict(int:biogeme.expressions.Expression)

    :param av: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type av: dict(int:biogeme.expressions.Expression)

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of the choice probability of the MEV model, given by
    
    .. math:: V_i + \\ln G_i(e^{V_1},\\ldots,e^{V_J}) - \\ln\\left(\\sum_j e^{V_j + \\ln G_j(e^{V_1},\\ldots,e^{V_J})}\\right)

    """
    H = {i:v + logGi[i] for i,v in V.items()}
    if av is None:
        logP = bioLogLogitFullChoiceSet(H,av=None,choice=choice)
    else:
        logP = bioLogLogit(H,av,choice)
    return logP

def mev(V,logGi,av,choice) :
    """ Choice probability for a MEV model.

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)


    :param logGi: a dictionary mapping each alternative id with the function

    .. math:: \\ln \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J})
        
    where :math:`G` is the MEV generating function. If an alternative :math:`i` is not available, then :math:`G_i = 0`.

    :param av: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type av: dict(int:biogeme.expressions.Expression)

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: Choice probability of the MEV model, given by

    .. math:: \\frac{e^{V_i + \\ln G_i(e^{V_1},\\ldots,e^{V_J})}}{\\sum_j e^{V_j + \\ln G_j(e^{V_1},\\ldots,e^{V_J})}}

    """
    return exp(logmev(V,logGi,av,choice))

def logmev_selectionBias(V,logGi,av,correction,choice) :
    """Log of choice probability for a MEV model, including the correction for endogenous sampling as proposed by `Bierlaire, Bolduc and McFadden (2008)`_.

    .. _`Bierlaire, Bolduc and McFadden (2008)`: http://dx.doi.org/10.1016/j.trb.2007.09.003

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.


    :param logGi: a dictionary mapping each alternative id with the function

    .. math:: \\ln \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J})
        
    where :math:`G` is the MEV generating function. If an alternative :math:`i` is not available, then :math:`G_i = 0`.

    :type logGi: dict(int:biogeme.expressions.Expression)

    :param av: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type av: dict(int:biogeme.expressions.Expression)

    
    :param correction: a dict of expressions for the correstion terms
                       of each alternative.
    :type correction: dict(int:biogeme.expressions.Expression)

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of the choice probability of the MEV model, given by

    .. math:: V_i + \\ln G_i(e^{V_1},\\ldots,e^{V_J}) + \\omega_i - \\ln\\left(\\sum_j e^{V_j + \\ln G_j(e^{V_1},\\ldots,e^{V_J})+ \\omega_j}\\right)

    where :math:`\\omega_i` is the correction term for alternative :math:`i`.
    """
    H = {i: v + logGi[i] + correction[i] for i,v in V.items()}
    logP = bioLogLogit(H,av,choice)
    return logP



def mev_selectionBias(V,logGi,av,correction,choice) :
    """Choice probability for a MEV model, including the correction for endogenous sampling as proposed by `Bierlaire, Bolduc and McFadden (2008)`_.

    .. _`Bierlaire, Bolduc and McFadden (2008)`: http://dx.doi.org/10.1016/j.trb.2007.09.003

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.


    :param logGi: a dictionary mapping each alternative id with the function

    .. math:: \\ln \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J})
        
    where :math:`G` is the MEV generating function. If an alternative :math:`i` is not available, then :math:`G_i = 0`.

    :type logGi: dict(int:biogeme.expressions.Expression)

    :param av: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type av: dict(int:biogeme.expressions.Expression)

    
    :param correction: a dict of expressions for the correstion terms
                       of each alternative.
    :type correction: dict(int:biogeme.expressions.Expression)

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of the choice probability of the MEV model, given by

    .. math:: V_i + \\ln G_i(e^{V_1},\\ldots,e^{V_J}) + \\omega_i - \\ln\\left(\\sum_j e^{V_j + \\ln G_j(e^{V_1},\\ldots,e^{V_J})+ \\omega_j}\\right)

    where :math:`\\omega_i` is the correction term for alternative :math:`i`.
    """
    return exp(logmev_selectionBias(V,logGi,av,correction,choice))


def getMevForNested(V,availability,nests) :
    """ Implements the MEV generating function for the nested logit model

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: A tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.

      Example::

          nesta = MUA , [1,2,3]
          nestb = MUB , [4,5,6]
          nests = nesta, nestb


    
    :type nests: tuple

    :return: a dictionary mapping each alternative id with the function

    .. math:: \\ln \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J}) = e^{(\\mu_m-1)V_i} \\left(\\sum_{i=1}^{J_m} e^{\\mu_m V_i}\\right)^{\\frac{1}{\\mu_m}-1}
    
    where :math:`m` is the (only) nest containing alternative :math:`i`, and :math:`G` is the MEV generating function.

    :rtype: dict(int:biogeme.expressions.Expression)

    """

    #y = {i:exp(v) for i,v in V.items()}
    logGi = {}
    for m in nests:
        if availability is None:
            sumdict = [exp(m[0] * V[i]) for i in m[1]]
        else:
            sumdict = [Elem({0:0.0,1: exp(m[0] * V[i])},availability[i]!=0) for i in m[1]]
        sum = bioMultSum(sumdict)
        for i in m[1]:
            logGi[i] = (m[0]-1.0) * V[i] + (1.0/m[0] - 1.0) * log(sum) 
    return logGi

def nested(V,availability,nests,choice) :
    """ Implements the nested logit model as a MEV model. 
    
    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: A tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.

      Example::

          nesta = MUA , [1,2,3]
          nestb = MUB , [4,5,6]
          nests = nesta, nestb


    
    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: choice probability for the nested logit model,
             based on the derivatives of the MEV generating function produced
             by the function getMevForNested
    """
    logGi = getMevForNested(V,availability,nests)
    P = mev(V,logGi,availability,choice) 
    return P

def lognested(V,availability,nests,choice) :
    """Implements the log of a nested logit model as a MEV model. 
    
    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: A tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.

      Example::

          nesta = MUA , [1,2,3]
          nestb = MUB , [4,5,6]
          nests = nesta, nestb


    
    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of choice probability for the nested logit model,
             based on the derivatives of the MEV generating function produced
             by the function getMevForNested

    """
    logGi = getMevForNested(V,availability,nests)
    logP = logmev(V,logGi,availability,choice) 
    return logP

def nestedMevMu(V,availability,nests,choice,mu) :
    """Implements the nested logit model as a MEV model, where mu is also
    a parameter, if the user wants to test different normalization
    schemes.
 
    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: A tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.

      Example::

          nesta = MUA , [1,2,3]
          nestb = MUB , [4,5,6]
          nests = nesta, nestb
    
    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :param mu: expression producing the value of the top-level scale parameter.
    :type mu:  biogeme.expressions.Expression

    :return: the nested logit choice probability based on the following derivatives of the MEV generating function: 

    .. math:: \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J}) = \\mu e^{(\\mu_m-1)V_i} \\left(\\sum_{i=1}^{J_m} e^{\\mu_m V_i}\\right)^{\\frac{\\mu}{\\mu_m}-1}

    where :math:`m` is the (only) nest containing alternative :math:`i`, and
    :math:`G` is the MEV generating function.

    :rtype: biogeme.expressions.Expression
    """
    return exp(lognestedMevMu(V,availability,nests,choice,mu))

def lognestedMevMu(V,availability,nests,choice,mu) :
    """ Implements the log of the nested logit model as a MEV model, where mu is also a parameter, if the user wants to test different normalization schemes.


    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.

    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative (:math:`a_i` in the above formula), indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: A tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.

      Example::

          nesta = MUA , [1,2,3]
          nestb = MUB , [4,5,6]
          nests = nesta, nestb
    
    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :param mu: expression producing the value of the top-level scale parameter.
    :type mu:  biogeme.expressions.Expression

    :return: the log of the nested logit choice probability based on the following derivatives of the MEV generating function: 

    .. math:: \\frac{\\partial G}{\\partial y_i}(e^{V_1},\\ldots,e^{V_J}) = \\mu e^{(\\mu_m-1)V_i} \\left(\\sum_{i=1}^{J_m} e^{\\mu_m V_i}\\right)^{\\frac{\\mu}{\\mu_m}-1}

    where :math:`m` is the (only) nest containing alternative :math:`i`, and
    :math:`G` is the MEV generating function.

    :rtype: biogeme.expressions.Expression
    """
    
    y = {i:exp(v) for i,v in V.items()}
    logGi = {}
    for m in nests:
        sum = [Elem({0:0,1: y[i] ** m[0]},availability[i]!=0) for i in m[1]]
        for i in m[1]:
            logGi[i] = log(mu) + (m[0]-1.0) * V[i] + (mu/m[0] - 1.0) * log(bioMultSum(sum))
    logP = logmev(V,logGi,availability,choice) 
    return logP

def cnl_avail(V,availability,nests,choice):
    """ Same as cnl. Maintained for backward compatibility

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression
    """
    return cnl(V,availability,nests,choice)

def cnl(V,availability,nests,choice):
    """ Implements the cross-nested logit model as a MEV model. 

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type available: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression
    

    """
    return exp(logcnl(V,availability,nests,choice))

def logcnl_avail(V,availability,nests,choice) :
    """ Same as logcnl. Maintained for backward compatibility

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression
    """
    return logcnl(V,availability,nests,choice)

def logcnl(V,availability,nests,choice) :
    """ Implements the log of the cross-nested logit model as a MEV model. 
    
    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :return: log of the choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression

    """
    Gi_terms = {}
    logGi = {}
    for i in V:
        Gi_terms[i] = list()
    biosum = {}
    for m in nests:
        biosum = bioMultSum([availability[i] * a**(m[0]) * exp(m[0] * (V[i])) for i,a in m[1].items()])
        for i,a in m[1].items():
            Gi_terms[i] += [a**(m[0])* exp((m[0]-1) * (V[i])) * biosum **((1.0/m[0])-1.0)]  
    for k in V:
        logGi[k] = log(bioMultSum(Gi_terms[k]))
    logP = logmev(V,logGi,availability,choice) 
    return logP


def cnlmu(V,availability,nests,choice,bmu) :
    """ Implements the cross-nested logit model as a MEV model with the homogeneity parameters is explicitly involved

    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :param bmu: Homogeneity parameter :math:`\\mu`.
    :type bmu: biogeme.expressions.Expression
    
    :return: choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression
    """
    return exp(logcnlmu(V,availability,nests,choice,bmu))

def logcnlmu(V,availability,nests,choice,bmu) :
    """ Implements the log of the cross-nested logit model as a MEV model with the homogeneity parameters is explicitly involved.


    :param V: dict of objects representing the utility functions of
              each alternative, indexed by numerical ids.
    :type V: dict(int:biogeme.expressions.Expression)

    :param availability: dict of objects representing the availability of each
               alternative, indexed
               by numerical ids. Must be consistent with V, or
               None. In this case, all alternatives are supposed to be
               always available.

    :type availability: dict(int:biogeme.expressions.Expression)

    :param nests: a tuple containing as many items as nests. Each item is also a tuple containing two items

          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 

        Example::

            alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
            alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
            nesta = MUA , alphaA
            nestb = MUB , alphaB
            nests = nesta, nestb

    :type nests: tuple

    :param choice: id of the alternative for which the probability must be
              calculated.
    :type choice: biogeme.expressions.Expression

    :param bmu: Homogeneity parameter :math:`\\mu`.
    :type bmu: biogeme.expressions.Expression
    
    :return: log of the choice probability for the cross-nested logit model.
    :rtype: biogeme.expressions.Expression

    """
    Gi_terms = {}
    logGi = {}
    for i in V:
        Gi_terms[i] = list()
    biosum = {}
    for m in nests:
        biosum = bioMultSum([availability[i] * a**(m[0]/bmu) * exp(m[0] * (V[i])) for i,a in m[1].items()])
        for i,a in m[1].items():
            Gi_terms[i] += [a**(m[0]/bmu)* exp((m[0]-1) * (V[i])) * biosum **((bmu/m[0])-1.0)]  
    for k in V:
        logGi[k] = log(bmu * bioMultSum(Gi_terms[k]))
    logP = logmev(V,logGi,availability,choice) 
    return logP


def bioNormalPdf(x):
    """pdf of the normal distribution N(0,1)

    .. math:: \\frac{1}{\\sqrt{2\\pi}} e^{\\frac{-x^2}{2}}

    :param x: argument of the function
    :type x: biogeme.expressions.Expression
    
    :return: value of the pdf
    :rtype: biogeme.expressions.Expression
    """
    invSqrtTwoPi = 0.3989422804
    return exp(-x*x/2.0) * invSqrtTwoPi
