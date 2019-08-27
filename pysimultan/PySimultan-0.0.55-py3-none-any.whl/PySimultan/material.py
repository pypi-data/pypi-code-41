
import numpy as np
import uuid
import itertools

from PySimultan.base_classes import ObjectBaseClass
from PySimultan import settings
# from face import Face as NewFace
# from face import Face


def create_random_color():
    return np.append(np.random.rand(1, 3), 0)*255


class Part(ObjectBaseClass):

    visible_class_name = 'Component'
    new_part_id = itertools.count(0)

    def __init__(self,
                 name=None,
                 layers=None,
                 part_id=None,
                 color=None,
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

        self._Openable = openable

        # -----------------------------------------------
        # bindings
        # -----------------------------------------------

        for layer in self.Layers:
            layer.bind_to(self._layer_updated)

        # add to the collection
        settings.building_collection.Part_collection.append(self)

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

    def _layer_updated(self, ChangedAttribute=None):
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
            if layer.Transparent:
                g_value = g_value - g_value * (layer.Absorption)
            else:
                g_value = 0
        self.G_Value = g_value


class Window(Part):

    visible_class_name = 'Window'
    new_window_id = itertools.count(0)

    def __init__(self,
                 face,
                 name=None,
                 part_id=None,
                 color=None,
                 color_from_parent=False,
                 is_visible=True,
                 openable=False,
                 u_g=0,
                 u_f=1,
                 g_value=0.6,
                 psi=0.05,
                 frame_width=0.05,
                 eps=2.5,
                 tau_e=None,
                 q_i=None,  # secondary heat dissipation to inside
                 tau_uv=None,
                 rho_e=None,
                 alpha_e=None,
                 number_of_glazings=2,
                 glazing_thickness=0.01
                 ):
        """

        :param face:
        :param name:
        :param part_id:
        :param color:
        :param color_from_parent:
        :param is_visible:
        :param openable:    window is openable or not
        :param u_g: u-value of the glass
        :param u_f: u-value of the frame
        :param g_value: solar transmittance through the hole part:
                        g-value = total solar heat gain / incident solar radiation
        :param psi: factor for heat loss calculation over frame; heat loss per metre (circumference) [W/m*K]
        :param frame_width: width of the window-frame [m]
        :param eps: correction factor for angle-dependent g-value
        :param tau_e: total Radiation transmission trough the glass [-]
        :param rho_e: total Radiation reflectance of the glass [-]
        :param alpha_e: total Radiation absorption of the glass [-]
        :param number_of_glazings:  [-]
        :param glazing_thickness:   thickness of the glazing panes [m]
        :param q_i: secondary heat dissipation to inside
        """

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
                         openable=openable)

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
        self._Tau_e = None
        self._Rho_e = None
        self._Alpha_e = None
        self._Q_i = None
        self._Tau_uv = None

        self.OriginalFace = face
        self.Q_i = q_i
        self.Tau_uv = tau_uv
        self.U_g = u_g
        self.U_f = u_f
        self.G_Value = g_value
        self.Psi = psi
        self.Eps = eps
        self.Tau_e = tau_e
        self.Rho_e = rho_e
        self.Alpha_e = alpha_e
        self.FrameWidth = frame_width
        self.NumberOfGlazings = number_of_glazings
        self.GlazingThickness = glazing_thickness

        self.create_window_part()

        self.Layers = self._WindowLayers

        # add to the collection
        settings.building_collection.Window_collection.append(self)

    @property
    def Eps(self):
        return self._Eps

    @Eps.setter
    def Eps(self, value):
        if value is not None:
            if (value > 5) or (value < 0):
                raise ValueError('Eps_e value can not be grater than 5 or less than 0')
        self._default_set_handling('Eps_e', value)

    @property
    def GlazingThickness(self):
        return self._GlazingThickness

    @GlazingThickness.setter
    def GlazingThickness(self, value):
        if value is not None:
            if value < 0:
                raise ValueError('GlazingThickness value can not be less than 0')
        self._default_set_handling('GlazingThickness', value)

    @property
    def Tau_e(self):
        if self._Tau_e is None:
            if (self._Rho_e is None) and (self._Alpha_e is None):
                self.Tau_e = 0.9 * self.G_Value                 # transmission
                self.Rho_e = 0.3 * self._Tau_e                   # reflection
                self.Alpha_e = 1 - self._Tau_e - self._Rho_e      # absorption

            elif self._Rho_e is None:
                self.Tau_e = 0.9 * self.G_Value                 # transmission
                self.Rho_e = 1 - self._Tau_e - self.Alpha_e      # reflection
            elif self._Alpha_e is None:
                self.Tau_e = 0.9 * self.G_Value                 # transmission
                self.Alpha_e = 1 - self._Tau_e - self._Rho_e      # reflection
            else:
                self.Tau_e = 1 - self.Rho_e - self.Alpha_e

            # check if Q_i is higher than absorption (1 - self.Tau_e - self.Rho_e):
            if (1 - self.Tau_e - self.Rho_e) < self.Q_i:
                raise ValueError('Attention! Q_i can not be higher than Absorption!')

        return self._Tau_e

    @Tau_e.setter
    def Tau_e(self, value):
        if value is not None:
            if (value > 1) or (value < 0):
                raise ValueError('Tau_e value can not be grater than 1 or less than 0')
        self._default_set_handling('Tau_e', value)

    @property
    def Rho_e(self):
        if self._Rho_e is None:
            if (self._Tau_e is None) and (self._Alpha_e is None):
                self.Tau_e = 0.9 * self.G_Value  # transmission
                self.Rho_e = 0.3 * self.Tau_e  # reflection
                self.Alpha_e = 1 - self.Tau_e - self._Rho_e  # absorption

            elif self._Tau_e is None:
                self.Tau_e = 0.9 * self.G_Value  # transmission
                self.Rho_e = 1 - self.Tau_e - self.Alpha_e  # reflection

            elif self.Alpha_e is None:
                self.Tau_e = 0.9 * self.G_Value  # transmission
                self.Alpha_e = 1 - self.Tau_e - self.Rho_e  # reflection
            else:
                self.Tau_e = 1 - self.Rho_e - self.Alpha_e

            # check if Q_i is higher than absorption (1 - self.Tau_e - self.Rho_e):
            if (1 - self.Tau_e - self.Rho_e) < self.Q_i:
                raise ValueError('Attention! Q_i can not be higher than Absorption!')

        return self._Rho_e

    @Rho_e.setter
    def Rho_e(self, value):
        if value is not None:
            if (value > 1) or (value < 0):
                raise ValueError('Rho_e value can not be grater than 1 or less than 0')
        self._default_set_handling('Rho_e', value)

    @property
    def Alpha_e(self):
        return self._Alpha_e

    @Alpha_e.setter
    def Alpha_e(self, value):
        if value is not None:
            if (value > 1) or (value < 0):
                raise ValueError('Alpha_e value can not be grater than 1 or less than 0')
        self._default_set_handling('Alpha_e', value)

    @property
    def Q_i(self):
        if self._Q_i is None:
            if self.G_Value is not None:
                self.Q_i = 0.1 * self.G_Value
            else:
                self.Q_i = 0
        return self._Q_i

    @Q_i.setter
    def Q_i(self, value):
        if value is not None:
            if (value > 1) or (value < 0):
                raise ValueError('Q_i value can not be grater than 1 or less than 0')
        self._default_set_handling('Q_i', value)

    @property
    def Tau_uv(self):
        return self._Tau_uv

    @Tau_uv.setter
    def Tau_uv(self, value):
        if value is not None:
            if (value > 1) or (value < 0):
                raise ValueError('Tau_uv value can not be grater than 1 or less than 0')
        self._default_set_handling('Tau_uv', value)

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
        if (value > 10000) or (value < 0):
            raise ValueError('U_g value can not be grater than 10000 or less than 0')
        self._default_set_handling('U_g', value)

    @property
    def U_f(self):
        return self._U_f

    @U_f.setter
    def U_f(self, value):
        if (value > 10000) or (value < 0):
            raise ValueError('U_f value can not be grater than 10000 or less than 0')
        self._default_set_handling('U_f', value)

    @property
    def Psi(self):
        return self._Psi

    @Psi.setter
    def Psi(self, value):
        if (value > 1000) or (value < 0):
            raise ValueError('Psi value can not be grater than 1000 or less than 0')
        self._default_set_handling('Psi', value)

    @property
    def FrameWidth(self):
        return self._FrameWidth

    @FrameWidth.setter
    def FrameWidth(self, value):
        self._default_set_handling('FrameWidth', value)

    @property
    def WindowPart(self):
        return self._WindowPart

    @WindowPart.setter
    def WindowPart(self, value):
        self._default_set_handling('WindowPart', value)
        if self._WindowPart is not None:
            self.OriginalFace.Part = self._WindowPart

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
        if self._FramePart is not None:
            self.FrameFace.Part = self._FramePart

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
        if self._GlassPart is not None:
            self.GlassFace.Part = self._GlassPart

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
                                  color=create_random_color(),
                                  density=density,
                                  heat_capacity=heat_capacity,
                                  thermal_conductivity=thermal_conductivity,
                                  transparent=False,
                                  solar_absorption_coefficient=solar_absorption_coefficient,
                                  absorption_coefficient=999999,
                                  wvdrf=20,
                                  w20=0,
                                  w80=0)

        frame_layer = MatLayer(material=frame_material, thickness=thermal_resistance_frame * thermal_conductivity)
        self.FramePart = Part(name='FrameComponent {}'.format(self.Name),
                              layers=frame_layer,
                              color=create_random_color())

        self._FrameLayers = frame_layer
        self._FrameMaterials = frame_material

        # return frame_material, frame_layer, self._FramePart

    def create_window_part(self,
                           thermal_conductivity=0.96,
                           density=2500,
                           heat_capacity=840,
                           solar_absorption_coefficient=0.1
                           ):
        """

        # glass properties:
        # https://refractiveindex.info/?shelf=glass&book=BK7&page=SCHOTT

        :param thermal_conductivity:
        :param density:
        :param heat_capacity:
        :param solar_absorption_coefficient:
        :return:
        """
        mean_u_value = self.calc_u_value(a_g=self.GlassFace.Area, a_f=self.FrameFace.Area, l_g=self.FrameFace.Circumference)
        mean_g_value = (self.G_Value * self.GlassFace.Area) / self.OriginalFace.Area
        thermal_resistance_window = 1 / ((1 / mean_u_value) - 0.14)
        absorption_coefficient = 0
        materials = list()

        window_glazing_material = self.create_glazing_mat()

        materials.append(window_glazing_material)

        window_air_material = self.create_air_mat()

        thermal_resistance_glazing = (self.NumberOfGlazings * self.GlazingThickness) / thermal_conductivity

        materials.append(window_air_material)
        window_layers = list()
        window_layers.append(MatLayer(material=window_glazing_material, thickness=self.GlazingThickness))

        for i in range(self.NumberOfGlazings - 1):
            window_layers.append(MatLayer(material=window_air_material,
                                          thickness=((thermal_resistance_window - thermal_resistance_glazing) * 0.026) / (self.NumberOfGlazings - 1)
                                          )
                                 )
            window_layers.append(MatLayer(material=window_glazing_material, thickness=self.GlazingThickness))

        window_part = Part(name='WindowComponent {}'.format(self.Name),
                           layers=window_layers,
                           color=create_random_color())

        self.OriginalFace.Part = window_part

        self.WindowPart = window_part
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

        glazing_material = self.create_glazing_mat()

        glass_materials.append(glazing_material)

        air_material = self.create_air_mat()

        glass_materials.append(air_material)

        thermal_resistance_glazing = (self.NumberOfGlazings * self.GlazingThickness) / thermal_conductivity

        glass_layers = list()
        glass_layers.append(MatLayer(material=glazing_material, thickness=self.GlazingThickness))
        for i in range(self.NumberOfGlazings - 1):
            glass_layers.append(MatLayer(material=air_material,
                                         thickness=((thermal_resistance_window - thermal_resistance_glazing) * 0.026 / (self.NumberOfGlazings - 1))
                                         )
                                )
            glass_layers.append(MatLayer(material=glazing_material, thickness=self.GlazingThickness))

        glass_part = Part(name='GlassComponent {}'.format(self.Name),
                          layers=glass_layers,
                          color=np.array([0, 0, 255, 0]))

        self.GlassPart = glass_part
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
        # hole_face = Face(boundary=self.GlassFace.Boundary,
        #                  orientation=self.OriginalFace.Orientation)

        face = Face(boundary=self.OriginalFace.Boundary,
                    holes=self.GlassFace.Boundary,
                    orientation=self.OriginalFace.Orientation,
                    part=None)
        self.FrameFace = face
        # Check:
        MaxError = 0.05
        TotalArea = abs(self.GlassFace.Area + face.Area)
        if ((TotalArea / self.OriginalFace.Area) > (1+MaxError)) or ((TotalArea / self.OriginalFace.Area) < (1-MaxError)):
            raise ValueError('Sum of frame and glass area differs more than {error} % from original face.'.format(error=MaxError * 100))
        self.FrameFace.Part = self.FramePart

    def calc_g_value(self):
        self.G_Value = (self.GlassFace.Area * self.GlassFace.Part.G_Value) / (self.GlassFace.Area + self.FrameFace.Area)

    def create_glazing_mat(self,
                           density=2500,  # DIN EN 572-1:2016-06
                           heat_capacity=720,  # DIN EN 572-1:2016-06
                           thermal_conductivity=1,  # DIN EN 572-1:2016-06
                           solar_absorption_coefficient=0,
                           ):
        '''

        :return:
        '''

        # calculate absorption coefficient of the glass-panes:
        overall_thickness = self.NumberOfGlazings * self.GlazingThickness
        absorption_coefficient = calc_absorption_coefficient(self.Alpha_e, overall_thickness)

        glazing_material = Material(name='WindowGlazingMaterial1_{}'.format(self.Name),
                                    density=density,
                                    heat_capacity=heat_capacity,
                                    thermal_conductivity=thermal_conductivity,
                                    transparent=True,
                                    solar_absorption_coefficient=solar_absorption_coefficient,
                                    absorption_coefficient=absorption_coefficient,
                                    wvdrf=999999,
                                    w20=0,
                                    w80=0)

        return glazing_material

    def create_air_mat(self):

        air_material = Material(name='WindowMaterialAir_{}'.format(self.Name),
                                density=1.7,                    # DIN EN ISO 10456:2010-05- Argon
                                heat_capacity=519,              # DIN EN ISO 10456:2010-05- Argon
                                thermal_conductivity=0.017,     # DIN EN ISO 10456:2010-05- Argon
                                transparent=True,
                                solar_absorption_coefficient=0,
                                absorption_coefficient=0,
                                wvdrf=1,
                                w20=0,
                                w80=0)

        return air_material


class Material(ObjectBaseClass):

    new_material_id = itertools.count(0)
    visible_class_name = 'Material'

    def __init__(self,
                 name=None,
                 material_id=None,
                 color=None,
                 density=1000,                      # kg / m^3
                 heat_capacity=1000,                # specific heat capacity [J /(kg K)]
                 thermal_conductivity=1,            # W /(m K)
                 transparent=False,                 # material is transparent
                 emission_coefficient=0.93,         # emission coefficient
                 solar_absorption_coefficient=0.5,
                 refractive_index=1,                # m/m
                 absorption_coefficient=999999,     # 1/m
                 scattering_coefficient=0,          # 1/m
                 dynamic_viscosity=999999,          # kg/(m*s)
                 thermodynamic_state=0,             # 0: solid, 1: liquid, 2: gas
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

        # add to the collection
        settings.building_collection.Material_collection.append(self)

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
        if self._ThermalConductivity is None:
            raise ValueError('thermal conductivity is none')
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
                 mat_layer_id=None,
                 name=None,
                 color=None,
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
        self._Transparent = None

        self.Thickness = thickness

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



        # --------------------------------------------------------
        # bind observed objects
        # --------------------------------------------------------

        if isinstance(self._Material, list):
            for material in self._Material:
                material.bind_to(self.material_updated)
        else:
            self._Material.bind_to(self.material_updated)

        # add to the collection
        settings.building_collection.MatLayer_collection.append(self)

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
    def Transparent(self):
        if isinstance(self.Material, list):
            transparent = self.Material[0].Transparent
        else:
            transparent = self.Material.Transparent
        return transparent

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
        return self._Absorption

    @Absorption.setter
    def Absorption(self, value):
        self._default_set_handling('Absorption', value)

    def calc_thermal_resistance(self):
        if isinstance(self.Material, list):
            self.ThermalResistance = self.Thickness / self.Material[0].ThermalConductivity
        else:
            self.ThermalResistance = self.Thickness / self.Material.ThermalConductivity

    def calc_absorption(self):
        """
        I = I0 exp(-ax)
        where I is the radiation intensity, a is the absorption coefficient, and x is the distance through the material.
        self.Absorption = exp(-ax)
        :return:
        """
        if isinstance(self.Material, list):
            if self.Material[0].Transparent:
                self.Absorption = 1 - np.exp(-self.Material[0].AbsorptionCoefficient * self.Thickness)
            else:
                self.Absorption = 1
        else:
            if self.Material.Transparent:
                self.Absorption = 1 - np.exp(-self.Material.AbsorptionCoefficient * self.Thickness)
            else:
                self.Absorption = 1

    def material_updated(self):
        self.calc_thermal_resistance()


def calc_absorption_coefficient(alpha_e, x):
    """
    # calculate absorption coefficient of the glass-panes:
    # I = I0 exp(-a * x)
    # where I is the radiation intensity, a is them absorption coefficient, and x is the distance through the
    # material.
    # -> solve for a: a = - ln(I / I0) / x
    # here is I / I0 the total absorption alpha_e

    :param alpha_e:
    :param x:
    :return:
    """
    absorption_coefficient = - np.log(1 - alpha_e) / x

    # test:
    np.exp(-absorption_coefficient * x)

    return absorption_coefficient








