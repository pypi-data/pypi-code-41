from json import JSONEncoder


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Parameter(object):
    def __init__(self, name, start_row, start_column, end_row, end_column, sheet=None, direction=0):
        self.name = name
        self.start_row = start_row
        self.start_column = start_column
        self.end_row = end_row
        self.end_column = end_column
        self.sheet = sheet
        self.direction = direction


class Resource(object):
    def __init__(self, name, direction=0, element_numbers=None):
        self.name = name
        # direction 0: vertical, 1: horizontal
        self.direction = direction
        # element numbers: None: read until last entry, Number: read n entries
        self.element_numbers = element_numbers
        self.parameters = list()

    def add_parameter(self, name, start_row, start_column, end_row=None, end_column=None, sheet=None, direction=0):
        """

        :param name: Name of the Parameter
        :param start_row:
        :param start_column:
        :param end_row:
        :param end_column:
        :param sheet:
        :param direction: direction 0: vertical, 1: horizontal
        :return:
        """
        new_parameter = Parameter(name=name,
                                  start_row=start_row,
                                  start_column=start_column,
                                  end_row=end_row,
                                  end_column=end_column,
                                  sheet=sheet,
                                  direction=direction)

        self.parameters.append(new_parameter)


def export_json(config_data, filename):
    import json
    json_string = json.dumps(config_data, cls=MyEncoder, indent=4)
    with open(filename, "w") as text_file:
        text_file.write(json_string)

    print('json sucessfully written to {}'.format(filename))


if __name__ == '__main__':
    from tkinter.filedialog import asksaveasfile

    resources = list()

    new_resource = Resource(name='Surfaces')
    new_resource.add_parameter(name='ID', start_row=8, start_column=2, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Area', start_row=8, start_column=4, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Azimut', start_row=8, start_column=5, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Elevation', start_row=8, start_column=6, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='PartID', start_row=8, start_column=7, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='AdjacentZone', start_row=8, start_column=8, sheet='XXFlächenRäume')
    resources.append(new_resource)

    new_resource = Resource(name='Windows')
    new_resource.add_parameter(name='ID', start_row=8, start_column=10, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Area', start_row=8, start_column=12, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='WindowHight', start_row=8, start_column=13, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Azimut', start_row=8, start_column=14, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='Elevation', start_row=8, start_column=15, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='PartID', start_row=8, start_column=16, sheet='XXFlächenRäume')
    resources.append(new_resource)

    new_resource = Resource(name='Zone')
    new_resource.add_parameter(name='ID', start_row=8, start_column=30, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='NetVolume', start_row=8, start_column=31, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='GrossFloorArea', start_row=8, start_column=32, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='UsageID', start_row=8, start_column=33, sheet='XXFlächenRäume')
    new_resource.add_parameter(name='n50', start_row=8, start_column=25, sheet='XXFlächenRäume')
    resources.append(new_resource)

    new_resource = Resource(name='Layer')
    new_resource.add_parameter(name='ID', start_row=8, start_column=3, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='PartId', start_row=8, start_column=2, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Name', start_row=8, start_column=4, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Thickness', start_row=8, start_column=5, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='HeatConductivity', start_row=8, start_column=6, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='SpecificHeatCapacity', start_row=8, start_column=7, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Density', start_row=8, start_column=8, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Mu', start_row=8, start_column=9, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='w20', start_row=8, start_column=10, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='w80', start_row=8, start_column=11, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='AbsorptionCoefficient', start_row=8, start_column=12, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='AdjacentZone', start_row=8, start_column=13, sheet='XXBauteilaufbauten')
    resources.append(new_resource)

    new_resource = Resource(name='WindowConstruction')
    new_resource.add_parameter(name='ID', start_row=8, start_column=20, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Ug', start_row=8, start_column=21, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Uf', start_row=8, start_column=22, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Psi', start_row=8, start_column=23, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='FrameWidth', start_row=8, start_column=24, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Openable', start_row=8, start_column=25, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='G-Value', start_row=8, start_column=26, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Eps', start_row=8, start_column=27, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Tau', start_row=8, start_column=29, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Rho', start_row=8, start_column=30, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Alpha', start_row=8, start_column=31, sheet='XXBauteilaufbauten')
    resources.append(new_resource)

    new_resource = Resource(name='CurtainFacade')
    new_resource.add_parameter(name='ID', start_row=8, start_column=40, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Ug', start_row=8, start_column=41, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Uf', start_row=8, start_column=42, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Psi', start_row=8, start_column=43, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='GridWidth', start_row=8, start_column=44, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='GridHight', start_row=8, start_column=45, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='ProfileWidth', start_row=8, start_column=46, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='GValue', start_row=8, start_column=47, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Eps', start_row=8, start_column=48, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Tau', start_row=8, start_column=50, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Rho', start_row=8, start_column=51, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Alpha', start_row=8, start_column=52, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='Openable', start_row=8, start_column=53, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='OpenableWidth', start_row=8, start_column=54, sheet='XXBauteilaufbauten')
    new_resource.add_parameter(name='OpenableHight', start_row=8, start_column=55, sheet='XXBauteilaufbauten')
    resources.append(new_resource)

    f_out = asksaveasfile(mode='a', defaultextension='.txt')

    export_json(resources, f_out.name)



