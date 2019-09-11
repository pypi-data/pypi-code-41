"""
Interface for the optimization algorithms.

:author: Michel Bierlaire
:date: Fri Aug 16 11:31:43 2019

:note:  An optimization algorithm takes as input:

 - a function taking three arguments:

       - x: the vector of parameters
       - hessian: a boolean specifying if the hessian must be calculated
       - bhhh: a boolean specifying if the BHHH matrix must be calculated
       - batchSize: if not None, the percentage of the data that must be sampled to obtain a stochastic version of the derivatives,

   and returning f,g,h,bhhh. It characterizes the function to *maximize*;

 - a vector a starting values for the betas to be estimated,
 - a vector of values for the fixed betas,
 - a list of IDs of the betas to be estimated,
 - lower and upper bounds,
 - algorithm specific parameters.

It returns:

 - the optimal solution,
 - the number of iterations,
 - the number of function evaluations,
 - a diagnostic.
"""
import numpy as np
import biogeme.exceptions as excep
import scipy.optimize as sc
import scipy.linalg as la
import inspect as ip
import biogeme.messaging as msg

logger = msg.bioMessage()


def scipy(fct,initBetas,fixedBetas,betaIds,bounds,parameters=None):
    """Optimization interface for Biogeme, based on the scipy minimize function.

    :param fct: a function taking four arguments:

              - x, the vector of parameters;
              - hessian, a boolean specifying if the hessian must be calculated;
              - bhhh, a boolean specifying if the BHHH matrix must be calculated:
              - batchSize, if not None, the percentage of the data that must
                be sampled to obtain a stochastic version of the derivatives,

            and returning f,g,h,bhhh. It characterizes the function to *maximize*.
    :type fct: function

    :param initBetas: initial value of the parameters
    :type initBetas: numpy.array
    :param fixedBetas: betas that stay fixed suring the optimization
    :type fixedBetas: numpy.array
    :param betaIds: internal identifiers of the non fixed betas
    :type betaIds: numpy.array
    :param bounds: list of tuples (ell,u) containing the lower and upper bounds
          for each free parameter
    :type bounds: list(tuple)
    :param parameters: dict of parameters to be transmitted to the 
         optimization routine.
    :type parameters: dict(string:float or string)

    :return: tuple x,nit,nfev,message, where x is the solution found,
              nit is the number of iterations performed, nfev is the
              number of time that the objective function has been
              evaluated, and message is the diagnostic provided by the
              algorithm.
    :rtype: numpay.array,int,int,string


    """
    def f_and_grad(x):
        f,g,h,b = fct(x,hessian=False,bhhh=False)
        return -f,-np.asarray(g)

    # Absolute tolerance
    absgtol = 1e-7
    opts = {'ftol' : np.finfo(np.float64).eps}
    opts['gtol'] = absgtol * max(abs(1000.0),1)
    if parameters is not None:
        opts = {**opts,**parameters}

    logger.general(f"Minimize with tol {opts['gtol']}")
    results =  sc.minimize(f_and_grad,initBetas,bounds=bounds,jac=True,options=opts)
    return results.x, results.nit,results.nfev,results.message


def schnabelEskow(A,tau=np.finfo(np.float64).eps**0.3333,taubar=np.finfo(np.float64).eps**0.6666,mu=0.1):

    """Modified Cholesky factorization by `Schnabel and Eskow (1999)`_.

    .. _`Schnabel and Eskow (1999)`: https://doi.org/10.1137/s105262349833266x

    If the matrix is 'safely' positive definite, the output is the
    classical Cholesky factor. If not, the diagonal elements are
    inflated in order to make it positive definite. The factor :math:`L`
    is such that :math:`A + E = PLL^TP^T`, where :math:`E` is a diagonal
    matrix contaninig the terms added to the diagonal, :math:`P` is a
    permutation matrix, and :math:`L` is w lower triangular matrix.

    :param A: matrix to factorize. Must be square and symmetric.
    :type A: numpy.array
    :param tau: tolerance factor. Default: :math:`\\varepsilon^{\\frac{1}{3}}`. See `Schnabel and Eskow (1999)`_
    :type tau: float
    :param taubar: tolerance factor. Default: :math:`\\varepsilon^{\\frac{2}{3}}`. See `Schnabel and Eskow (1999)`_
    :type taubar: float
    :param mu: tolerance factor. Default: 0.1.  See `Schnabel and Eskow (1999)`_
    :type mu: float

    :return: tuple :math:`L`, :math:`E`, :math:`P`, where :math:`A + E = PLL^TP^T`.
    :rtype: numpy.array, numpy.array, numpy.array

    """
    def pivot(j):
        A[j, j] = np.sqrt(A[j, j])
        for i in range(j+1, dim):
            A[j, i] = A[i, j] = A[i, j] / A[j, j]
            A[i, j+1:i+1] -= A[i, j]*A[j+1:i+1, j]
            A[j+1:i+1, i] = A[i, j+1:i+1] 

    def permute(i,j):
        A[[i,j]] = A[[j,i]]
        E[[i,j]] = E[[j,i]]
        A[:,[i,j]] = A[:,[j,i]]
        P[:,[i,j]] = P[:,[j,i]]
        
    A = A.astype(np.float64)    
    dim = A.shape[0]
    if A.shape[1] != dim:
        raise excep.biogemeError("The matrix must be square")

    if not np.all(np.abs(A-A.T) < np.sqrt(np.finfo(np.float64).eps)):
        raise excep.biogemeError("The matrix must be symmetric")
    
    E = np.zeros(dim,dtype=np.float64)
    P = I = np.identity(dim)
    phaseOne = True
    gamma = abs(A.diagonal()).max()
    j = 0
    while j < dim and phaseOne is True:
        a_max = A.diagonal()[j:].max()
        a_min = A.diagonal()[j:].min()
        if (a_max < taubar*gamma or a_min < -mu*a_max):
            phaseOne = False
            break
        else:
            # Pivot on maximum diagonal of remaining submatrix
            i = j + np.argmax(A.diagonal()[j:])
            if i != j:
                # Switch rows and columns of i and j of A
                permute(i,j)
            if j < dim-1 and ((A.diagonal()[j+1:] - A[j+1:,j]**2/A.diagonal()[j]).min() < -mu*gamma):
                phaseOne = False # go to phase two
            else:
                # perform jth iteration of factorization
                pivot(j)
                j += 1

    # Phase two, A not positive-definite
    if not phaseOne:
        if j == dim - 1:
            E[-1] = delta = -A[-1,-1] + max(tau*(-A[-1,-1])/(1-tau), taubar*gamma)
            A[-1,-1] += delta
            A[-1,-1] = np.sqrt(A[-1,-1])
        else:
            deltaPrev = 0.0
            g = np.zeros(dim)
            k = j - 1  # k = number of iterations performed in phase one;
            # Calculate lower Gerschgorin bounds of A[k+1]
            for i in range(k + 1, dim):
                g[i] = A[i,i] - abs(A[i,k+1:i]).sum() - abs(A[i+1:dim,i]).sum()
            # Modified Cholesky Decomposition
            for j in range(k + 1, dim - 2):
                # Pivot on maximum lower Gerschgorin bound estimate
                i = j + np.argmax(g[j:])
                if i != j:
                    # Switch rows and columns of i and j of A
                    permute(i,j)
                # Calculate E[j,j] and add to diagonal
                norm_j = abs(A[j+1:dim,j]).sum()
                E[j] = delta = max(0,
                                   -A[j,j] + max(norm_j, taubar*gamma),
                                   deltaPrev)
                if delta > 0:
                    A[j,j] += delta
                    deltaPrev = delta         # deltaPrev will contain E_inf
                # Update Gerschgorin bound estimates
                if A[j,j] != norm_j:
                    temp = 1.0 - norm_j/A[j,j]
                    g[j+1:] += abs(A[j+1:,j])*temp
                # perform jth iteration of factorization
                pivot(j)

            # Final 2 by 2 submatrix
            e = np.linalg.eigvalsh(A[-2:,-2:])
            e.sort()
            E[-2] = E[-1] = delta = max(0,
                        -e[0] + max(tau*(e[1] - e[0])/(1 - tau),
                                    taubar*gamma),
                        deltaPrev)
            if delta > 0:
                A[-2,-2] += delta
                A[-1,-1] += delta
                deltaPrev = delta
            A[-2,-2] = np.sqrt(A[-2,-2])    # overwrites A[-2,-2]
            A[-1,-2] = A[-1,-2]/A[-2,-2]   # overwrites A[-1,-2]
            A[-2,-1] = A[-1,-2]
            A[-1,-1] = np.sqrt(A[-1,-1] - A[-1,-2]*A[-1,-2]) # overwrites A[-1,-1]
            

    return np.tril(A), np.diag(P @ E), P


def lineSearch(obj,x,d,alpha0 = 1.0,beta1 = 1.0e-4,beta2 = 0.99,lbd = 2.0):
    """
    Calculate a step along a direction that satisfies both Wolfe conditions

    
    :param obj: function taking x as argument as returning a tuple f,g with
       the value of the objective function f and the gradient g.
    :type obj: function
    :param x: current iterate.
    :type x: numpy.array
    :param d: descent direction.
    :type d: numpy.array
    :param alpha0: first step to test.
    :type alpha0: float
    :param beta1: parameter of the first Wolfe condition.
    :type beta1: float
    :param beta2: parameter of the second Wolfe condition.
    :type beta2: float
    :param lbd: expansion factor for a short step.
    :type lbd: float

    :return: a step verifing both Wolfe conditions
    :rtype: float

    :raises biogeme.exceptons.biogemeError: if lbd :math:`\\leq` 1
    :raises biogeme.exceptons.biogemeError: if alpha0 :math:`\\leq` 0
    :raises biogeme.exceptons.biogemeError: if beta1 :math:`\\geq` beta2
    :raises biogeme.exceptons.biogemeError: if d is not a descent direction
    
    """
    if  lbd <= 1:
        raise excep.biogemeError(f"lambda is {lbd} and must be > 1")
    if  alpha0 <= 0:
        raise excep.biogemeError(f"alpha0 is {alpha0} and must be > 0")
    if  beta1 >= beta2:
        raise excep.biogemeError(f"Incompatible Wolfe cond. parsmeters: beta1={beta1} is greater than beta2={beta2}")
    f,g = obj(x)
    nfev = 1
    deriv = np.inner(g,d)
    if deriv >= 0:
        raise excep.biogemeError(f"d is not a descent direction: {deriv} >= 0")
    i = 0
    alpha = alpha0
    alphal = 0
    alphar = np.finfo(np.float128).max
    finished = False
    while not finished:
        xnew = x + alpha * d ;
        fnew,gnew = obj(xnew)
        nfev += 1
        # First Wolfe condition
        if fnew > f + alpha * beta1 * deriv:
            alphar = alpha ;
            alpha = (alphal + alphar) / 2.0 ;
        # Second Wolfe condition
        elif np.inner(gnew,d) < beta2 * deriv:
            alphal = alpha ;
            if alphar == np.finfo(np.float128).max:
                alpha = lbd * alpha ;
            else:
                alpha = (alphal + alphar) / 2.0
        else:
            finished = True
    return alpha,nfev

def relativeGradient(x,f,g,typx,typf):
    """ Calculates the relative gradients. 

    It is typically used for stopping criteria. 

    :param x: current iterate.
    :type x: numpy.array
    :param f: value of f(x)
    :type f: float
    :param g: :math:`\\nabla f(x)`, gradient of f at x 
    :type g: numpy.array
    :param typx: typical value for x.
    :type typx: numpy.array
    :param typf: typical value for f.
    :type typf: float

    :return: relative gradient

    .. math:: \\max_{i=1,\\ldots,n}\\frac{(\\nabla f(x))_i \\max(x_i,\\text{typx}_i)}{\\max(|f(x)|, \\text{typf})}

    :rtype: float
    """
    relgrad = np.array([g[i] * max(abs(x[i]),typx[i]) / max(abs(f),typf) for i in range(len(x))])
    return abs(relgrad).max()
                           


def newtonLineSearch(obj,x0,eps=np.finfo(np.float64).eps**0.3333,maxiter=100):
    """
    Newton's method with inexact line search (Wolfe conditions)

    :param obj: function taking two arguments:

             - x, the point where the function must be evaluated, and
             - hessian, a boolean indicating if the hessian must be calculated and returning the tuple f,g,H with the value of the function, the gradient and the hessian.
    :type obj: function
    :param x0: starting point
    :type x0: numpy.array
    :param eps: the algorithm stops when this precision is reached. Default: :math:`\\varepsilon^{\\frac{1}{3}}`
    :type eps: float
    :param maxiter: the algorithm stops if this number of iterations is reached. Defaut: 100
    :type maxiter: int

    :return: x,nit,nf,diagnostic where
        
        - x is the solution generated by the algorithm,
        - nit is the number of iterations,
        - nf is the number of function evaluations,
        - diagnostic is the diagnostic provided by the algorithm.

    :rtype: numpy.array, int, int, string
    """
    def f_and_g(x):
        f,g,*_ = obj(x,hessian=False)
        return f,g

    xk = x0
    f,g,H = obj(xk,hessian=True)
    typx = np.ones(np.asarray(xk).shape)
    typf = np.abs(f) / 100.0
    k = 0
    nfev = 0
    cont = True
    while cont:
        L,E,P = schnabelEskow(H)
        y3 = -P.T @ g
        y2 = la.solve_triangular(L,y3,lower=True)
        y1 = la.solve_triangular(L.T,y2,lower=False)
        d = P @ y1
        alpha,nfls = lineSearch(f_and_g,xk,d)
        nfev += nfls
        xk = xk + alpha * d
        f,g,H = obj(xk,hessian=True)
        nfev += 1
        k += 1
        if k == maxiter:
            message = f"Maximum number of iterations reached: {maxiter}"
            cont = False
        relgrad = relativeGradient(xk,f,g,typx,typf)
        if relgrad <= eps:
            message = f"Relative gradient = {relgrad} <= {eps}"
            cont = False
    return xk,k,nfev,message


def newtonLineSearchForBiogeme(fct,initBetas,fixedBetas,betaIds,bounds,parameters=None):
    """Optimization interface for Biogeme, based on Newton's method.

    :param fct: a function taking three arguments:

              - x, the vector of parameters;
              - hessian, a boolean specifying if the hessian must be calculated;
              - bhhh, a boolean specifying if the BHHH matrix must be calculated (ignored by this algorithm);
              - batchSize, if not None, the percentage of the data that must be sampled to obtain a stochastic version of the derivatives (ignored by this algorithm),

            and returning f,g,h,bhhh. It characterizes the function to *maximize*.
    :type fct: function 
    :param initBetas: initial value of the parameters.
    :type initBetas: numpy.array
    :param fixedBetas: betas that stay fixed suring the optimization.
    :type fixedBetas: numpy.array
    :param betaIds: internal identifiers of the non fixed betas.
    :type betaIds: numpy.array
    :param bounds: list of tuples (ell,u) containing the lower and upper bounds for each free parameter. Note that this algorithm does not support bound constraints. Therefore, all the bounds must be None.
    :type bounds: list(tuples)
    :param parameters: dict of parameters to be transmitted to the  optimization routine:             
         - tolerance, when the relavite gradient is below that threshold, the algorithm has reached convergence;
         - maxiter, the maximum number of iterations.
    :type parameters: dict(string:float or int)

    :return: tuple x,nit,nfev,message, where 

            - x is the solution found,
            - nit is the number of iterations performed, 
            - nfev is the number of time that the objective function has been evaluated, and 
            - message is the diagnostic provided by the algorithm.
    :rtype: numpy.array,int,int,string

    """
    for l,u in bounds:
        if l is not None or u is not None:
            raise excep.biogemeError("This algorithm does not handle bound constraints. Remove the bounds, or select another algorithm.")

    tol = np.finfo(np.float64).eps**0.3333
    maxiter = 100
    if parameters is not None:
        if 'tolerance' in parameters:
            tol = parameters['tolerance']
        if 'maxiter' in parameters:
            maxiter = parameters['maxiter']
    def fgh(x,hessian):
        f,g,h,b = fct(x,hessian,bhhh=False)
        if hessian:
            return -f,-np.asarray(g),-np.asarray(h)
        else:
            return -f,-np.asarray(g),None

    return newtonLineSearch(fgh,initBetas,tol,maxiter)

def trustRegionIntersection(dc,d,delta):
    """Calculates the intersection with the boundary of the trust region.
    
    Consider a trust region of radius :math:`\\delta`, centered at
    :math:`\\hat{x}`. Let :math:`x_c` be in the trust region, and
    :math:`d_c = x_c - \\hat{x}`, so that :math:`\\|d_c\\| \\leq
    \\delta`. Let :math:`x_d` be out of the trust region, and
    :math:`d_d = x_d - \\hat{x}`, so that :math:`\\|d_d\\| \\geq
    \\delta`.  We calculate :math:`\\lambda` such that

    .. math:: \\| d_c + \\lambda (d_d - d_c)\\| = \\delta

    :param dc: xc-xhat.
    :type dc: numpy.array
    :param d: dd - dc.
    :type d: numpy.array
    :param delta: radius of the trust region.
    :type delta: float

    :return: :math:`\\lambda` such that :math:`\\| d_c + \\lambda (d_d - d_c)\\| = \\delta`
    
    :rtype: float

    """
    a = np.inner(d,d)
    b = 2 * np.inner(dc,d)
    c = np.inner(dc,dc) - delta ** 2
    discriminant = b * b - 4.0 * a * c
    return (- b + np.sqrt(discriminant) ) / (2 * a)

def cauchyNewtonDogleg(g,H):
    """Calculate the Cauchy, the Newton and the dogleg points.

    The Cauchy point is defined as

    .. math:: d_c = - \\frac{\\nabla f(x)^T \\nabla f(x)}{\\nabla f(x)^T \\nabla^2 f(x)\\nabla f(x)} \\nabla f(x)

    The Newton point :math:`d_n` verifies Newton's equation:

    .. math:: H_s d_n = - \\nabla f(x)

    where :math:`H_s` is a positive definite matrix generated with the method by `Schnabel and Eskow (1999)`_.

    The Dogleg point is 

    .. math:: d_d = \\eta d_n

    where

    .. math:: \\eta = 0.2 + 0.8 \\frac{\\alpha^2}{\\beta |\\nabla f(x)^T d_n|}

    and :math:`\\alpha= \\nabla f(x)^T \\nabla f(x)`, :math:`\\beta=\\nabla f(x)^T \\nabla^2 f(x)\\nabla f(x)`

    :param g: gradient :math:`\\nabla f(x)`

    :type g: numpy.array

    :param H: hessian :math:`\\nabla^2 f(x)`

    :type H: numpy.array

    :return: tuple with Cauchy point, Newton point, Dogleg point
    :rtype: numpy.array, numpy.array, numpy.array
    
    """
    alpha = np.inner(g,g)
    beta = np.inner(g, H @ g)
    dc = - (alpha / beta ) * g
    L,E,P = schnabelEskow(H)
    if np.any(E):
        raise excep.biogemeError("The dogleg method requires a convex optimization problem.")
        
    y3 = -P.T @ g
    y2 = la.solve_triangular(L,y3,lower=True)
    y1 = la.solve_triangular(L.T,y2,lower=False)
    dn = P @ y1
    eta = 0.2 + (0.8 * alpha * alpha / (beta * abs(np.inner(g,dn)))) 
    return dc,dn,eta*dn
    
def dogleg(g,H,delta):
    """
    Find an approximation of the trust region subproblem using the dogleg method

    :param g: gradient of the quadratic model.
    :type g: numpy.array
    :param H: hessian of the quadratic model.
    :type H: numpy.array
    :param delta: radius of the trust region.
    :type delta: float

    :return: d,diagnostic where

          - d is an approximate solution of the trust region subproblem
          - diagnostic is the nature of the solution:

             * -2 if negative curvature along Newton's direction
             * -1 if negative curvature along Cauchy's direction (i.e. along the gradient)
             * 1 if partial Cauchy step 
             * 2 if Newton step
             * 3 if partial Newton step
             * 4 if Dogleg

    :rtype: numpy.array, int
    """

    dc,dn,dl = cauchyNewtonDogleg(g,H)

    
    # Check if the model is convex along the gradient direction

    alpha = np.inner(g,g)
    beta = np.inner(g,H @ g)
    if beta <= 0:
        dstar = -delta * g / np.sqrt(alpha)
        return dstar,-1

    # Compute the Cauchy point
    
    normdc = alpha * np.sqrt(alpha) / beta ;
    if normdc >= delta:
        # The Cauchy point is outside the trust
        # region. We move along the Cauchy
        # direction until the border of the trust
        # region.

        dstar = (delta / normdc) * dc
        return dstar, 1

    # Compute Newton's point

    
    normdn = la.norm(dn)

    # Check the convexity of the model along Newton's direction

    if np.inner(dn,H @ dn) <= 0.0:
        # Return the Cauchy point
        return dc,-2


    if normdn <= delta: 
        # Newton's point is inside the trust region
        return dn,2


    # Compute the dogleg point

    eta = 0.2 + (0.8 * alpha * alpha / (beta * abs(np.inner(g,dn))))  

    partieldn = eta * la.norm(dn)
    
    if partieldn <= delta:
        # Dogleg point is inside the trust region
        dstar = (delta / normdn) * dn ;
        return dstar,3
  
    # Between Cauchy and dogleg
    nu = dl - dc
    lbd = trustRegionIntersection(dc,nu,delta)  
    dstar = dc + lbd * nu ;
    return dstar,4

def truncatedConjugateGradient(g,H,delta):
    """
    Find an approximation of the trust region subproblem using the 
    truncated conjugate gradient method

    :param g: gradient of the quadratic model.
    :type g: numpy.array
    :param H: hessian of the quadrartic model.
    :type H: numpy.array
    :param delta: radius of the trust region.
    :type delta: float

    :return: d,diagnostic, where 

          - d is the approximate solution of the trust region subproblem,
          - diagnostic is the nature of the solution:

            * 1 for convergence,
            * 2 if out of the trust region,
            * 3 if negative curvature detected.

    :rtype: numpy.array, int
    """
    tol = 1.0e-6
    n = len(g)
    xk = np.zeros(n)
    gk = g 
    dk = -gk
    for k in range(n):
        curv = np.inner(dk,H @ dk)
        if  curv <= 0:
            # Negative curvature has been detected
            type = 3
            a = np.inner(dk,dk) 
            b = 2 * np.inner(xk,dk)
            c = np.inner(xk,xk) - delta * delta
            rho = b * b - 4 * a * c ;
            step = xk + ((-b + np.sqrt(rho)) / (2*a)) * dk
            return step,type
        alphak = - np.inner(dk,gk) / curv
        xkp1 = xk + alphak * dk
        if la.norm(xkp1) > delta:
            # Out of the trust region
            type = 2 
            a = np.inner(dk,dk) 
            b = 2 * np.inner(xk,dk)
            c = np.inner(xk,xk) - delta * delta
            rho = b * b - 4 * a * c ;
            step = xk + ((-b + np.sqrt(rho)) / (2*a)) * dk
            return step, type
        xk = xkp1 ;
        gkp1 = H @ xk + g
        betak = np.inner(gkp1,gkp1) / np.inner(gk,gk)
        dk = -gkp1 + betak * dk
        gk = gkp1
        if la.norm(gkp1) <= tol:
          type = 1
          step = xk
          return step,type
    type = 1
    step = xk
    return step, type


def newtonTrustRegion(obj,x0,delta0=100,eps=np.finfo(np.float64).eps**0.3333,dl=False,maxiter=1000,eta1 = 0.01,eta2 = 0.9):
    """Newton's method with trust region

    :param obj: function taking two arguments:

             - x, the point where the function must be evaluated, and
             - hessian, a boolean indicating if the hessian must be calculated and returning the tuple f,g,H with the value of the function, the gradient and the hessian.
    :type obj: function
    :param x0: starting point
    :type x0: numpy.array
    :param delta0: initial radius of the trust region. Default: 100.
    :type delta0: float
    :param eps: the algorithm stops when this precision is reached. Default: :math:`\\varepsilon^{\\frac{1}{3}}`
    :type eps: float
    :param dl: If True, the Dogleg method is used to solve the
       trut region subproblem. If False, the truncated conjugate
       gradient is used. Default: False.
    :type dl: bool
    :param maxiter: the algorithm stops if this number of iterations is reached. Default: 1000.
    :type maxiter: int
    :param eta1: threshold for failed iterations. Default: 0.01.
    :type eta1: float
    :param eta2: threshold for very successful iterations. Default 0.9.
    :type eta2: float
    :return: tuple x,nit,nfev,message, where x is the solution found,
              nit is the number of iterations performed, nfev is the
              number of time that the objective function has been
              evaluated, and message is the diagnostic provided by the
              algorithm.
    :rtype: numpay.array,int,int,string

    """
    k = 0
    xk = x0
    f,g,H = obj(xk,hessian=True)
    typx = np.ones(np.asarray(xk).shape)
    typf = np.abs(f) / 100.0
    relgrad = relativeGradient(xk,f,g,typx,typf)
    delta = delta0
    nfev = 0
    cont = True
    maxDelta = np.finfo(float).max
    while cont:
        k += 1
        if dl:
            step,type = dogleg(g,H,delta)
        else: 
            step,type = truncatedConjugateGradient(g,H,delta)
        xc = xk + step
        fc,gc,Hc = obj(xc,hessian=True)
        nfev += 1
        num = f - fc;
        denom = -np.inner(step,g) - 0.5 * np.inner(step,H @ step)
        rho = num / denom
        if rho < eta1:
            # Failure: reduce the trust region
            delta = la.norm(step) / 2.0
            status = "-"
        else:
            # Candidate accepted
            xk = xc
            f = fc
            g = gc
            H = Hc
            if rho >= eta2:
                # Enlarge the trust region
                delta = min(2 * delta,maxDelta)
                status = "++"
            else:
                status = "+"
            relgrad = relativeGradient(xk,f,g,typx,typf)
            if relgrad <= eps:
                message = f"Relative gradient = {relgrad} <= {eps}"
                cont = False
        if k == maxiter:
            message = f"Maximum number of iterations reached: {maxiter}"
            cont = False
        logger.detailed(f"f={f:10.7g} relgrad={relgrad:6.2g} delta={delta:6.2g} {status}")
                
    return xk,k,nfev,message

def newtonTrustRegionForBiogeme(fct,initBetas,fixedBetas,betaIds,bounds,parameters=None):
    """Optimization interface for Biogeme, based on Newton's method with TR.

    :param fct: a function taking three arguments:

              - x, the vector of parameters;
              - hessian, a boolean specifying if the hessian must be calculated;
              - bhhh, a boolean specifying if the BHHH matrix must be calculated (ignored by this algorithm);
              - batchSize, if not None, the percentage of the data that must be sampled to obtain a stochastic version of the derivatives (ignored by this algorithm),

            and returning f,g,h,bhhh. It characterizes the function to *maximize*.
    :type fct: function 
    :param initBetas: initial value of the parameters.
    :type initBetas: numpy.array
    :param fixedBetas: betas that stay fixed suring the optimization.
    :type fixedBetas: numpy.array
    :param betaIds: internal identifiers of the non fixed betas.
    :type betaIds: numpy.array
    :param bounds: list of tuples (ell,u) containing the lower and upper bounds for each free parameter. Note that this algorithm does not support bound constraints. Therefore, all the bounds must be None.
    :type bounds: list(tuples)
    :param parameters: dict of parameters to be transmitted to the  optimization routine:             
         - tolerance, when the relavite gradient is below that threshold, the algorithm has reached convergence;
         - maxiter, the maximum number of iterations.
    :type parameters: dict(string:float or int)

    :return: tuple x,nit,nfev,message, where 

            - x is the solution found,
            - nit is the number of iterations performed, 
            - nfev is the number of time that the objective function has been evaluated, and 
            - message is the diagnostic provided by the algorithm.
    :rtype: numpy.array,int,int,string

    """
    for l,u in bounds:
        if l is not None or u is not None:
            raise excep.biogemeError("This algorithm does not handle bound constraints. Remove the bounds, or select another algorithm.")

    tol = np.finfo(np.float64).eps**0.3333
    maxiter = 100
    dogleg = False
    radius = 100
    if parameters is not None:
        if 'tolerance' in parameters:
            tol = parameters['tolerance']
        if 'maxiter' in parameters:
            maxiter = parameters['maxiter']
        if 'dogleg' in parameters:
            dogleg = parameters['dogleg']
        if 'radius' in parameters:
            radius = parameters['radius']
    def fgh(x,hessian):
        f,g,h,b = fct(x,hessian,bhhh=False)
        if hessian:
            return -f,-np.asarray(g),-np.asarray(h)
        else:
            return -f,-np.asarray(g),None

    return newtonTrustRegion(obj=fgh,x0=initBetas,delta0=radius,eps=tol,dl=dogleg,maxiter=maxiter)
