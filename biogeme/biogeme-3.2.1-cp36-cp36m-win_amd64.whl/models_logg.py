from biogeme.expressions import *

## \file 
# Implements various models.
# \author Michel Bierlaire
# \date Fri Mar 29 17:13:14 2019

def logit(V,av,i):
    """The logit model \f[ \frac{a_i e^{V_i}}{\sum_{i=1}^J a_j e^{V_j}} \f]

    Args:

       V: dict of objects of type biogeme.expressions.Expression  representing the
    utility functions of each alternative, indexed by numerical ids.

       av: dict of objects of type biogeme.expressions.Expression  representing
    the availability of each alternative (\f$a_i\f$ in the above formula), indexed by numerical ids. Must be consistent with V, or None. In this case, all alternatives are supposed to be always available.

       i: id of the alternative for which the probability must be calculated.

    Return:
       choice probability of alternative number i. 
    """

    if av is None:
        return exp(bioLogLogitFullChoiceSet(V,av=None,choice=i))
    else:
        return exp(bioLogLogit(V,av,i))


def boxcox(x,l):
    """
    Box-Cox transform: \f[ B(x,\ell) = \frac{x^{\ell}-1}{\ell} \f]. It has the property that \f[\lim_{\ell \to 0} B(x,\ell)=\log(x). \f]

    Args:
      x: a variable to transform.
      l: parameter of the transformation.
    
    Return: 
       the Box-Cox transform
    """
    return (x**l-1.0)/l

def piecewise(variable,thresholds):
    """ Generate the variables to include in a piecewise linear specification. If there are K thresholds, K+1 variables are generated. If \f$ t \f$ is the variable of interest, for each interval \f$[a:a+b[\f$ we define a variable defined as:  
\f[
x_{Ti} =
\left\{
  \begin{array}{ll}
 0 & \text{if } t < a \\
 t-a & \text{if } a \leq t < a+b \\
 b  & \text{otherwise}
  \end{array}
\right. \;\;\;x_{Ti} = \max(0,\min(t-a,b)) 
\f]

    Args:
       variable: variable for which we need the piecewise linear transform.
       thresholds: list of thresholds

    Return:
       list of variables to for the piecewise linear specification.
    """
    n = len(thresholds)
    results = [bioMin(variable,thresholds[0])]
    for i in range(0,n-1):
        b = thresholds[i+1]-thresholds[i]
        results += [bioMax(Numeric(0),bioMin(variable - thresholds[i],b))]
    results += [bioMax(0,variable - thresholds[-1])]
    return results
    

def logmev(V,Gi,av,choice) :
    """
     Log of the choice probability for a MEV model.
    
     Args: 
        V: A dictionary mapping each alternative id with the expression of the utility function.
        Gi: A dictionary mapping each alternative id with the function
        \f[
        \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J})
        \f]
        where \f$G\f$ is the MEV generating function. If an alternative \f$i\f$ is not available, then \f$G_i = 0\f$.
      av: A dictionary mapping each alternative id with its availability condition. If None, all alternatives are considered available.
        choice: Object of type biogeme.expressions.Expression  producing the id of the chosen alternative.

    Return:
        Log of the choice probability of the MEV model, given by
  \f[
    V_i + \ln G_i(e^{V_1},\ldots,e^{V_J}) - \log\left(\sum_j e^{V_j + \ln G_j(e^{V_1},\ldots,e^{V_J})}\right)
  \f]
    """
    #    H = {}
    #    for i,v in V.items() :
    #        H[i] =  Elem({0:0, 1: v + log(Gi[i])},av[i]!=0)
    H = {i:v + log(Gi[i]) for i,v in V.items()}
    if av is None:
        logP = bioLogLogitFullChoiceSet(H,av=None,choice=choice)
    else:
        logP = bioLogLogit(H,av,choice)
    return logP



def mev(V,Gi,av,choice) :
    """ Choice probability for a MEV model.
    Args:

      V: A dictionary mapping each alternative id with the expression of the utility function.
      Gi: A dictionary mapping each alternative id with the function
       \f[
          \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J})
      \f]
        where \f$G\f$ is the MEV generating function. If an alternative \f$i\f$ is not available, then \f$G_i = 0\f$.
      av: A dictionary mapping each alternative id with its availability condition. If None, all alternatives are considered available.
      choice: Expression producing the id of the chosen alternative.

    Return:
       Choice probability of the MEV model, given by
        \f[
          \frac{e^{V_i + \ln G_i(e^{V_1},\ldots,e^{V_J})}}{\sum_j e^{V_j + \ln G_j(e^{V_1},\ldots,e^{V_J})}}
        \f]
    """
    #    H = {}
    #    for i,v in V.items() :
    #        H[i] =  Elem({0:0, 1: v + log(Gi[i])},av[i]!=0)
    
    return exp(logmev(V,Gi,av,choice))

def logmev_selectionBias(V,Gi,av,correction,choice) :
    """ Log of choice probability for a MEV model, including the correction for endogenous sampling as proposed by <a href="http://dx.doi.org/10.1016/j.trb.2007.09.003" taret="_blank">Bierlaire, Bolduc and McFadden (2008)</a>.

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
     Gi: A dictionary mapping each alternative id with the function
 \f[
   \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J})
\f]
 where \f$G\f$ is the MEV generating function.
      av: A dictionary mapping each alternative id with its availability condition. If None, all alternatives are considered available.
    correction: A dictionary mapping each alternative id with the expression of the correction. Typically, it is a value, or a parameter to be estimated.

    choice: Expression producing the id of the chosen alternative.

    Return: 
        Log of choice probability of the MEV model, given by
  \f[
    V_i + \ln G_i(e^{V_1},\ldots,e^{V_J}) - \log\left(\sum_j e^{V_j + \ln G_j(e^{V_1},\ldots,e^{V_J})}\right)
  \f]
    """
    H = {i: v + log(Gi[i]) + correction[i] for i,v in V.items()}
    logP = bioLogLogit(H,av,choice)
    return logP



def mev_selectionBias(V,Gi,av,correction,choice) :
    """ Choice probability for a MEV model, including the correction for endogenous sampling as proposed by <a href="http://dx.doi.org/10.1016/j.trb.2007.09.003" taret="_blank">Bierlaire, Bolduc and McFadden (2008)</a>.

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      Gi: A dictionary mapping each alternative id with the function
      \f[
      \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J})
      \f]
      where \f$G\f$ is the MEV generating function.
      av: A dictionary mapping each alternative id with its availability condition. If None, all alternatives are considered available.
      correction: A dictionary mapping each alternative id with the expression of the correction. Typically, it is a value, or a parameter to be estimated.
      choice: Expression producing the id of the chosen alternative.

    Return:
    Choice probability of the MEV model, given by
    \f[
    \frac{e^{V_i + \ln G_i(e^{V_1},\ldots,e^{V_J})}}{\sum_j e^{V_j + \ln G_j(e^{V_1},\ldots,e^{V_J})}}
    \f]
    """
    return exp(logmev_selectionBias(V,Gi,av,correction,choice))


def getMevForNested(V,availability,nests) :
    """ Implements the MEV generating function for the nested logit model
    Args:
      V:  A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition. If None, all alternatices are assumed to be always available.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a list containing the list of identifiers of the alternatives belonging to the nest.
    

    Return:
    A dictionary mapping each alternative id with the function
    \f[
    \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J}) = e^{(\mu_m-1)V_i} \left(\sum_{i=1}^{J_m} e^{\mu_m V_i}\right)^{\frac{1}{\mu_m}-1}
    \f]
    where \f$m\f$ is the (only) nest containing alternative \f$i\f$, and
    \f$G\f$ is the MEV generating function.

    Example:
  nesta = MUA , [1,2,3]
  nestb = MUB , [4,5,6]
  nests = nesta, nestb
    """

    y = {i:exp(v) for i,v in V.items()}
    Gi = {}
    for m in nests:
        sumdict = [Elem({0:0.0,1: y[i] ** m[0]},availability[i]!=0) for i in m[1]]
        sum = bioMultSum(sumdict)
        for i in m[1]:
            Gi[i] = y[i]**(m[0]-1.0) * sum ** (1.0/m[0] - 1.0) 
    return Gi

def nested(V,availability,nests,choice) :
    """ Implements the nested logit model as a MEV model. 
    
    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
         - an object of type biogeme.expressions.Expression  representing the nest parameter,
         - a list containing the list of identifiers of the alternatives belonging to the nest.
      choice: biogeme.expressions.Expression  producing the id of the chosen alternative.


    Return:
       Choice probability for the nested logit model, based on the derivatives of the MEV generating function produced by the function nested::getMevForNested

    Example:
    nesta = MUA , [1,2,3]
    nestb = MUB , [4,5,6]
    nests = nesta, nestb
    """
    Gi = getMevForNested(V,availability,nests)
    P = mev(V,Gi,availability,choice) 
    return P

def lognested(V,availability,nests,choice) :
    """ Implements the log of a nested logit model as a MEV model. 
    
    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
       - an object of type biogeme.expressions.Expression  representing the nest parameter.
       - a list containing the list of identifiers of the alternatives belonging to the nest.
      choice: biogeme.expressions.Expression  producing the id of the chosen alternative.

    Return:
      Log of choice probability for the nested logit model, based on the derivatives of the MEV generating function produced by the function nested::getMevForNested

    Example:
    nesta = MUA , [1,2,3]
    nestb = MUB , [4,5,6]
    nests = nesta, nestb
    """
    Gi = getMevForNested(V,availability,nests)
    logP = logmev(V,Gi,availability,choice) 
    return logP

def nestedMevMu(V,availability,nests,choice,mu) :
    """Implements the nested logit model as a MEV model, where mu is also
    a parameter, if the user wants to test different normalization
    schemes.

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
         - an object of type biogeme.expressions.Expression  representing the nest parameter,
         - a list containing the list of identifiers of the alternatives belonging to the nest.
      choice: expression producing the id of the chosen alternative.
      mu: expression producing the value of the top-level scale parameter.

    Return: 
      The nested logit choice probability based on the following derivatives of the MEV generating function: 
    \f[
    \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J}) = \mu e^{(\mu_m-1)V_i} \left(\sum_{i=1}^{J_m} e^{\mu_m V_i}\right)^{\frac{\mu}{\mu_m}-1}
    \f]
    where \f$m\f$ is the (only) nest containing alternative \f$i\f$, and
    \f$G\f$ is the MEV generating function.
    
    Example:
    nesta = MUA , [1,2,3]
    nestb = MUB , [4,5,6]
    nests = nesta, nestb
    """
    return exp(lognestedMevMu(V,availability,nests,choice,mu))

def _oldnestedMevMu(V,availability,nests,choice,mu) :
    """Implements the nested logit model as a MEV model, where mu is also
    a parameter, if the user wants to test different normalization
    schemes.

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
         - an object of type biogeme.expressions.Expression  representing the nest parameter,
         - a list containing the list of identifiers of the alternatives belonging to the nest.
      choice: expression producing the id of the chosen alternative.
      mu: expression producing the value of the top-level scale parameter.

    Return: 
      The nested logit choice probability based on the following derivatives of the MEV generating function: 
    \f[
    \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J}) = \mu e^{(\mu_m-1)V_i} \left(\sum_{i=1}^{J_m} e^{\mu_m V_i}\right)^{\frac{\mu}{\mu_m}-1}
    \f]
    where \f$m\f$ is the (only) nest containing alternative \f$i\f$, and
    \f$G\f$ is the MEV generating function.
    
    Example:
    nesta = MUA , [1,2,3]
    nestb = MUB , [4,5,6]
    nests = nesta, nestb
    """
    y = {}
    for i,v in V.items() :
        y[i] = exp(v)
    
    Gi = {}
    for m in nests:
        sum = list()
        for i in m[1]:
            sum.append(Elem({0:0,1: y[i] ** m[0]},availability[i]!=0))
        for i in m[1]:
            Gi[i] = Elem({0:0,1:mu * y[i]**(m[0]-1.0) * bioMultSum(sum) ** (mu/m[0] - 1.0)},availability[i]!=0)
    P = mev(V,Gi,availability,choice) 
    return P

def lognestedMevMu(V,availability,nests,choice,mu) :
    """ Implements the log of the nested logit model as a MEV model, where mu is also a parameter, if the user wants to test different normalization schemes.

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
        - an object of type biogeme.expressions.Expression  representing the nest parameter,
        - a list containing the list of identifiers of the alternatives belonging to the nest.
      choice: expression producing the id of the chosen alternative.
      mu: expression producing the value of the top-level scale parameter.

    Return: 
      The nested logit choice probability based on the following derivatives of the MEV generating function: 
    \f[
    \frac{\partial G}{\partial y_i}(e^{V_1},\ldots,e^{V_J}) = \mu e^{(\mu_m-1)V_i} \left(\sum_{i=1}^{J_m} e^{\mu_m V_i}\right)^{\frac{\mu}{\mu_m}-1}
    \f]
    where \f$m\f$ is the (only) nest containing alternative \f$i\f$, and
    \f$G\f$ is the MEV generating function.
    """
    
    y = {i:exp(v) for i,v in V.items()}
    Gi = {}
    for m in nests:
        sum = [Elem({0:0,1: y[i] ** m[0]},availability[i]!=0) for i in m[1]]
        for i in m[1]:
            Gi[i] = mu * y[i]**(m[0]-1.0) * bioMultSum(sum) ** (mu/m[0] - 1.0)
    logP = logmev(V,Gi,availability,choice) 
    return logP


def cnl_avail(V,availability,nests,choice):
    """ Implements the cross-nested logit model as a MEV model. 
    Args:
       V: A dictionary mapping each alternative id with the expression of the utility function.
       availability: A dictionary mapping each alternative id with its availability condition.
       nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
          - an object of type biogeme.expressions.Expression  representing the nest parameter,
          - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 
       choice: an object of type biogeme.expressions.Expression  characterizing the chosne alternative.

    Return: 
        Choice probability for the cross-nested logit model.

    Example:
    alphaA = {1: alpha1a,2: alpha2a, 3: alpha3a, 4: alpha4a,5: alpha5a, 6: alpha6a}
    alphaB = {1: alpha1b,2: alpha2b, 3: alpha3b, 4: alpha4b,5: alpha5b, 6: alpha6b}
    nesta = MUA , alphaA
    nestb = MUB , alphaB
    nests = nesta, nestb
    """
    Gi = {}
    Gidict = {}
    for k in V:
        Gidict[k] = list()
    for m in nests:
        biosumlist = list()
        for i,a in m[1].items():
            biosumlist.append(Elem({0:0,1:a**(m[0]) * exp(m[0] * (V[i]))},availability[i] != 0))
        biosum = bioMultSum(biosumlist)        
        for i,a in m[1].items():
            Gidict[i].append(Elem({0:0,1:(biosum**((1.0/m[0])-1.0)) * (a**m[0]) * exp((m[0]-1.0)*(V[i]))},availability[i] != 0))
    for k in V:
        Gi[k] = bioMultSum(Gidict[k])
    P = mev(V,Gi,availability,choice) 
    return P


def logcnl_avail(V,availability,nests,choice) :
    """ Implements the log of the cross-nested logit model as a MEV model. 
    
    Args:
     V: A dictionary mapping each alternative id with the expression of the utility function.
     availability: A dictionary mapping each alternative id with its availability condition.
     nests: A tuple containing as many items as nests. Each item is also a tuple
    containing two items:
       - an object of type biogeme.expressions.Expression  representing the nest parameter,
       - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 
      choice: Expression producing the id of the chosen alternative.

    Return: 
      Choice probability for the cross-nested logit model.

    Example:
alphaA = {1: alpha1a,
          2: alpha2a,
          3: alpha3a,
          4: alpha4a,
          5: alpha5a,
          6: alpha6a}
alphaB = {1: alpha1b,
          2: alpha2b,
          3: alpha3b,
          4: alpha4b,
          5: alpha5b,
          6: alpha6b}
nesta = MUA , alphaA
nestb = MUB , alphaB
nests = nesta, nestb
    """
    Gi = {}
    Gidict = {}
    for k in V:
        Gidict[k] = list()
    for m in nests:
        biosumlist = list()
        for i,a in m[1].items():
            biosumlist.append(Elem({0:0,1:a**(m[0]) * exp(m[0] * (V[i]))},availability[i] != 0))
        biosum = bioMultSum(biosumlist)
        for i,a in m[1].items():
            Gidict[i].append(Elem({0:0,1:(biosum**((1.0/m[0])-1.0)) * (a**m[0]) * exp((m[0]-1.0)*(V[i]))},availability[i] != 0))
    for k in V:
        Gi[k] = bioMultSum(Gidict[k])
    logP = logmev(V,Gi,availability,choice) 
    return logP


def cnlmu(V,availability,nests,choice,bmu) :
    """ Implements the cross-nested logit model as a MEV model with the homogeneity parameters is explicitly involved

    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
        - an object of type biogeme.expressions.Expression  representing the nest parameter.
        - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 
      choice: Expression producing the id of the chosen alternative.
      bmu: Homogeneity parameter \f$\mu\f$.

    Return: 
      Choice probability for the cross-nested logit model.

    Example:
    alphaA = {1: alpha1a,
          2: alpha2a,
          3: alpha3a,
          4: alpha4a,
          5: alpha5a,
          6: alpha6a}
    alphaB = {1: alpha1b,
          2: alpha2b,
          3: alpha3b,
          4: alpha4b,
          5: alpha5b,
          6: alpha6b}
    nesta = MUA , alphaA
    nestb = MUB , alphaB
    nests = nesta, nestb
    """
    Gi = {}
    Gidict = {}
    for k in V:
        Gilist[k] = list()
    for m in nests:
        biosumlist = list()
        for i,a in m[1].items():
            biosumlist.append(Elem({0:0,1:a**(m[0]/bmu) * exp(m[0] * (V[i]))},availability[i] != 0))
        biosum = bioMultSum(biosumlist)
        for i,a in m[1].items():
            Gilist[i].append(Elem({0:0,1:bmu * (biosum**((bmu/m[0])-1.0)) * (a**(m[0]/bmu)) * exp((m[0]-1.0)*(V[i]))},availability[i] != 0))
    for k in V:
        Gi[k] = bioMultSum(Gilist[k])
    P = mev(V,Gi,availability,choice) 
    return P

def logcnlmu(V,availability,nests,choice,bmu) :
    """ Implements the log of the cross-nested logit model as a MEV model with the homogeneity parameters is explicitly involved.
    Args:
      V: A dictionary mapping each alternative id with the expression of the utility function.
      availability: A dictionary mapping each alternative id with its availability condition.
      nests: A tuple containing as many items as nests. Each item is also a tuple containing two items
        - an object of type biogeme.expressions.Expression representing the nest parameter,
        - a dictionary mapping the alternative ids with the cross-nested parameters for the corresponding nest. 
    choice: Expression producing the id of the chosen alternative.
    bmu: Homogeneity parameter \f$\mu\f$.

    Return:
      Log of choice probability for the cross-nested logit model.

    Example:
    alphaA = {1: alpha1a,
          2: alpha2a,
          3: alpha3a,
          4: alpha4a,
          5: alpha5a,
          6: alpha6a}
    alphaB = {1: alpha1b,
          2: alpha2b,
          3: alpha3b,
          4: alpha4b,
          5: alpha5b,
          6: alpha6b}
    nesta = MUA , alphaA
    nestb = MUB , alphaB
    nests = nesta, nestb
"""
    Gi = {}
    Gidict = {}
    for k in V:
        Gidict[k] = list()
    for m in nests:
        biosumlist = list() 
        for i,a in m[1].items():
            biosumlist.append(Elem({0:0,1:a**(m[0]/bmu) * exp(m[0] * (V[i]))},availability[i] != 0))
        biosum = bioMultSum(biosumlist)
        for i,a in m[1].items():
            Gidict[i].append(Elem({0:0,1:bmu * (biosum**((bmu/m[0])-1.0)) * (a**(m[0]/bmu)) * exp((m[0]-1.0)*(V[i]))},availability[i] != 0))
    for k in V:
        Gi[k] = bioMultSum(Gidict[k])
    logP = logmev(V,Gi,availability,choice) 
    return logP

