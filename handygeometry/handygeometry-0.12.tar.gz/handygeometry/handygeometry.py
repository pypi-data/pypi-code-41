
import math

pi = 3.141592653589793


def area_square(a):
    return a * a


def area_rectangle(length, width):
    return length * width


def area_triangle(base, height):
    """
    Formula: round(b * h / 2,3)
    """
    return (base * height) * 1 / 2


def area_triangle_three_sides(a, b, c):
    """
    Formula: 0.25 * √( (a + b + c) * (-a + b + c) * (a - b + c)
    """
    return 0.25 * ((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))**0.5


def area_triangle_two_sides_and_angle_SAS(a, b, angle):
    """
    Formula: 0.5 * a * b * sin(γ)
    """
    return 0.5 * a * b * math.sin(math.radians(angle))


def area_triangle_two_angles_and_side_ASA(angle1, a, angle2):
    """
    Formula: a² * sin(β) * sin(γ) / (2 * sin(β + γ))
    """
    # math module use radians. so we convert degrees to radians
    angle1, angle2 = math.radians(angle1), math.radians(angle2)
    return round((a * a) * math.sin(angle1) * math.sin(angle2) / (2 * math.sin(angle1 + angle2)), 3)


def area_circle(r):
    """
    Formla: πr²
    """
    return round(pi * (r * r), 3)


def area_circle_sector(r, angle):
    """
    Formula: r² * angle / 2
    """
    return round((r * r) * math.radians(angle) / 2, 3)


def area_ellipse(a, b):
    """
    Formula: a * b * π
    """
    return round(a * b * pi, 3)


def area_trapezoid(a, b, height):
    """
    Formula: (a + b) * h / 2
    """
    return (a + b) * height / 2


def area_parallelogram(base, height):
    """
    Formula: a * h
    """
    return round(base * height, 3)


def area_paralelogram_two_sides_and_angle(a, b, angle):
    """
    Formula: a * b * sin(angle)
    """
    return round(a * b * math.sin(math.radians(angle)), 3)


def area_paralelogram_diagonals_and_an_angle(e, f, angle):
    """
    Formula: e * f * sin(angle)
    """
    return e * f * math.sin(math.radians(angle))


def area_rhombus(side, height):
    """
    Formula: a * h
    """
    return side * height


def area_rhombus_diagonals(e, f):
    """
    Formula: (e * f) / 2
    """
    return (e * f) / 2


def area_rhombus_side_and_any_angle(side, angle):
    """
    Formula: s² * sin(angle)
    """
    return round((side * side) * math.sin(math.radians(angle)), 3)


def area_kite_diagonals(e, f):
    """
    Formula: (e * f) / 2
    """
    return (e * f) / 2


def area_kite_two_unequal_sides_and_angle(a, b, angle):
    """
    Formula: a * b * sin(γ)
    """
    return a * b * math.sin(math.radians(angle))


def area_regular_pentagon(a):
    """
    Formula: a² * √(25 + 10√5) / 4
    """
    return round((a * a) * ((25 + 10 * (5 ** 0.5))) ** 0.5 / 4, 3)


def area_regular_hexagon(a):
    """
    Formula: 3/2 * √3 * a²
    """
    return round(3 / 2 * 3 ** 0.5 * (a * a), 3)


def area_regular_octagon(a):
    """
    Formula: 2 * (1 + √2) * a²
    """
    return round(2 * (1 + 2 ** 0.5) * (a * a), 3)


def area_annulus(R, r):
    """
    Formula: π(R² - r²) --> R>r
    """
    assert R >= r
    return pi * ((R * R) - (r * r))


def area_irregualar_quadrilateral(e, f, angle):
    """
    Formula: e * f * sin(angle)
    """
    return round(e * f * math.sin(math.radians(angle)), 3)


def area_regular_polygon(sides, a):
    """
    Formula: n * a² * cot(π/n) / 4
    """
    return sides * (a * a) * 1 / math.tan(pi / sides) / 4


def perimeter_square(a):
    """
    P =  4a
    """
    return 4 * a


def perimeter_rectangle(a, b):
    """
    P = 2(a + b)
    """
    return 2 * (a + b)


def perimeter_triangle_three_sides_SSS(a, b, c):
    """
    P = a + b + c
    """
    return a + b + c


def perimeter_triangle_two_sides_and_angle_SAS(a, b, angle):
    """
    P = a + b + √(a² + b² - 2ab * cos(γ))
    """
    return round(a + b + ((a * a) + (b * b) - 2 * a * b * math.cos(math.radians(angle))) ** 0.5)


def perimeter_triangle_two_angles_and_side_ASA(a, angle1, angle2):
    """
    P = a + (a / sin(β + γ)) * (sin(β) + sin(γ))
    """
    return round(a + (a / math.sin(math.radians(angle1) + math.radians(angle2))) * (math.sin(math.radians(angle1)) + math.sin(math.radians(angle2))), 3)


def perimeter_circle(r):
    """
    P = 2πr
    """
    return round(2 * pi * r, 3)


def perimeter_circle_sector(r, angle):
    """
    P = r(α + 2) (α is in radians)
    """
    return r * (math.radians(angle) + 2)


def perimeter_ellipse(a, b):
    """
    P = π(3(a + b) - √((3a + b) * (a + 3b)))
    """
    return round(pi * (3 * (a + b) - ((3 * a + b) * (a + 3 * b)) ** 0.5), 3)


def perimeter_quadrilateral(a, b, c, d):
    """
    P = a + b + c + d
    """
    return a + b + c + d


def perimeter_trapezoid(a, b, c, d):
    """
    P = a + b + c + d
    """
    return a + b + c + d


def perimeter_parallelogram_sides(a, b):
    """
    P = 2(a + b)
    """
    return 2 * (a + b)

# TODO hesapla sonucu yanlis cikiyor..


def perimeter_parallelogram_one_side_and_diagonals(a, e, f):
    """
    P = 2a² + √(2e² + 2f² - 4a²)
    """
    pass


def perimeter_parallelogram_base_heigt_any_angle(base, height, angle):
    """
    P = 2(b + h/sin(α))
    """
    return round(2 * (base + height / math.sin(math.radians(angle))), 3)


def perimeter_rhombus_side(a):
    """
    P = 4a
    """
    return 4 * a


def perimeter_rhombus_diagonals(e, f):
    """
    P = 2√(e² + f²)
    """
    return round(2 * ((e * e) + (f * f))**0.5, 3)


def perimeter_kite(a, b):
    """
    P = 2(a + b)
    """
    return round(2 * (a + b), 3)


def perimeter_annulus(R, r):
    """
    P = 2π(R + r)
    """
    assert R > r
    return round(2 * pi * (R + r), 3)


def perimeter_regular_polygon(sides, a):
    """
    P = n * a
    """
    return sides * a

#------------- VOLUME


def volume_cube(s):
    """
    V = s³
    """
    return (s * s * s)


def volume_sphere(r):
    """
    V = (4/3)πr³
    """
    return (4 / 3) * pi * (r * r * r)


def volume_cylinder(r, height):
    """
    Right / oblique full cylinder
    V = π * cylinder_radius² * cylinder_height \n
    cm,cm, result: cm³
    """
    return pi * (r * r) * height


def volume_hollow_cylinder(R, r, height):
    """
    Hollow cylinder
    V = π * (R² - r²) * cylinder_height \n
    cm,cm,cm result: cm³
    """
    assert R > r
    return round(pi * ((R * R) - (r * r)) * height, 3)


def volume_pyramid(base_area, height):
    """
    That formula is working for any type of base polygon and oblique and right pyramids. All you need to know are those two values - base area and height. \n
    V = (1/3) * base_area * height \n
    """
    return round((1 / 3) * base_area * height, 3)


def volume_pyramid_with_regular_base(shape_of_base, height, side_length):
    """
    In case you don't know the base area. For any pyramid with a regular base, you can use the equation:\n
    V = (n/12) * height * side_length² * cot(π/n) \n where n is number of sides of the base for regular polygon
    """
    return (shape_of_base / 12) * height * (side_length * side_length) * 1 / math.tan(pi / shape_of_base)


def volume_cone(r, height):
    """
    Right / oblique cone \n
    V = (1/3) * π * r² * h
    """
    return round((1 / 3) * pi * (r * r) * height, 3)


def volume_truncated_cone(lower_r, upper_r, height):
    """
    V=(1/3)*π(r1²+r1*r2+r2²)*height
    """
    return round((1 / 3) * pi * ((lower_r * lower_r) + lower_r * upper_r + (upper_r * upper_r)) * height, 3)


def volume_ellipsoid(a, b, c):
    """
    semi-axis a,b,c
    """
    return (4 / 3) * pi * a * b * c


def volume_torus(a, b):
    """
    inner radius, outer radius
    """
    return (1 / 4) * (pi**2) * (a + b) * (b - a)**2


def volume_rectangular_cuboid(length, width, height):
    return length * width * height


def volume_regular_tetrahedron(a):
    """
    Calculates the volume of a regular tetrahedron from the edge length.
    """
    return ((2)**0.5 / 12) * (a**3)


def volume_obelisk(a, b, A, B, height):
    """
    Calculates the volume of a obelisk given the base and top sides, and height.
    """
    return (height / 6) * (A * b + a * B + 2 * (a * b + A * B))


def volume_wedge(a, b, c, height):
    """
    Calculates the volume of a wedge given the bottom of the rectangle.
    """
    return ((b * height) / 6) * (2 * a + c)


def volume_frustum(s1, s2, height):
    """
    Calculates the volume of a frustum given the base and top areas, and height.
    """
    return (height / 3) * (s1 + s2 + (s1 * s2)**0.5)

# Total surface area = base + lateral


def surface_area_wedge(a, b, c, height):
    """
    Calculates the lateral and surface areas of a wedge given the bottom of the rectangle.
    """
    lateral_area = (a + c) / 2 * (4 * (height ** 2) + (b ** 2)
                                  ) ** 0.5 + b * ((height ** 2) + (a - c) ** 2) ** 0.5
    surface_area = lateral_area + a * b
    return surface_area


def surface_area_regular_tetrahedron(a):
    """
    Calculates the surface area of a regular tetrahedron from the edge length.
    """
    return (3**0.5) * (a**2)


def surface_area_rectangular_cuboid(length, width, height):
    return 2 * (length * width + width * height + height * length)


def surface_area_torus(a, b):
    """
    inner radius, outer radius
    """
    return (pi ** 2) * (b ** 2 - a ** 2)


def surface_area_sphere(r):
    """
    A = 4πr², r stands for radius
    """
    return round(4 * pi * ((r * r)), 3)


def surface_area_cube(a):
    """
    A = 6a²
    """
    return 6 * (a * a)


def surface_area_cylinder(r, height):
    """
    A = 2πr² + 2πrh
    """
    return round(2 * pi * (r * r) + 2 * pi * r * height, 3)


def surface_area_lateral_cylinder(r, height):
    """
    A(lateral) = h * (2 * π * r)
    """
    return round(height * (2 * pi * r), 3)


def surface_area_base_cylinder(r):
    """
    A(base) = π * r²
    """
    return round(pi * (r * r), 3)


def surface_area_cone(r, height):
    """
    A = πr² + πr√(r² + h²)
    """
    return pi * (r * r) + pi * r * ((r * r) + (height * height)) ** 0.5


def surface_area_lateral_cone(r, height):
    """
    A(lateral) = π * r * √(r² + h²)
    """
    return round(pi * r * ((r * r) + (height * height)) ** 0.5, 3)


def surface_area_base_cone(r, height):
    """
    A(base) = π * r²
    """
    return round(pi * (r * r), 3)


def surface_area_rectangular_prism_box(a, b, c):
    """

    A = 2(ab + bc + ac)
    """
    return round(2 * (a * b + b * c + a * c), 3)


def surface_area_triangular_prism(a, b, c, height):
    """
    A = 0.5 * √((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c)) + h * (a + b + c)
    """
    return round(0.5 * ((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))**0.5 + height * (a + b + c), 3)


def surface_area_pyramid(l, height):
    """
    A = l * √(l² + 4 * h²) + l² \n
    l is a side length of the square base and h is a height of a pyramid.
    """
    return round(l * ((l * l) + 4 * (height * height))**0.5 + (l * l), 3)


def surface_area_base_pyramid(l):
    """
    A(base) = l²
    """
    return round((l * l), 3)

# TODO hesaplama sonuclari yanlis cikiyor..


def surface_area_lateral_pyramid(l, height):
    """
    A(lateral face) = √(h² + l²/4) * l / 2
    """
    pass

###################
# Inscribed and circumscribed
#
###################

# TODO geri kalanlari ekleyelim


def incircle_of_a_triangle(a, b, c):
    """
    Calculates the radius and area of the incircle of a triangle given the three sides
    """
    s = (a + b + c) / 2
    _incircle_radius = r = (s * (s - a) * (s - b) * (s - c)) ** 0.5 / s
    _incircle_area = Sc = pi * (r ** 2)
    _triangle_area = St = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    area_ratio = Sc / St
    return r, Sc, St, area_ratio


def incircle_of_a_regular_polygon(n, a):
    """
    Calculates the radius and area of the incircle of a regular polygon.
    n= number of sides
    """
    _inradius = r = a / (2 * math.tan(pi / n))
    _incircle_area = Sc = pi * (r ** 2)
    _polygon_area = Sp = (1 / 2) * n * a * r
    area_ratio = Sc / Sp
    return r, Sc, Sp, area_ratio


def regular_polygons_inscribed_to_a_circle(n, r):
    """
    Calculates the side length and area of the regular polygon inscribed to a circle.
    n= number of sides
    """
    _polygon_side = a = round(2 * r * math.sin(pi / n), 3)
    _polygon_area = Sp = (1 / 2) * n * (r ** 2) * math.sin((2 * pi) / n)
    _circle_area = Sc = pi * (r ** 2)
    area_ratio = Sp / Sc
    return a, Sp, Sc, area_ratio


def circumcircle_of_a_triangle(a, b, c):
    """
    Calculates the radius and area of the circumcircle of a triangle given the three sides.

    s = (a + b + c) / 2
    _circumcirle_radius = r = (a * b * c) / (s * (s - a) * (s - b) * (s - c))**(1/4)
    _circumcirle_area = Sc = pi * (r ** 2)
    _triangle_area = St = (s * (s - a) * (s - b) * (s - c))**0.5
    return r,Sc,St
    """
    pass


def circumcircle_of_a_regular_polygon(n, a):
    """
    Calculates the radius and area of the circumcircle of a regular polygon.
    n= number of sides
    """
    _circumradius = r = a / (2 * math.sin(pi / n))
    _circumcircle_area = Sc = pi * (r ** 2)
    _polygon_area = Sp = n * (a ** 2) / (4 * math.tan(pi / n))
    area_ratio = Sc / Sp
    return r, Sc, Sp, area_ratio


def regular_polygon_circumscribed_to_a_circle(n, r):
    """
    Calculates the side length and area of the regular polygon circumscribed to a circle.
    n = number of sides
    """
    _polygon_side = a = 2 * r * math.tan(pi / n)
    _polygon_area = Sp = (1 / 2) * n * a * r
    _circle_area = Sc = pi * (r ** 2)
    area_ratio = Sp / Sc
    return a, Sp, Sc, area_ratio

#------------------- OTHERS


def edge_length_cube(V):
    """
    Calculates the edge length and surface area of a cube given the volume
    """
    a = V ** (1 / 3)
    S = 6 * (a ** 2)

    return a, S


def angles_of_a_triangle(a, b, c):
    """
    Calculates the three angles and area of a triangle given three sides.
    """
    s = (a + b + c) / 2
    S = (s * (s - a) * (s - b) * (s - c))**0.5
    h = (2 * S) / a
    _angle_B = B = math.degrees(math.asin(h / c))  # chance radians to degree
    _angle_C = C = math.degrees(math.asin(h / b))
    _angle_A = A = 180 - (B + C)
    inradius = S / s
    circumradius = a / (2 * math.sin(math.radians(A)))
    return A, B, C, inradius, circumradius


def regular_polyhedrons(n, a):
    """
    Calculates the volume, surface area and radii of inscribed and circumscribed spheres of the regular polyhedrons given the side length.
    n=number of faces
    a= side length
    """
    def r_i(V, S):
        return (3 * V) / S

    def r_c(r_i, a, k):
        return ((r_i ** 2) + (a / (2 * math.sin(pi / k)) ** 2))**0.5

    if n == 4:  # tetrahedron
        V = ((2 ** 0.5) / 12) * (a ** 3)
        S = (3 * (a ** 2)) ** 0.5
        k = 3
        ri = r_i(V, S)
        rc = r_c(ri, a, k)
        #r_i = (3 * V) / S
        #rc = ((r_i ** 2) + (a / (2 * math.sin(pi / k))** 2))**0.5
    if n == 6:  # cube
        V = (a ** 3)
        S = 6 * (a ** 2)
        k = 4
        ri = r_i(V, S)
        rc = r_c(ri, a, k)
    if n == 8:  # octahedron
        V = ((2 ** 0.5) / 3) * (a ** 3)
        S = 2 * (3 * (a ** 2)) ** 0.5
        k = 3
        ri = r_i(V, S)
        rc = r_c(ri, a, k)
    if n == 12:  # dodecahedron
        V = ((15 + 7 * (5) ** 0.5) / 4) * (a ** 3)
        S = 3 * (25 + 10 * (5 * (a ** 2)) ** 0.5) ** 0.5
        k = 5
        ri = r_i(V, S)
        rc = r_c(ri, a, k)
    if n == 20:  # icosahedron
        V = ((5 * (3 + (5) ** 0.5)) / 12) * (a ** 3)
        S = 5 * (3 * (a ** 2)) ** 0.5
        k = 3
        ri = r_i(V, S)
        rc = r_c(ri, a, k)
    return "Volume:{}, Area:{}, Insphere:{} Circumsphere:{}".format(V, S, ri, rc)


def vector_norm(*args):
    """
    Calculates the L1 norm, the Euclidean (L2) norm and the Maximum(L infinity) norm of a vector.
    """
    L1 = sum(args)
    L2 = (sum([i ** 2 for i in args])) ** 0.5
    Linf = max([abs(i) for i in args])
    return L1, L2, Linf
