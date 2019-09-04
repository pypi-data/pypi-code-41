#Package created by Tinos Psomadakis
#Version 2.0
import os
import math

#Quadratic formula solver
def quadratic(num1,num2,num3):
    """Usage: (NUMx^2)=num1 (NUMx)=num2 (NUM)=num3 Example: 3x^2+5x-2 num1=3, num2=5, num3=-2"""
    last=math.sqrt(num2**2 - 4 * (num1) * (num3))
    result1 = -num2 + last
    ans1 = (result1 / (2 * num1))
    result2 = -num2 - last
    ans2 = (result2 / (2 * num1))
    return ans1, ans2

def pythagoras(a=None, b=None, c=None):
    """Given two sides of a triangle abc, solve for the missing side.

Usage: pythagoras(a=3,c=4) leaving out the side you want to solve for."""

    have_a, have_b, have_c = a is not None, b is not None, c is not None

    if not have_a and have_b and have_c:
        return math.sqrt((c**2)-(b**2))
    if have_a and not have_b and have_c:
        return math.sqrt((c**2)-(a**2))
    if have_a and have_b and not have_c:
       return math.sqrt((a**2)+(b**2))

    raise Exception("You must specify exactly two sides.")

#Solve distance using speed and time
def distance_dst(speed, time):
    """Usage: distance_dst(speed of object, time taken to get there)"""
    return speed*time

#Solve speed using distance and time
def speed_dst(distance, time):
    """Usage: speed_dst(distance traveled, time taken)"""
    return distance/time

#Solve time using speed and distance
def time_dst(distance, speed):
    """Usage: time_dst(distance traveled, speed of object)"""
    return distance/speed

#Solve force using mass and acceleration
def force_fma(mass,acceleration):
    """Usage: force_fma(mass of object, acceleration)"""
    return mass*acceleration


#Solve mass using force and acceleration
def mass_fma(force,acceleration):
    """Usage: mass_fma(force of object, acceleration of object)"""
    return force/acceleration


#Solve acceleration using mass and force
def acceleration_fma(force,mass):
    """Usage: acceleration_fma(force of object, mass of object)"""
    return force/mass


#Solve weight using mass and gravitational field strength
def weight_wmg(mass, gravitational_field_strength):
    """Usage: weight_wmg(Mass of object, gravitational field strength)"""
    return mass*gravitational_field_strength


#Solve mass using weight and gravitational field strength
def mass_wmg(weight, gravitational_field_strength):
    """Usage: mass_wmg(weight (Newtons), gravitational field strength)"""
    return weight/gravitational_field_strength


#Solve gravitational field strength using weight and mass
def gravity_wmg(weight, mass):
    """Usage: gravity_wmg(weight of object, mass of object)"""
    return weight/mass


#Solve for area of circle using radius
def circle_area_rad(radius):
    """Usage: Find circle's area from radius"""
    return math.pi*(radius**2)


#Solve for area of circle using diameter
def circle_area_dia(diameter):
    """Usage: Find circle's area from diameter"""
    return (1/4)*(math.pi*(diameter**2))


#Solve for diameter of circle using radius
def circle_diam_rad(radius):
    """Usage: Find circle's diameter from radius"""
    return radius*2


#Solve for diameter of circle using area
def circle_diam_are(area):
    """Usage: Find circle#s diameter from the area"""
    return 2*(math.sqrt(area/math.pi))


#Solve for circumference of circle using area
def circle_circum_rad(radius):
    """Usage: Find circumference from radius"""
    return 2*(math.pi*radius)


#Solve acceleration using Change in velocity and time
def acceleration_avt(delta_velocity,time):
    """Usage: acceleration_avt(change in speed, time taken)"""
    return delta_velocity/time


#Solve Change in velocity using acceleration and time
def delta_velocity_avt(acceleration,time):
    """Usage: delta_velocity_avt(acceleration of object, time taken)"""
    return acceleration*time


#Solve time taken using acceleration and change in velocity
def time_avt(acceleration,delta_velocity):
    """Usage: time_avt(acceleration of object, change in speed)"""
    return delta_velocity/acceleration


#Solve pressure using force and area
def pressure_fpa(force, area):
    """Usage: pressure_fpa(force of object, areaof object)"""
    return force/area


#Solve force using pressure and area
def force_fpa(pressure, area):
    """Usage: force_fpa(pressure, area of object)"""
    return pressure/area


#Solve area using pressure and force
def area_fpa(force, pressure):
    """Usage: area_fpa(force of object, pressure)"""
    return force*pressure


#Solve volume of a cylinder
def cylinder_vol(radius,height):
    """Usage: find volume of a cylinder"""
    return math.pi*(radius**2*(height))


#Solve surface area of a cylinder
def cylinder_surface_are(radius,height):
    """Usage: Find surface area of a cylinder"""
    return (2*(math.pi*radius*height))+2*(math.pi*(radius**2))


#Solve area of a trapezoid
def trapezoid_area(base_short,base_long,height):
    """Usage: Find the area of a trapezoid"""
    return ((base_short+base_long)/2)*height


#Solve height of a trapezoid
def trapezoid_height(base_short,base_long,area):
    """Usage: Find height of a trapezoid"""
    return 2*(area/(base_short+base_long))


#Solve surface area of a trapezoid
def trapezoid_surface_are(base_short,base_long,height):
    """Usage: Find the surface area of a trapezoid"""
    return ((base_short+base_long)/2)*height


def energy_evq(voltage,charge):
    """Usage: energy_evq(voltage, charge)"""
    return voltage*charge


def voltage_evq(energy,charge):
    """Usage: voltage_evq(energy, charge)"""
    return energy/charge


def charge_evq(energy,voltage):
    """Usage: charge_evq(energy,voltage)"""
    return energy/voltage


def power_piv(current, voltage):
    """Usage: power_piv(current, voltage)"""
    return current*voltage


def current_piv(power, voltage):
    """Usage: current_piv(power, voltage)"""
    return power/voltage


def voltage_piv(power, current):
    """Usage: voltage_piv(power,current)"""
    return power/current

def power_pet(energy,time):
    """Usage: power_pet(energy,time)"""
    return energy/time

def energy_pet(power,time):
    """Usage: energy_pet(power,time)"""
    return power*time

def time_pet(power,energy):
    """Usage: time_pet(power,energy)"""
    return energy/power

def sequence_nth(first_term,term_number,common_difference):
    """Usage: Find the nth term of a sequence"""
    return first_term+(common_difference*(term_number-1))

def sequence_first(nth,term_number,common_difference):
    """Usage: Find first number from a sequence"""
    return nth-(common_difference*(term_number-1))

def sequence_difference(nth,first_term,term_number):
    """Usage: Find the difference in a sequence"""
    return (nth-first_term)/(term_number-1)

def sequence_termnum(nth,first_term,common_difference):
    """Usage: Find the term number in a sequence"""
    return ((nth-first_term)/common_difference)+1

def orbitalspeed_vrt(radius,time):
    """Usage: orbitalspeed_vrt(radius of orbit, time taken)"""
    return (2*(math.pi)*radius)/time

def radius_vrt(orbitalspeed,time):
    """Usage: radius_vrt(orbit speed, time taken)"""
    return (orbitalspeed*time)/(2*math.pi)

def orbittime_vrt(orbitalspeed,radius):
    """Usage: orbittime_vrt(orbital speed, radius of orbit)"""
    return (2*math.pi*radius)/orbitalspeed

def cosine_side_a(b,c,angle_A):
    """Usage: Find side a"""
    return math.sqrt((b**2+c**2)-(2*(b*c*math.cos(angle_A))))

def cosine_side_b(a,c,angle_B):
    """Usage: Find side b"""
    return math.sqrt(a**2+c**2-(2*a*c*math.cos(angle_B)))

def cosine_side_c(a,b,angle_C):
    """Usage: Find side c"""
    return math.sqrt(a**2+b**2-(2*a*b*math.cos(angle_C)))

def cosine_angle_A(a,b,c):
    """Usage: Find angle A"""
    return math.acos(((b**2+c**2)-a**2)/(2*b*c))

def cosine_angle_B(a,b,c):
    """Usage: Find angle B"""
    return math.acos(((a**2+c**2)-b**2)/(2*a*c))

def cosine_angle_C(a,b,c):
    """Usage: Find angle C"""
    return math.acos(((a**2+b**2)-c**2)/(2*a*b))

def energy_emc(mass,speedoflight):
    """Usage: energy_emc(mass of object, speed of light) - You can use the constant light_speed."""
    return mass*speedoflight**2

def mass_emc(energy,speedoflight):
    """Usage: mass_emc(energy of an object, speed of light) - You can use the constant light_speed."""
    return energy/(speedoflight**2)

def speedoflight_emc(energy,mass):
    """Usage: Find the speed of light using energy and mass"""
    return math.sqrt(energy/mass)

def schwarzschild(gravity,mass,speedoflight):
    """Usage: schwarzschild(gravity, mass, speed of light) - Note: you can use the constant earth_g for the earth's gravity and light_speed for the speed of light."""
    return (2*gravity*mass)/(speedoflight**2)

def sphere_mass(density,radius):
    """Usage: Find the mass of a sphere using density and radius"""
    return density*((4/3)*(math.pi)*radius**3)

def sphere_density(mass,radius):
    """Usage: Find the density of a sphere using mass and radius"""
    return mass/((4/3)*math.pi*radius**3)

def sphere_radius(mass,density):
    """Usage: Find the radius of a sphere knowing mass and density"""
    return (mass/(density*(4/3)*math.pi))** (1. / 3)

def cube_vol(side_length):
    """Usage: cube_volume(Side of one length)"""
    return side_length**3

def rectangle_vol(length,width,height):
    """Usage: rectangle_vol(length rectangle, width of rectangle, height of rectangle)"""
    return length*width*height

def sphere_vol(radius):
    """Usage: Find the volume of a sphere using the radius"""
    return (4*math.pi*(radius**3))/3

def cone_vol(radius,height):
    """Usage: Find the volume of a cone using radius and height"""
    return (math.pi*(radius**2)*height)/3

def pyramid_vol(base_area,height):
    """Usage: Find the volume of a pyramid  using base area and height"""
    return (base_area*height)/3

#GitHub SirEraz

def force_fmg(mass,gravitational_field_strength):
    """Usage: Find force of gravity using mass and a gravitational constant """
    return mass * gravitational_field_strength
#(f(g)=mg) find mass using force of grav and g
def mass_fmg(force,gravitational_field_strength):
    """Usage: Find mass using force of gravity and a gravitational constant """
    return force / gravitational_field_strength
#(f(g)=mg) find grav constant using force of g and mass
def gravity_fmg(force,mass):
    """Usage: Find gravity using force and mass """
    return force / mass

def friction_fnc(normal_force,friction_coefficient):
    """Usage: Find force of friction using normal force and friction coefficent"""
    return normal_force * friction_coefficient
#(F(f)=u*F(n)) finds normal force (F(n)) using F(f) and friction coefficient (u)
def normal_fnc(friction_force,friction_coefficient):
    """Usage: Find normal force using force of friction and friction coefficent"""
    return friction_force / friction_coefficient
#(F(f)=u*F(n)) finds friction coefficient (u) using F(f) and F(n)
def coefficient_fmc(friction_force,normal_force):
    """Usage: Find friction coefficent using force of friction and normal force"""
    return friction_force / normal_force

def acceleration_aug(friction_coefficient,gravity):
    """Usage: Find acceleration using friction coefficient and gravitational constant"""
    return friction_coefficient * gravity
#(a=ug) find fric. coefficient (u) using acceleration and grav constant
def coefficient_aug(acceleration,gravity):
    """Usage: Find friction coefficient using acceleration and gravitational constant"""
    return acceleration / gravity
#(a=ug) find grav constant using u and a
def gravity_aug(acceleration,friction_coefficient):
    """Usage: Find gravitational constant using acceleration and friction coefficient"""
    return acceleration / friction_coefficient

def coefficient_cfn(friction,normal):
    """Usage: Find coefficient with friction and normal force"""
    return friction / normal
#(u=F(f)/F(n)) find F(f) with u and F(n)
def friction_cfn(coefficient,normal):
    """Usage: Find friction using coefficient and normal force"""
    return coefficient * normal
#(u=F(f)/F(n)) find F(n) with u and F(f)
def normal_cfn(coefficient,friction):
    """Usage: Find normal force using coefficient and friction"""
    return friction / coefficient

def radius_rf(focal_point):
    """Usage: radius with focal point for concave and convex mirrors"""
    return 2 *focal_point
#(C=2f) find focal point with C
def focal_rf(radius):
    """Usage: focal point with radius for concave and convex mirrors"""
    return radius / 2

#(f=(di*do/di+do)) find focal point (f) with d(i) and d(o)
def focal_point(distance_image,distance_object):
    """Usage: Find focal point with distance of image and distance of object"""
    numerator = distance_image * distance_object
    denominator = distance_image + distance_object
    return numerator / denominator
#d(i)=(f*do/do-f) find d(i) with focal point and d(o)
def mirror_distance_image(focal_point,distance_object):
    """Usage: Find distance of image with focal point and distance of object"""
    numerator = focal_point * distance_object
    denominator = distance_object - focal_point
    return numerator / denominator
#d(o)=(f*di/di-f) find d(o) with focal point and d(i)
def mirror_distance_object(focal_point,distance_image):
    """Usage: Find distance of object with focal point and distance of image"""
    numerator = focal_point * distance_image
    denominator = distance_image - focal_point
    return numerator / denominator

#the following equations are variations of m=(hi/ho)=(-di/do)
#find m with h(i) and h(o)
def mirror_mag_h(height_image,height_object):
    """Usage: Find magnification using height of image and height of object"""
    return height_image/ height_object
#find m with d(i) and d(o)
def mirror_mag_d(distance_image,distance_object):
    """Usage: Find magnification using distance of image and distance of object"""
    neg_di = (-1) * distance_image
    return neg_di / distance_object
#find h(i) with m and h(o)
def mirror_hi_m(magnification,height_object):
    """Usage: Find height of image using magnification and height of object"""
    return magnification * height_object
#find h(i) with d(i), d(o), and h(o)
def mirror_hi_hodido(distance_image,distance_object,height_object):
    """Usage: Find height of image using height of object, distance of object and height of object"""
    neg_di = (-1) * distance_image
    numerator = neg_di * height_object
    return numerator / distance_object
#find h(o) with m and h(i)
def mirror_ho_m(height_image,magnification):
    """Usage: Find height of object using magnification"""
    return height_image / magnification
#find h(o) with d(i), d(o), h(i)
def mirror_ho_hidido(distance_image,distance_object,height_image):
    """Usage: Find height of object using height of image, distance of object and height of object"""
    neg_di = (-1) * distance_image
    numerator = height_image * distance_object
    return numerator / neg_di

#PENDULUMS
#T = period
#L = length of string (of pendulum)
#g = grav constant (acceleration of grav)

#T = 2(math.pi)*sqrt(L/g)

#find T with L and g
def time_tlg(length,gravity):
    """Usage: PENDULUMS - Find time using length and gravity"""
    return (2 * math.pi) *(math.sqrt(length / gravity))
#find L with T and g
def length_tlg(time,gravity):
    """Usage: PENDULUMS - Find length using time and gravity"""
    return gravity * (time / (2 * math.pi))**2
#find g with T and L
def gravity_tlg(time,length):
    """Usage: PENDULUMS - Find gravity using time and length"""
    return (2 * math.pi)**2 / time**2

#END OF SIR ERAZ GITHUB

def wave_frequency_t(time_period):
    """Usage: Finding the wave frequency using time period.
    f=1/T"""
    return 1/time_period

def wave_speed_flv(frequency,wave_length):
    """Usage: Finding the wave speed using frequency and wave length.
    v=f×λ"""
    return frequency*wave_length

def frequency_flv(wave_length,wave_speed):
    """Usage: Finding the frequency using wave speed and wave length.
    f=v/λ"""
    return wave_speed/wave_length

def wave_length_flv(frequency,wave_speed):
    """Usage: Finding the wave length using frequency and wave speed.
    λ=v/f"""
    return wave_speed/frequency

def refractive_index_nir(angle_incidence,angle_refraction):
    """Usage: Find refractive index using angle of incidence and angle of refraction"""
    refractive_index_nir_resul=math.sin(angle_incidence)/math.sin(angle_refraction)
    return refractive_index_nir_resul

def angle_incidence_nir(refractive_index,angle_refraction):
    """Usage: Find angle of incidence using refractive index and angle of refraction
    returns in radians"""
    angle_incidence_nir_resul=refractive_index*math.sin(angle_refraction)
    return angle_incidence_nir_resul

def angle_refraction_nir(refractive_index,angle_incidence):
    """Usage: Find angle of refraction using refractive index and angle of incidence
    returns in radians"""
    angle_refraction_nir_resul=math.sin(angle_incidence)/refractive_index
    return angle_refraction_nir_resul



def kinetic_energy_kmv(mass,velocity):
    """Usage: Find kinetic energy from mass and velocity"""
    result = 0.5*(mass*velocity**2)
    return result

def mass_kmv(kinetic_energy,velocity):
    """Usage: Find mass from kinetic energy and velocity"""
    result = (2*kinetic_energy)/velocity**2
    return result

def velocity_kmv(kinetic_energy,mass):
    """Usage: Find velocity from kinetic energy and mass"""
    result = math.sqrt(kinetic_energy/(0.5*mass))
    return result

def GPE_gpemgh(mass,gravity,height):
    """Usage: Find gravitational potential energy from mass, gravity and height"""
    result=mass*gravity*height
    return result

def mass_gpemgh(GPE,gravity,height):
    """Usage: Find mass from gravitational potential energy, gravity and height"""
    result=GPE/gravity*height
    return result

def gravity_gpemgh(GPE,mass,height):
    """Usage: Find gravity from gravitational potential energy, mass and height"""
    result=GPE/mass*height
    return result

def height_gpemgh(GPE,mass,gravity):
    """Usage: Find height from gravitational potential energy, mass and gravity"""
    result=GPE/mass*gravity
    return result

def wave_period_tf(frequency):
    """Usage: Calculate wave period (T) using frequency (f)"""
    return 1/frequency

def wave_period_tlv(wavelength, velocity):
    """Usage: Calculate wave period (T) using wavelength (l) and velocity (v)"""
    return wavelength/velocity

def wavelength_tlv(wave_period, velocity):
    """Usage: Calculate wavelength (l) using wave period (T) and velocity (v)"""
    return wave_period*velocity

def velocity_tlv(wave_period, wavelength):
    """Usage: Calculate velocity (v) using wave period (T) and wave length(l)"""
    return wavelength/wave_period

def fringe_spacing(wavelength, distance_from_slits_to_screen, slit_separation):
    """Usage: Calculate fringe spacing using wavelength (lambda), distance from slits to screen (D) and slit separation (s)"""
    return ((wavelength*distance_from_slits_to_screen)/slit_separation)

def moment_mfd(force, distance_from_pivot):
    """Usage: Calculate moment from force and the perpendicular distance from the pivot"""
    return force*distance_from_pivot

def force_mfd(moment, distance_from_pivot):
    """Usage: Calculate force from moment and the perpendicular distance from the pivot"""
    return moment/distance_from_pivot

def distance_pivot_mfd(moment, force):
    """Usage: Calculate perpendicular distance from the pivot from force and the moment """
    return moment/force

def energy_photon(frequency, wavelength):
    """Usage: Calculate the energy of a photon using frequency and wavelength """
    equation = ((6.62607004e-34 )*3e+8)/wavelength
