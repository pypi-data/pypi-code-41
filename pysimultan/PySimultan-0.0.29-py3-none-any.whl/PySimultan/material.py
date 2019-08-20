
import numpy as np
import uuid
import itertools

from PySimultan.base_classes import ObjectBaseClass
# from face import Face as NewFace
# from face import Face


class Part(ObjectBaseClass):

    visible_class_name = 'Part'
    new_part_id = itertools.count(0)

    def __init__(self,
                 name=None,
                 layers=None,
                 part_id=uuid.uuid4(),
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False,
                 is_visible=True,
                 openable=False
                 ):

        super().__init__(id=part_id,
                         pid=next(type(self).new_part_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible
                         )

        self._U_Value = None
        self._G_Value = None
        self._Openable = None
        self._ThermalResistance = None
        self._Layers = None

        if name is None:
            self.Name = 'Part{}'.format(self.PID)
        else:
            self.Name = name

        if layers is None:
            if not MatLayer.get_instances():
                self.Layers = [MatLayer()]
            else:
                self.Layers = [MatLayer.get_instances()[0]]
        else:
            if isinstance(layers, list):
                self.Layers = layers
            else:
                self.Layers = [layers]

        # ------------------------------------------------------
        # Physical Properties
        # ------------------------------------------------------

        self.Openable = openable

        # -----------------------------------------------
        # bindings
        # -----------------------------------------------

        for layer in self.Layers:
            layer.bind_to(self._layer_updated)

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    @property
    def Layers(self):
        return self._Layers

    @Layers.setter
    def Layers(self, value):
        self._default_set_handling('Layers', value)

    @property
    def Openable(self):
        return self._Openable

    @Openable.setter
    def Openable(self, value):
        self._default_set_handling('Openable', value)


    @property
    def ThermalResistance(self):
        if self._ThermalResistance is None:
            self.calc_thermal_resistance()
        return self._ThermalResistance

    @ThermalResistance.setter
    def ThermalResistance(self, value):
        self._default_set_handling('ThermalResistance', value)

    @property
    def U_Value(self):
        if self._U_Value is None:
            self.calc_u_value()
        return self._U_Value

    @U_Value.setter
    def U_Value(self, value):
        self._default_set_handling('U_Value', value)

    @property
    def G_Value(self):
        if self._G_Value is None:
            self.calc_g_value()
        return self._G_Value

    @G_Value.setter
    def G_Value(self, value):
        self._default_set_handling('G_Value', value)

    # --------------------------------------------------------
    # update functions
    # --------------------------------------------------------

    def _layer_updated(self):
        self.print_status('updating part: Layers updated')
        self.calc_thermal_resistance()
        self.calc_u_value()
        self.calc_g_value()

    def calc_thermal_resistance(self):
        self.ThermalResistance = sum([x.ThermalResistance for x in self.Layers])

    def calc_u_value(self, r_si=0.13, r_se=0.04):
        self._U_Value = 1/(self.ThermalResistance + r_si + r_se)

    def calc_g_value(self):

        g_value = 1
        for layer in self.Layers:
            g_value = g_value * layer.Absorption
        self.G_Value = g_value


class Window(Part):

    visible_class_name = 'Window'
    new_window_id = itertools.count(0)

    def __init__(self,
                 face,
                 name=None,
                 part_id=uuid.uuid4(),
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False,
                 is_visible=True,
                 openable=False,
                 u_g=0,
                 u_f=1,
                 psi=0.05,
                 frame_width=0.05,
                 eps=2.5,
                 tau=0.1,
                 rho=0.5,
                 alpha=0.4,
                 number_of_glazings=2,
                 glazing_thickness=0.01
                 ):

        # The hole window is modeled as a face with averaged material data.
        # The window is modeled as one material layer with a thickness of 1 cm of Material 'Glass'
        # The physical properties of the Material are adapted, so that the window can be modeled as homogeneous material
        # To achieve this the thermal conductivity is adapted

        super().__init__(name=name,
                         layers=None,
                         part_id=part_id,
                         color=color,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         openable=openable,
                         pid=next(type(self).new_window_id))

        self._OriginalFace = None
        self._GlassPart = None
        self._GlassFace = None
        self._FramePart = None
        self._FrameFace = None
        self._G_Value = None
        self._FrameWidth = None
        self._NumberOfGlazings = None
        self._GlazingThickness = None
        self._WindowPart = None
        self._WindowLayers = None
        self._WindowMaterials = None
        self._FrameLayers = None
        self._FrameMaterials = None
        self._GlassLayers = None
        self._GlassMaterials = None
        self._U_g = None
        self._U_f = None
        self._Psi = None
        self._Eps = None
        self._Tau = None
        self._Rho = None
        self._Alpha = None

        self.OriginalFace = face
        self.U_g = u_g
        self.U_f = u_f
        self.Psi = psi
        self.Eps = eps
        self.Tau = tau
        self.Rho = rho
        self.Alpha = alpha
        self.FrameWidth = frame_width
        self.NumberOfGlazings = number_of_glazings
        self.GlazingThickness = glazing_thickness

        self.create_window_part()

        self.Layers = self._WindowLayers

    @Part.G_Value.getter
    def G_Value(self):
        if self._G_Value is None:
            self.calc_g_value()
        return self._G_Value

    @property
    def U_Value(self, a_g, a_f, l_g):
        return self.calc_u_value(a_g=a_g, a_f=a_f, l_g=l_g)

    @property
    def U_g(self):
        return self._U_g

    @U_g.setter
    def U_g(self, value):
        if (value > 1) or (value < 0):
            raise ValueError('U_g value can not be grater than 1 or less than 0')
        self._default_set_handling('U_g', value)

    @property
    def U_f(self):
        return self._U_f

    @U_f.setter
    def U_f(self, value):
        if (value > 1) or (value < 0):
            raise ValueError('U_f value can not be grater than 1 or less than 0')
        self._default_set_handling('U_f', value)

    @property
    def Psi(self):
        return self._Psi

    @Psi.setter
    def Psi(self, value):
        if (value > 1) or (value < 0):
            raise ValueError('Psi value can not be grater than 1 or less than 0')
        self._default_set_handling('Psi', value)

    @property
    def FrameWidth(self):
        return self._FrameWidth

    @FrameWidth.setter
    def FrameWidth(self, value):
        self._default_set_handling('FrameWidth', value)

    @property
    def FramePart(self,
                  a_f=1,
                  l_g=1,
                  thermal_conductivity=0.19,
                  density=1380,
                  heat_capacity=840,
                  solar_absorption_coefficient=0.5):
        if self._FramePart is None:
            self.create_frame_part(a_f=a_f,
                                   l_g=l_g,
                                   thermal_conductivity=thermal_conductivity,
                                   density=density,
                                   heat_capacity=heat_capacity,
                                   solar_absorption_coefficient=solar_absorption_coefficient)
        return self._FramePart

    @FramePart.setter
    def FramePart(self, value):
        self._default_set_handling('FramePart', value)

    @property
    def GlassPart(self,
                  thermal_conductivity=0.96,
                  density=2500,
                  heat_capacity=840,
                  solar_absorption_coefficient=0.1):

        if self._GlassPart is None:
            self.create_glass_part(thermal_conductivity=thermal_conductivity,
                                   density=density,
                                   heat_capacity=heat_capacity,
                                   solar_absorption_coefficient=solar_absorption_coefficient)
        return self._GlassPart

    @GlassPart.setter
    def GlassPart(self, value):
        self._default_set_handling('GlassPart', value)

    @property
    def OriginalFace(self):
        return self._OriginalFace

    @OriginalFace.setter
    def OriginalFace(self, value):
        self._default_set_handling('OriginalFace', value)

    @property
    def GlassFace(self):
        if self._GlassFace is None:
            self.create_glass_face()
        return self._GlassFace

    @GlassFace.setter
    def GlassFace(self, value):
        self._default_set_handling('GlassFace', value)

    @property
    def FrameFace(self):
        if self._FrameFace is None:
            self.create_frame_face()
        return self._GlassFace

    @FrameFace.setter
    def FrameFace(self, value):
        self._default_set_handling('FrameFace', value)

    def calc_u_value(self, a_g=1, a_f=1, l_g=1):
        """
        calculate the u-value of the window
        :param a_g: area of the glass [m²]
        :param a_f: area of the frame [m²]
        :param l_g: circumference of the face [m]
        :return: u-value of the window [W/m²K]
        """
        u_value = (a_g * self.U_g + a_f * self.U_f + l_g * self.Psi) / (a_g + a_f)
        return u_value

    def create_frame_part(self,
                          a_f=1,
                          l_g=1,
                          thermal_conductivity=0.19,
                          density=1380,
                          heat_capacity=840,
                          solar_absorption_coefficient=0.5):

        thermal_resistance_frame = 1 / ((1 / ((self.U_f + l_g * self.Psi) / a_f)) - 0.14)

        frame_material = Material(name='FrameMaterial_{}'.format(self.Name),
                                  density=density,
                                  heat_capacity=heat_capacity,
                                  thermal_conductivity=thermal_conductivity,
                                  transparent=False,
                                  solar_absorption_coefficient=solar_absorption_coefficient,
                                  g_value=0,
                                  wvdrf=20,
                                  w20=0,
                                  w80=0)

        frame_layer = MatLayer(material=frame_material, thickness=thermal_resistance_frame * thermal_conductivity)
        self._FramePart = Part(name='FramePart_{}'.format(self.Name),
                               layers=frame_layer)

        self._FrameLayers = frame_layer
        self._FrameMaterials = frame_material

        # return frame_material, frame_layer, self._FramePart

    def create_window_part(self,
                           thermal_conductivity=0.96,
                           density=2500,
                           heat_capacity=840,
                           solar_absorption_coefficient=0.1
                           ):
        mean_u_value = self.calc_u_value(a_g=self.GlassFace.Area, a_f=self.FrameFace.Area, l_g=self.FrameFace.Circumference)
        mean_g_value = self.G_Value
        thermal_resistance_window = 1 / ((1 / mean_u_value) - 0.14)
        absorption_coefficient = 0
        materials = list()

        window_glazing_material = Material(name='WindowGlazingMaterial1_{}'.format(self.Name),
                                           density=density,
                                           heat_capacity=heat_capacity,
                                           thermal_conductivity=thermal_conductivity,
                                           transparent=True,
                                           solar_absorption_coefficient=solar_absorption_coefficient,
                                           absorption_coefficient=0,
                                           wvdrf=999999,
                                           w20=0,
                                           w80=0)
        materials.append(window_glazing_material)

        window_air_material = Material(name='WindowMaterialAir_{}'.format(self.Name),
                                       density=1.4,
                                       heat_capacity=1.0,
                                       thermal_conductivity=0.026,
                                       transparent=True,
                                       solar_absorption_coefficient=0,
                                       absorption_coefficient=0,
                                       g_value=1,
                                       wvdrf=1,
                                       w20=0,
                                       w80=0)

        thermal_resistance_glazing = (self._NumberOfGlazings * self._GlazingThickness) / thermal_conductivity

        materials.append(window_air_material)
        window_layers = list()
        window_layers.append(MatLayer(material=window_glazing_material, thickness=self._GlazingThickness))
        for i in range(self._NumberOfGlazings - 1):
            window_layers.append(MatLayer(material=window_air_material,
                                          thickness=((thermal_resistance_window - thermal_resistance_glazing) * 0.026) / (self._NumberOfGlazings - 1)
                                          )
                                 )
            window_layers.append(MatLayer(material=window_glazing_material, thickness=self._GlazingThickness))

        window_part = Part(name='WindowPart_{}'.format(self.Name),
                           layers=window_layers)

        self._WindowPart = window_part
        self._WindowLayers = window_layers
        self._WindowMaterials = materials

        # return window_part, window_layers, materials

    def create_glass_part(self,
                          thermal_conductivity=0.96,
                          density=2500,
                          heat_capacity=840,
                          solar_absorption_coefficient=0.1
                          ):

        thermal_resistance_window = 1 / ((1 / self.U_g) - 0.14)

        glass_materials = list()

        glazing_material = Material(name='WindowGlazingMaterial1_{}'.format(self.Name),
                                    density=density,
                                    heat_capacity=heat_capacity,
                                    thermal_conductivity=thermal_conductivity,
                                    transparent=True,
                                    solar_absorption_coefficient=solar_absorption_coefficient,
                                    g_value=self.G_Value**(1/self._NumberOfGlazings),
                                    wvdrf=999999,
                                    w20=0,
                                    w80=0)

        glass_materials.append(glazing_material)

        air_material = Material(name='WindowMaterialAir_{}'.format(self.Name),
                                density=1.4,
                                heat_capacity=1.0,
                                thermal_conductivity=0.026,
                                transparent=True,
                                solar_absorption_coefficient=0,
                                g_value=1,
                                wvdrf=1,
                                w20=0,
                                w80=0)

        glass_materials.append(air_material)

        thermal_resistance_glazing = (self._NumberOfGlazings * self._GlazingThickness) / thermal_conductivity

        glass_layers = list()
        glass_layers.append(MatLayer(material=glazing_material, thickness=self._GlazingThickness))
        for i in range(self._NumberOfGlazings - 1):
            glass_layers.append(MatLayer(material=air_material,
                                          thickness=((thermal_resistance_window - thermal_resistance_glazing) * 0.026 / (self._NumberOfGlazings - 1))
                                          )
                                 )
            glass_layers.append(MatLayer(material=glazing_material, thickness=self._GlazingThickness))

        glass_part = Part(name='WindowPart_{}'.format(self.Name),
                           layers=glass_layers)

        self._GlassPart = glass_part
        self._GlassLayers = glass_layers
        self._GlassMaterials = glass_materials

        # return glass_part, glass_layers, glass_materials

    def create_glass_face(self):

        self.print_status('creating_glass_face')
        # create vertices:
        face = self.OriginalFace.create_offset_face(offset=-self.FrameWidth)
        # face.Part = self.GlassPart
        self.GlassFace = face
        self.GlassFace.Part = self.GlassPart

    def create_frame_face(self):
        from PySimultan.face import Face
        hole_face = Face(boundary=self.GlassFace.Boundary,
                         orientation=self.OriginalFace.Orientation)

        face = Face(boundary=self.OriginalFace.Boundary,
                    holes=hole_face,
                    orientation=self.OriginalFace.Orientation,
                    part=None)
        self.FrameFace = face
        self.FrameFace.Part = self.FramePart

    def calc_g_value(self):
        self.G_Value = (self.GlassFace.Area * self.GlassFace.Part.G_Value) / (self.GlassFace.Area + self.FrameFace.Area)


class Material(ObjectBaseClass):

    new_material_id = itertools.count(0)
    visible_class_name = 'Material'

    def __init__(self,
                 name=None,
                 material_id=uuid.uuid4(),
                 color=np.append(np.random.rand(1, 3), 0) * 255,
                 density=1000,                  # kg / m^3
                 heat_capacity=1000,            # specific heat capacity [J /(kg K)]
                 thermal_conductivity=1,        # W /(m K)
                 transparent=False,             # material is transparent
                 emission_coefficient=0.93,      # emission coefficient
                 solar_absorption_coefficient=0.5,
                 refractive_index=1,            # m/m
                 absorption_coefficient=1,      # 1/m
                 scattering_coefficient=0,      # 1/m
                 dynamic_viscosity=999999,      # kg/(m*s)
                 thermodynamic_state=0,         # 0: solid, 1: liquid, 2: gas
                 wvdrf=9999999,
                 w20=1,
                 w80=5):
        """

        :param name:                    Name of the Material,
                                        Format: string
                                        Default Value: uuid.uuid4()
        :param material_id:             ID of the Material
                                        Format: string, int, uuid
                                        Default Value:
        :param color:                   Color of the Material; the color is a 4x0 np.array, where the first three
                                        entries are rgb-Values (0-255), the fourth value is the opacity. The opacity
                                        can be in range from 0 to 1, where 0 means opaque, 1 is not opaque
                                        Example: np.array([125,255,0,1])
                                        Default Value: np.append(np.random.rand(1, 3), 0) * 255
        :param density:                 density of the material (dry)
                                        Units: [kg/m³]
                                        Format: float64
                                        Default Value: 1000
        :param heat_capacity:           specific heat capacity of the material at constant pressure
                                        Units: [J/(kg*K)]
                                        Format: float64
                                        Default Value: 1000
        :param thermal_conductivity:    Thermal conductivity of the material
                                        Units: [W/(m*K)]]
                                        Format: float64
                                        Default Value: 1
        :param transparent:             Transparent Material; True means the material is transparent, False means not
                                        Units: [-]
                                        Format: bool
                                        Default Value: False
        :param emission_coefficient:    Hemispherical emissivity e of a surface, e = Me / Me° where Me is the radiant
                                        exitance of that surface; Me° is the radiant exitance of a black body at
                                        the same temperature as that surface.
                                        Units: [-]
                                        Format: float64
                                        Default Value: 0.93
        :param solar_absorption_coefficient:
                                        Units: [-]
                                        Format: float64
                                        Default Value: 0.5
        :param refractive_index:        The refractive index is the ratio of speed of light in the medium to the speed
                                        of light in vacuum. It is by default set to 1
                                        Units: [-]
                                        Format: float64
                                        Default Value: 1
        :param absorption_coefficient:  If there are only absorption effects,
                                        then Lambert’s Law of absorption applies:
                                        I = I0 exp(-a*x)
                                        where I is the radiation intensity,
                                        a is the absorption coefficient,
                                        and x is the distance through the material.
                                        Units: [1/m]
                                        Format: float64
                                        Default Value: 9999
        :param scattering_coefficient:  The scattering coefficient is, by default, set to zero,
                                        and it is assumed to be isotropic
                                        Units: [1/m]
                                        Format: float64
                                        Default Value: 0
        :param dynamic_viscosity:       Dynamic viscosity (), also called absolute viscosity, is a measure of the
                                        resistance of a fluid to shearing forces, and appears in the momentum equations.
                                        Units: [kg/(m*s)]
                                        Format: float64
                                        Default Value: 0
        :param thermodynamic_state:     This parameter sets the state of a substance to solid, liquid or gas.
                                        0: solid, 1: liquid, 2: gas
                                        There are certain limitations imposed by selecting a particular state.
                                        For example, a solid must always have at least density, specific heat capacity
                                        and thermal conductivity specified.
                                        Units: [-]
                                        Format: int; 0,1,2
                                        Default Value: 0
        :param wvdrf:                   Water Vapor Diffusion Resistance Factor, µ-value
                                        Units: [-]
                                        Format: float64
                                        Default Value: 99999999
        :param w20:                     Units: [kg/m³]
                                        Format: float64
        :param w80:                     Units: [kg/m³]
                                        Format: float64
        """

        super().__init__(id=material_id,
                         pid=next(type(self).new_material_id),
                         color=color,
                         name=name
                         )

        self._Density = None
        self._HeatCapacity = None
        self._ThermalConductivity = None
        self._EmissionCoefficient = None
        self._SolarAbsorptionCoefficient = None
        self._Transparent = None
        self._WaterVaporDiffusionResistanceFactor = None
        self._w20 = None
        self._w80 = None
        self._RefractiveIndex = None
        self._AbsorptionCoefficient = None
        self._ScatteringCoefficient = None
        self._DynamicViscosity = None
        self._ThermodynamicState = None

        # ------------------------------------------------------------------------------------
        # set values:
        # -------------------------------------------------------------------------------------
        self.PID = next(self.new_id)

        if name is None:
            self.Name = 'DefaultMaterial{}'.format(self.PID)
        else:
            self.Name = name

        # ------------------------------------------------------
        # physical properties:
        # -----------------------------------------------------
        self.Density = density                                             # kg/m³
        self.HeatCapacity = heat_capacity                                  # J/kg K
        self.ThermalConductivity = thermal_conductivity                    # W/m K
        self.EmissionCoefficient = emission_coefficient                    # -
        self.SolarAbsorptionCoefficient = solar_absorption_coefficient     # -
        self.Transparent = transparent                                     # true/false
        self.WaterVaporDiffusionResistanceFactor = wvdrf                   # -
        self.w20 = w20
        self.w80 = w80

        self.RefractiveIndex = refractive_index
        self.AbsorptionCoefficient = absorption_coefficient                # If there are only absorption effects,
                                                                            # then Lambert’s Law of absorption applies:
                                                                            # I = I0 exp(-a*x)
                                                                            # where I is the radiation intensity,
                                                                            # a is the absorption coefficient,
                                                                            # and x is the distance through the material.
        self.ScatteringCoefficient = scattering_coefficient
        self.DynamicViscosity = dynamic_viscosity
        self.ThermodynamicState = thermodynamic_state

    # ------------------------------------------------------
    # physical properties:
    # -----------------------------------------------------

    @property
    def RefractiveIndex(self):
        return self._RefractiveIndex

    @RefractiveIndex.setter
    def RefractiveIndex(self, value):
        if (value < 1) or (value > 1000):
            raise ValueError('RefractiveIndex can not be grater than 1000 or less than 1')
        self._default_set_handling('RefractiveIndex', value)

    @property
    def AbsorptionCoefficient(self):
        return self._AbsorptionCoefficient

    @AbsorptionCoefficient.setter
    def AbsorptionCoefficient(self, value):
        if value < 0:
            raise ValueError('RefractiveIndex can not be less than 0')
        self._default_set_handling('AbsorptionCoefficient', value)

    @property
    def ScatteringCoefficient(self):
        return self._ScatteringCoefficient

    @ScatteringCoefficient.setter
    def ScatteringCoefficient(self, value):
        if value < 0:
            raise ValueError('ScatteringCoefficient can not be less than 0')
        self._default_set_handling('ScatteringCoefficient', value)

    @property
    def DynamicViscosity(self):
        return self._DynamicViscosity

    @DynamicViscosity.setter
    def DynamicViscosity(self, value):
        if value < 0:
            raise ValueError('DynamicViscosity can not be less than 0')
        self._default_set_handling('DynamicViscosity', value)

    @property
    def ThermodynamicState(self):
        return self._ThermodynamicState

    @ThermodynamicState.setter
    def ThermodynamicState(self, value):
        if not isinstance(value, int):
            raise ValueError('ThermodynamicState must be integer. 0: solid, 1: liquid, 2:gas')
        if (value < 0) or (value > 2):
            raise ValueError('ThermodynamicState can must be 0, 1 or 2.')
        self._default_set_handling('ThermodynamicState', value)


    @property
    def Density(self):
        return self._Density

    @Density.setter
    def Density(self, value):
        if (value > 100000) or (value < 0):
            raise ValueError('Density can not be grater than 100000 or less than 0')
        self._default_set_handling('Density', value)

    @property
    def HeatCapacity(self):
        return self._HeatCapacity

    @HeatCapacity.setter
    def HeatCapacity(self, value):
        if (value > 1000000) or (value < 0):
            raise ValueError('HeatCapacity can not be grater than 1000000 or less than 0')
        self._default_set_handling('HeatCapacity', value)

    @property
    def ThermalConductivity(self):
        return self._ThermalConductivity

    @ThermalConductivity.setter
    def ThermalConductivity(self, value):
        if (value > 1000000) or (value < 0):
            raise ValueError('ThermalConductivity can not be grater than 1000000 or less than 0')
        self._default_set_handling('ThermalConductivity', value)

    @property
    def Transparent(self):
        return self._Transparent

    @Transparent.setter
    def Transparent(self, value):
        if not isinstance(value, bool):
            raise ValueError('Transparent can only be boolean value')
        self._default_set_handling('Transparent', value)

    @property
    def EmissionCoefficient(self):
        return self._EmissionCoefficient

    @EmissionCoefficient.setter
    def EmissionCoefficient(self, value):
        if (value > 1) or (value < 0):
            raise ValueError('EmissionCoefficient value can not be grater than 1 or less than 0')
        self._default_set_handling('EmissionCoefficient', value)

    @property
    def SolarAbsorptionCoefficient(self):
        return self._SolarAbsorptionCoefficient

    @SolarAbsorptionCoefficient.setter
    def SolarAbsorptionCoefficient(self, value):
        if (value > 1) or (value < 0):
            raise ValueError('SolarAbsorptionCoefficient value can not be grater than 1 or less than 0')
        self._default_set_handling('SolarAbsorptionCoefficient', value)

    @property
    def WaterVaporDiffusionResistanceFactor(self):
        return self._WaterVaporDiffusionResistanceFactor

    @WaterVaporDiffusionResistanceFactor.setter
    def WaterVaporDiffusionResistanceFactor(self, value):
        self._default_set_handling('WaterVaporDiffusionResistanceFactor', value)

    @property
    def w20(self):
        return self._w20

    @w20.setter
    def w20(self, value):
        self._default_set_handling('w20', value)

    @property
    def w80(self):
        return self._w80

    @w80.setter
    def w80(self, value):
        self._default_set_handling('w80', value)

    # --------------------------------------------------------
    # observed object change callbacks
    # --------------------------------------------------------


class MatLayer(ObjectBaseClass):

    new_matlayer_id = itertools.count(0)
    visible_class_name = 'Material Layer'

    def __init__(self,
                 mat_layer_id=uuid.uuid4(),
                 name=None,
                 color=np.append(np.random.rand(1, 3), 0) * 255,
                 material=None,
                 thickness=0.1
                 ):

        super().__init__(id=mat_layer_id,
                         pid=next(type(self).new_matlayer_id),
                         color=color,
                         name=name
                         )

        self._Material = None
        self._Thickness = None
        self._ThermalResistance = None
        self._Absorption = None

        if name is None:
            self.Name = 'DefaultLayer{}'.format(self.PID)
        else:
            self.Name = name

        if material is None:
            if not Material.get_instances():
                self.Material = [Material()]
            else:
                self.Material = [Material.get_instances()[0]]
        else:
            if not isinstance(material, list):
                self.Material = [material]
            else:
                self.Material = material

        self.Thickness = thickness
        self.ThermalResistance = None
        self.Absorption = None

        # --------------------------------------------------------
        # bind observed objects
        # --------------------------------------------------------

        if isinstance(self._Material, list):
            for material in self._Material:
                material.bind_to(self.material_updated)
        else:
            self._Material.bind_to(self.material_updated)

    # ------------------------------------------------------
    # physical properties:
    # -----------------------------------------------------

    @property
    def Thickness(self):
        return self._Thickness

    @Thickness.setter
    def Thickness(self, value):
        self._default_set_handling('Thickness', value)

    @property
    def Material(self):
        return self._Material

    @Material.setter
    def Material(self, value):
        self._default_set_handling('Material', value)

    @property
    def ThermalResistance(self):
        if self._ThermalResistance is None:
            self.calc_thermal_resistance()
        return self._ThermalResistance

    @ThermalResistance.setter
    def ThermalResistance(self, value):
        if not(value is None):
            if value < 0:
                raise ValueError('ThermalResistance can not be less than 0')
        self._default_set_handling('ThermalResistance', value)

    @property
    def Absorption(self):
        if self._Absorption is None:
            self.calc_absorption()
        return self._Thickness

    @Absorption.setter
    def Absorption(self, value):
        self._default_set_handling('Absorption', value)

    def calc_thermal_resistance(self):
        self.ThermalResistance = self.Thickness / self.Material.ThermalConductivity

    def calc_absorption(self):
        """
        I = I0 exp(-ax)
        where I is the radiation intensity, a is the absorption coefficient, and x is the distance through the material.
        self.Absorption = exp(-ax)
        :return:
        """
        self.Absorption = np.exp(self.Material.AbsorptionCoefficient * self.Thickness)

    def material_updated(self):
        self.calc_thermal_resistance()






