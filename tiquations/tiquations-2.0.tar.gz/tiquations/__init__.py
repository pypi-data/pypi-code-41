#!/usr/bin/env python
from .equations import *
from .constants import *
from .planets import *
from .chemistry import *
from .convert import *
import logging
logging.getLogger(__name__).info("Made using Tiquations 2.0")
__author__="Tinos Psomadakis"
__copyright__="Copyright (c) 2019 Tinos Psomadakis"
__credits__ = ["Creme", "Sir Eraz", "Paul Kienzle"]
__version__ = "1.3"
__maintainer__ = "Tinos Psomadakis"
__email__ = "tinosps@gmail.com"
__status__ = "Release"

def help():
    print('''
        https://www.tiquations.com

        A python package containing useful equations for physics, maths, chemistry and computer science.
        Created by Tinos Psomadakis\n
          ''')
    #Commands
    print("Angles are always measured in radians")
    print("All command examples are shown as: tiquations.x with x being the command example prefix")
    print('''
        Commands:

        equations.quadratic(a,b,c) - Find quadratic formula from an equation like 3x^2+6x+2 = 0 where a=3, b=6 and c=2.
        equations.distance_dst(speed,time) - Find distance using speed and time
        equations.speed_dst(distance,time) - Find speed using distance and time
        equations.time_dst(distance,speed) - Find time using distance and speed
        equations.force_fma(mass,acceleration) - Find force using mass and acceleration
        equations.mass_fma(force,acceleration) - Find mass using force and acceleration
        equations.acceleration_fma(force,mass) - Find acceleration using force and mass
        equations.force_fmg(mass,gravitational_field_strength) - Find force using the mass and gravitational field strength
        equations.mass_fmg(force,gravitational_field_strength) - Find mass using the force and gravitational field strength
        equations.gravity_fmg(force,mass) - Find gravitational field strength using force and mass
        equations.weight_wmg(mass, gravitational_field_strength) - Find weight using mass and gravitational field strength
        equations.mass_wmg(weight, gravitational_field_strength) - Find mass using weight and gravitational field strength
        equations.gravity_wmg(weight, mass) - Find gravitational field strength using weight and mass
        equations.circle_area_rad(radius) - Find area of a circle using radius
        equations.circle_area_dia(diameter) - Find area of a circle using diameter
        equations.circle_diam_rad(radius) - Find diameter of a circle using radius
        equations.circle_diam_are(area) - Find diameter of a circle using area
        equations.circle_circum_rad(radius) - Find circumference of a circle
        equations.acceleration_avt(delta_velocity,time) - Find acceleration using change in velocity and time
        equations.delta_velocity_avt(acceleration,time) - Find change in velocity using acceleration and time
        equations.time_avt(acceleration,delta_velocity) - Find time taken using change in velocity and acceleration
        equations.pressure_fpa(force, area) - Find pressure using force and area
        equations.force_fpa(pressure, area) - Find force using pressure and area
        equations.area_fpa(force, pressure) - Find area using force and pressure
        equations.cylinder_vol(radius,height) - Find volume of cylinder
        equations.cylinder_surface_are(radius,height) - Find surface area of cylinder
        equations.trapezoid_area(base_short,base_long,height) - Find area of trapezoid
        equations.trapezoid_height(base_short,base_long,area) - Find height of trapezoid
        equations.trapezoid_surface_are(base_short,base_long,height) - Find surface are of trapezoid
        equations.pythagoras(a=None, b=None, c=None) - Use pythagoras' theorem to solve for a missing side
        equations.energy_evq(voltage,charge) - Find energy using potential difference and charge
        equations.voltage_evq(energy,charge) - Find potential difference using energy and charge
        equations.charge_evq(energy,voltage) - Find charge using energy and potential difference
        equations.power_piv(current, potential_difference) - Find power using current and potential difference
        equations.current_piv(power, potential_difference) - Find current using power and potential difference
        equations.potential_dif_piv(power, current) - Find potential difference using power and current
        equations.power_pet(energy,time) - Find power using energy and time
        equations.energy_pet(power,time) - Find energy using power and time
        equations.time_pet(power,energy) - Find time using power and energy
        equations.sequence_nth(first_term,term_number,common_difference) - Find nth term of sequence
        equations.sequence_first(nth,term_number,common_difference) - Find the first term of a sequence
        equations.sequence_difference(nth,first_term,term_number) - Find difference of a sequence
        equations.sequence_termnum(nth,first_term,common_difference) - Find term number of a sequence
        equations.orbitalspeed_vrt(radius,time) - Find orbital speed using radius and orbit time
        equations.radius_vrt(orbitalspeed,time) - Find radius using orbital speed and orbit time
        equations.orbittime_vrt(orbitalspeed,radius) - Find orbit time using orbital speed and radius
        equations.cosine_side_a(b,c,A_radians) - Find side a using cosine rule
        equations.cosine_side_b(a,c,B_radians) - Find side b using cosine rule
        equations.cosine_side_c(a,b,C_radians) - Find side c using cosine rule
        equations.cosine_angle_A(a,b,c) - Find angle A using cosine rule
        equations.cosine_angle_B(a,b,c) - Find angle B using cosine rule
        equations.cosine_angle_C(a,b,c) - Find angle C using cosine rule
        equations.energy_emc(mass,speedoflight) - Find energy using mass and speed of light
        equations.mass_emc(energy,speedoflight) - Find mass using energy and speed of light
        equations.speedoflight_emc(energy,mass) - Find speed of light using energy and mass. You can also use the light_speed constant.
        equations.schwarzschild(gravity,mass,speedoflight) - Find the Schwarzschild radius of a black hole
        equations.sphere_mass(density,radius) - Find mass of a sphere using density and radius
        equations.sphere_density(mass,radius) - Find density of a sphere using mass and radius
        equations.sphere_radius(mass,density) - Find radius of a sphere using mass and density
        equations.cube_vol(side_length) - Find the volume of a cube using one side
        equations.rectangle_vol(length,width,height) - Find the volume of a rectangle using length, width and height
        equations.sphere_vol(radius) - Find the volume of a sphere using it's radius
        equations.cone_vol(radius,height) - Find the volume of a cone using the radius and height
        equations.pyramid_vol(base_area,height) - Find the volume of a pyramid using the area of the base and height
        equations.wave_frequency_t(time_period) - Find wave frequency using time
        equations.wave_speed_flv(frequency,wave_length) - Find wave speed using frequency and wave speed
        equations.frequency_flv(wave_length,wave_speed) - Find frequency using wave length and wave speed
        equations.wave_length_flv(frequency,wave_speed)  - Find wave length using frequency and wave speed
        equations.refractive_index_nir(angle_incidence,angle_refraction) - Find refractive index using angle of incidence and angle of refraction
        equations.angle_incidence_nir(refractive_index,angle_refraction) - Find angle of incidence using refractive index and angle of angle_refraction
        equations.angle_refraction_nir(refractive_index,angle_incidence) - Find angle of refraction using refractive index and angle of incidence
        equations.kinetic_energy_kmv(mass,velocity) - Find kinetic energy using mass and velocity
        equations.velocity_kmv(kinetic_energy,mass) - Find velocity using kinetic energy and mass
        equations.mass_kmv(kinetic_energy,velocity) - Find mass using kinetic energy and velocity
        equations.GPE_gpemgh(mass,gravity,height) - Find gravitational potential energy using mass, gravity and height
        equations.mass_gpemgh(GPE,gravity,height) - Find mass using gravitational potential energy, gravity and height
        equations.gravity_gpemgh(GPE,mass,height) - Find gravity using gravitational potential energy, mass and height
        equations.height_gpemgh(GPE,mass,gravity) - Find height using gravitational potential energy, mass and gravity
        equations.friction_fnc(normal_force,friction_coefficient) - Find force of friction using normal force and friction coefficent
        equations.normal_fnc(friction_force,friction_coefficient) - Find normal force using force of friction and friction coefficent
        equations.coefficient_fmc(friction_force,normal_force) - Find friction coefficent using force of friction and normal force
        equations.acceleration_aug(friction_coefficient,gravity) - Find acceleration using friction coefficient and gravitational constant
        equations.coefficient_aug(acceleration,gravity) - Find friction coefficient using acceleration and gravitational constant
        equations.gravity_aug(acceleration,friction_coefficient) - Find gravitational constant using acceleration and friction coefficient
        equations.coefficient_cfn(friction,normal) - Find coefficient with friction and normal force
        equations.friction_cfn(coefficient,normal) - Find friction using coefficient and normal force
        equations.normal_cfn(coefficient,friction) - Find normal force using coefficient and friction
        equations.radius_rf(focal_point) -radius with focal point for concave and convex mirrors
        equations.focal_rf(radius) - focal point with radius for concave and convex mirrors
        equations.focal_point(distance_image,distance_object) - Find focal point with distance of image and distance of object
        equations.mirror_distance_image(focal_point,distance_object) - Find distance of image with focal point and distance of object
        equations.mirror_distance_object(focal_point,distance_image) - Find distance of object with focal point and distance of image
        equations.mirror_mag_h(height_image,height_object) - Find magnification using height of image and height of object
        equations.mirror_mag_d(distance_image,distance_object) - Find magnification using distance of image and distance of object
        equations.mirror_hi_m(magnification,height_object) - Find height of image using magnification and height of object
        equations.mirror_hi_hodido(distance_image,distance_object,height_object) - Usage: Find height of image using height of object, distance of object and height of object
        equations.mirror_ho_m(height_image,magnification) - Find height of object using magnification
        equations.mirror_ho_hidido(distance_image,distance_object,height_image) - Find height of object using height of image, distance of object and height of object
        equations.time_tlg(length,gravity) - PENDULUMS: Find time using length and gravity
        equations.length_tlg(time,gravity) - PENDULUMS: Find length using time and gravity
        equations.gravity_tlg(time,length) - PENDULUMS: Find gravity using time and length

        NEW IN TIQUATIONS 2.0

        convert.Kelvin_C(Celsius) - Convert Celsius to Kelvin
        convert.Kelvin_F(Fahrenheit) - Convert Fahrenheit to Kelvin
        convert.Celsius_K(Kelvin) - Convert Kelvin to Celsius
        convert.Celsius_F(Fahrenheit) - Convert Fahrenheit to Celsius
        convert.Fahrenheit_C(Celsius) - Convert Celsius to Fahrenheit
        convert.Fahrenheit_K(Kelvin) - Convert Kelvin to Fahrenheit
        convert.bits(bytes,kilobytes,megabytes,gigabytes,terabytes,petabytes) - Convert to bits using any of the kwargs
        convert.bytes(bits,kilobytes,megabytes,gigabytes,terabytes,petabytes) - Convert to bytes using any of the kwargs
        convert.kilobytes(bits,bytes,megabytes,gigabytes,terabytes,petabytes) - Convert to kilobytes using any of the kwargs
        convert.megabytes(bits,bytes,kilobytes,gigabytes,terabytes,petabytes) - Convert to megabytes using any of the kwargs
        convert.gigabytes(bits,bytes,kilobytes,megabytes,terabytes,petabytes) - Convert to gigabytes using any of the kwargs
        convert.terabytes(bits,bytes,kilobytes,megabytes,gigabytes,petabytes) - Convert to terabytes using any of the kwargs
        convert.petabytes(bits,bytes,kilobytes,megabytes,gigabytes,terabytes) - Convert to petabytes using any of the kwargs
        convert.km_miles(kilometers) - Convert km to miles
        convert.miles_km(miles) - Convert miles to km
        equations.wave_period_tf(frequency) - Calculate wave period using frequency
        equations.wave_period_tlv(wavelength, velocity) - Calculate wave period using wavelength and velocity
        equations.wavelength_tlv(wave_period, velocity) - Calculate wavelength using wave period and velocity
        equations.velocity_tlv(wave_period, wavelength) - Calculate wave period using wave period and wavelength
        equations.fringe_spacing(wavelength, distance_from_slits_to_screen, slit_separation) - Equation to calculate fringe spacing
        equations.moment_mfd(force, distance_from_pivot) - Calculate moment using force and distance from a pivot
        equations.force_mfd(moment, distance_from_pivot) - Calculate force using moment and distance from a pivot
        equations.distance_pivot_mfd(moment, force) - Calculate distance from a pivot using moment and force
        equations.energy_photon(frequency, wavelength) - Calculate the energy of a proton using frequency and wavelength

        Usage:
        hello = tiquations.equations.example_xyz(5,72)
        testing = tiquations.equations.quadratic(1,2,-3)[0]
        world = tiquations.convert.bit_byte(22)

          ''')

    #Built-in variables
    print('''
        planets.py options:

        Planets:

        planets.earth
        planets.moon (I know this isn't a planet)
        planets.mars
        planets.jupiter
        planets.neptune
        planets.mercury
        planets.saturn
        planets.uranus
        planets.venus
        planets.pluto

        Planets constants:

        index - Integer - Position from sun
        gravity - Float - m/s^2
        mass - Float - kg
        radius - Float - km
        surface_area - Float - million km
        sun_distance - Integer - km
        eccentricity - Float
        volume - Float - km^3
        orbital_period - Integer - days

        Example: tiquations.planets.earth.mass

        Other constants:

        constants.speed_of_light = 299792458 m/s
        constants.pi = 3.141592653589793
        constants.eulersnum = 2.7182818284590452353602874713527
        constants.tau = 6.283185307179586
        constants.eulersmasch = 0.577215664901532860606512
        constants.golden_ratio = 1.6180339887498948420
        constants.light_speed = 299792458 m/s
        constants.boltzmann = 1.380649e−23 J/K
        constants.gas_constant = 8.314462618 J/mol K
        constants.luminous_efficacy = 683 lm/W
        constants.atmosphere = 101325 Pa
        constants.avogadro = 6.02214086 * 10^23 mol^-1
        constants.planck = 6.62607004 * 10^-34 m^2 kg / s

                ''')

    print('''
        Chemistry

        chemistry.py

        Usage: tiquations.chemistry.element_name

        Options:
        symbol - String
        atomic_mass - Float
        atomic_number - Integer

        Examples:
        tiquations.chemistry.hydrogen.symbol
        tiquations.chemistry.calcium.atomic_mass
                ''')

def changelog():
    print(
    '''
    Currently running tiquations Version 2.0
    Changelog:

    - Added orbital period to planets
    - Improved documentation for python built-in help(value) command
    - Added tau constant
    - Moved conversion equations to convert.py instead of equations.py
    - Added conversions for bits, bytes, kilobytes, megabytes, gigabytes, terabytes, petabytes
    - Completely rewrote help command and split changelog and help command into the init so you can do tiquations.help() and tiquations.changelog()
    - Added miles - kilometers conversion
    - Added wave period equations using velocity and wavelength
    - Added Planck's constant
    - Changed tiquations.equations.help() to tiquations.help()
    - Changed tiquations.equations.changelog.help() to tiquations.changelog()

    '''
    )
