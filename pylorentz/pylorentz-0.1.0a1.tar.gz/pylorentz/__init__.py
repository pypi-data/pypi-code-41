"""
Pylorentz is a python package to facilitate working with 4-vectors and lorentz
boosts in high energy physics.
"""
__version__ = '0.1.0-alpha.1'

import abc
import cmath
import math
import numpy as np

METRIC = np.diag([1, -1, -1, -1])

class Vector4:
    """
    Representation of a Lorentz 4-vector.
    """
    def __init__(self, *x):
        """
        Creates a new 4-vector. The arguments can be either the four
        components or another 4-vector.

        >>> Vector4(60, 2, 3, 4)
        Vector4(60, 2, 3, 4)

        >>> vec = Vector4(60, 1, 2, 3)
        >>> Vector4(vec)
        Vector4(60, 1, 2, 3)
        """
        if len(x) == 1 and isinstance(x[0], Vector4):
            x = x[0]
            self._values = np.array(x.components)
        elif len(x) == 4:
            self._values = np.array(list(x))
        else:
            raise TypeError("4-vectors expects four values")

    def __repr__(self):
        """
        Returns a string representation of the object.
        """
        return "%s(%s)" % (self.__class__.__name__,
                           ", ".join(["%g" % _ for _ in self._values]))

    @property
    def components(self):
        """
        Returns the interal array of all components.
        """
        return self._values

    def __add__(self, other):
        """
        Addition of two 4-vectors. Can only add vectors of the same type (or
        subtype).

        >>> a = Vector4(1, 2, 3, 4)
        >>> b = Vector4(2, 4, 8, 16)
        >>> a + b
        Vector4(3, 6, 11, 20)
        """
        vector = self.__class__(self)
        vector += other
        return vector

    def __iadd__(self, other):
        """
        In-place addition of two 4-vectors.

        >>> a = Vector4(1, 2, 3, 4)
        >>> b = Vector4(2, 4, 8, 16)
        >>> b += a
        >>> b
        Vector4(3, 6, 11, 20)
        """
        self._values = self.components + Vector4(*other).components
        return self

    def __sub__(self, other):
        """
        Subtraction of two 4-vectors.

        >>> a = Vector4(1, 2, 3, 4)
        >>> a - b
        Vector4(-3, -1, 1, 3)
        """
        vector = self.__class__(self)
        vector -= other
        return vector

    def __isub__(self, other):
        """
        In-place subtraction of two 4-vectors.

        >>> a = Vector4(1, 2, 3, 4)
        >>> b = Vector4(4, 3, 2, 1)
        >>> b -= a
        >>> b
        Vector4(-3, -1, 1, 3)
        """
        self._values = self.components - Vector4(*other).components
        return self

    def __mul__(self, other):
        """
        Multiplication of a 4-vector by a scalar or the dot product with
        another 4-vector.
        """
        if hasattr(other, "__len__") and len(other) == 4:
            # Dot product
            other = Vector4(*other)
            return self.components.dot(METRIC).dot(other.components)

        vector = self.__class__(self)
        vector *= other
        return vector


    def __rmul__(self, other):
        """
        Multiplication of a 4-vector by a scalar from the left.
        """
        return self * other

    def __imul__(self, other):
        """
        Multiplication of a 4-vector by a scalar from the left.
        """
        if hasattr(other, "__len__") and len(other) != 1:
            raise TypeError("In-place multiplication only possible for "
                            "scalars.")

        self._values *= other
        return self

    def __truediv__(self, other):
        """
        Division of a 4-vector by a scalar from the left.
        """
        vector = self.__class__(self)
        vector /= other
        return vector

    def __floordiv__(self, other):
        """
        Division of a 4-vector by a scalar from the left.
        """
        vector = self.__class__(self)
        vector //= other
        return vector

    def __ifloordiv__(self, other):
        """
        In-place division of a 4-vector by a scalar.
        """
        if hasattr(other, "__len__") and len(other) != 1:
            raise TypeError("Division only possible by scalars.")

        # in-place div no always possible for numpy arrays depending on their
        # type, i.e. cannot in-place convert int array to float
        self._values = self._values // other
        return self

    def __itruediv__(self, other):
        """
        In-place division of a 4-vector by a scalar.
        """
        if hasattr(other, "__len__") and len(other) != 1:
            raise TypeError("Division only possible by scalars.")

        # in-place div no always possible for numpy arrays depending on their
        # type, i.e. cannot in-place convert int array to float
        self._values = self._values / other
        return self

    def __div__(self, other):
        """
        Legacy support
        """
        return self.__truediv__(other)

    def __idiv__(self, other):
        """
        Legacy support
        """
        return self.__itruediv__(other)

    def __len__(self):
        """
        Returns 4, i.e. the length of the vector.
        """
        return 4

    def __iter__(self):
        """
        Returns an iterator over all its values.
        """
        return iter(self._values)

    def __getitem__(self, i):
        """
        Access to the components of the vector.
        """
        return self._values[i]

    @property
    def mag(self):
        """
        Magnitude of vector.
        """
        return cmath.sqrt(self.mag2)

    @property
    def mag2(self):
        """
        Square of magnitude of vector, i.e. the dot product with itself.
        """
        return self * self

    @property
    def trans(self):
        """
        Magnitude of the transverse component.
        """
        return math.sqrt(self[1]**2 + self[2]**2)

    @property
    def eta(self):
        """
        Returns the pseudo-rapidity, a measure for the angle between the
        vector and the x[3] axis.
        """
        if self.theta == 0:
            return float('inf')

        if self.theta == math.pi:
            return float('-inf')

        return -math.log(math.tan(self.theta / 2))

    @property
    def phi(self):
        """
        Polar angle in the x[1:4] space.
        """
        return math.atan2(self[2], self[1])

    @property
    def theta(self):
        """
        Azimuth angle in the x[1:4] space.
        """
        return math.atan2(self.trans, self[3])

    # pylint: disable=too-many-arguments
    def boost(self, x, y, z, beta=None, gamma=None):
        """
        Boosts the 4-vector in the direction given by (x, y, z). The magnitude
        of (x, y, z) is ignored. Exactly one of beta and gamma must be given.

        The method returns the transformed 4-vector as measured in the frame
        moving in (x, y, z) direction with velocity defined by beta or gamma.
        This is the opposite of TLorentzVector::Boost().
        """
        if beta is None:
            if gamma is None:
                raise ValueError("beta and gamma cannot be both None")
            beta = math.sqrt(1 - 1 / gamma**2)
        else:
            if gamma is not None:
                raise ValueError("beta and gamma cannot be both not None")
            gamma = 1 / math.sqrt(1 - beta**2)

        p = np.array([x, y, z])
        p = p / math.sqrt(p.dot(p))

        A = np.array([[0, 0, 0, 0]] + [[0] + list(p)]*3)
        # pylint: disable=invalid-unary-operand-type
        A = (gamma - 1) * A * A.transpose() + np.diag([0, 1, 1, 1])
        bp = -beta * p

        B = np.array([[0] + list(bp)] + [[0, 0, 0, 0]]*3)
        B = gamma * (B + B.transpose() + np.diag([1, 0, 0, 0]))

        L = B + A

        return self.__class__(*L.dot(self.components))


    def boost_particle(self, momentum):
        """
        Performs a Lorentz transformation of the 4-vector. The boost is
        specified by the 4-momentum of a particle (measured in the laboratory
        frame). The transformation is from the particle rest frame into the
        laboratory frame.

        The method returns the transformed 4-vector.
        """

        gamma = momentum.e / momentum.m
        if gamma.imag != 0:
            raise ValueError("Invalid boost momentum.")
        gamma = abs(gamma)

        return self.boost(*(-momentum.components)[1:], gamma=gamma)

class Momentum4(Vector4):
    """
    Representation of 4-momenta.
    """
    @staticmethod
    def e_eta_phi_pt(e, eta, phi, p_t):
        """
        Creates a new energy-momentum vector based on energy, pseudo-rapidity,
        polar angle and transverse momentum.
        """
        p_x = math.cos(phi) * p_t
        p_y = math.sin(phi) * p_t
        p_z = p_t / (math.tan(2*math.atan(math.exp(-eta))))
        return Momentum4(e, p_x, p_y, p_z)

    @staticmethod
    def m_eta_phi_pt(m, eta, phi, p_t):
        """
        Creates a new energy-momentum vector based on mass, pseudo-rapidity,
        polar angle and transverse momentum.
        """
        p_x = math.cos(phi) * p_t
        p_y = math.sin(phi) * p_t
        p_z = p_t / (math.tan(2*math.atan(math.exp(-eta))))
        e = math.sqrt(m**2 + p_x**2 + p_y**2 + p_z**2)
        return Momentum4(e, p_x, p_y, p_z)

    @staticmethod
    def m_eta_phi_p(m, eta, phi, p):
        """
        Creates a new energy-momentum vector based on mass, pseudo-rapidity,
        polar angle and momentum.
        """
        theta = 2 * math.atan(math.exp(-eta))
        p_x = math.cos(phi) * math.sin(theta) * p
        p_y = math.sin(phi) * math.sin(theta) * p
        p_z = math.cos(theta) * p
        e = math.sqrt(m**2 + p_x**2 + p_y**2 + p_z**2)
        return Momentum4(e, p_x, p_y, p_z)

    @staticmethod
    def e_eta_phi_p(e, eta, phi, p):
        """
        Creates a new energy-momentum vector based on energy, pseudo-rapidity,
        polar angle and momentum.
        """
        theta = 2 * math.atan(math.exp(-eta))
        p_x = math.cos(phi) * math.sin(theta) * p
        p_y = math.sin(phi) * math.sin(theta) * p
        p_z = math.cos(theta) * p
        return Momentum4(e, p_x, p_y, p_z)

    @staticmethod
    def e_m_eta_phi(e, m, eta, phi):
        """
        Creates a new energy-momentum vector based on energy, mass,
        pseudo-rapidity and polar angle.
        """
        p = math.sqrt(e**2 - m**2)
        return Momentum4.e_eta_phi_p(e, eta, phi, p)

    @property
    def p_t(self):
        """
        Returns the transverse momentum.
        """
        return self.trans

    @property
    def m(self):
        """
        Returns the mass.
        """
        return self.mag

    @property
    def m2(self):
        """
        Returns the mass squared.
        """
        return self.mag2

    @property
    def p(self):
        """
        Returns the magnitude of the 3-momentum.
        """
        return math.sqrt(self.p2)

    @property
    def p2(self):
        """
        Returns the square of the magnitude of the 3-momentum.
        """
        return self.p_x**2 + self.p_y**2 + self.p_z**2

    @property
    def p_x(self):
        """
        Returns the x-component of the momentum.
        """
        return self[1]

    @property
    def p_y(self):
        """
        Returns the y-component of the momentum.
        """
        return self[2]

    @property
    def p_z(self):
        """
        Returns the y-component of the momentum.
        """
        return self[3]

    @property
    def e(self):
        """
        Returns the energy of the vector.
        """
        return self[0]


class Position4(Vector4):
    """
    Representation of points in space-time.
    """

    @property
    def x(self):
        """
        Returns the x component of the vector.
        """
        return self[1]

    @property
    def y(self):
        """
        Returns the y component of the vector.
        """
        return self[2]

    @property
    def z(self):
        """
        Returns the z component of the vector.
        """
        return self[3]

    @property
    def t(self):
        """
        Returns the t component of the vector.
        """
        return self[0]
