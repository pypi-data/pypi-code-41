import os
from jinja2 import Template
# validacion con cerberus https://docs.python-cerberus.org/en/stable/usage.html
from cerberus import Validator


class Anexo2:
    """ Generacion del Anexo II """

    here = os.path.dirname(os.path.realpath(__file__))
    templates_folder = os.path.join(here, 'templates')
    default_template = os.path.join(templates_folder, 'Anexo-II-RESOLUCION-487-2002.html')

    errors = {}  # errores al procesar los datos {campo: error}

    def __init__(self, data):
        self.validator = Validator(self.get_schema())
        self.data = data

    def get_html(self, template_path=None, save_path=None):
        """
        recibe los datos a "dibujar", graba el HTML (si se lo pide)
        y devuelve:
            None si hay errores
            el código HTML si está todo OK
        TODO generar PDF: https://github.com/fdemmer/django-weasyprint
        """
        data = self.data
        if template_path is None:
            template_path = self.default_template

        res, errors = self.validate_data(data=data)
        if not res:
            self.errors = errors
            return None

        f = open(template_path)
        template = Template(f.read())
        html = template.render(**data)
        if save_path is not None:
            f = open(save_path, 'w')
            f.write(html)
            f.close()

        return html

    def validate_data(self, data):
        # validate
        r = self.validator.validate(data)
        return r, self.validator.errors

    def get_schema(self):
        schema = {
            'dia': {'type': 'integer', 'min': 1, 'max': 31},
            'mes': {'type': 'integer', 'min': 1, 'max': 12},
            'anio': {'type': 'integer', 'min': 2019, 'max': 2030},
            'hospital': {
                'type': 'dict',
                'schema': {
                    'nombre': {'type': 'string'},
                    # HPGD = Hospitales Públicos de Gestión Descentralizada
                    'codigo_hpgd': {'type': 'string'}
                    }
                },
            'beneficiario': {
                'type': 'dict',
                'schema': {
                    'apellido_y_nombres': {'type': 'string'},
                    'tipo_dni': {'type': 'string', 'allowed': ['DNI', 'LE', 'LC']}, 
                    'dni': {'type': 'string'},
                    'tipo_beneficiario': {'type': 'string', 'allowed': ['titular', 'no titular', 'adherente']},
                    'parentesco': {'type': 'string', 'allowed': ['conyuge', 'hijo', 'otro']},
                    'sexo': {'type': 'string', 'allowed': ['F', 'M']},
                    'edad': {'type': 'integer', 'min': 0, 'max': 110}
                    }
                },
            'atencion': {
                'type': 'dict',
                'schema': {
                    'tipo': {'type': 'string', 'allowed': ['consulta', 'practica', 'internacion']}, 
                    'especialidad': {'type': 'string'},
                    'codigos_N_HPGD': {'type': 'list'},
                    'fecha': {
                        'type': 'dict',
                        'schema': {
                            'dia': {'type': 'integer', 'min': 1, 'max': 31},
                            'mes': {'type': 'integer', 'min': 1, 'max': 12},
                            'anio': {'type': 'integer', 'min': 2019, 'max': 2030}
                            }
                        },
                    'diagnostico_ingreso_cie10': {
                        'type': 'dict',
                        'schema': {
                            'principal': {'type': 'string'}, 
                            'otros': {'type': 'list'}
                            }
                        }
                    }
                },
            'obra_social': {
                'type': 'dict',
                'schema': {
                    'codigo_rnos': {'type': 'string'},
                    'nombre': {'type': 'string'},
                    'nro_carnet_obra_social': {'type': 'string'},
                    'fecha_de_emision': {
                        'type': 'dict',
                        'schema': {
                            'dia': {'type': 'integer', 'min': 1, 'max': 31},
                            'mes': {'type': 'integer', 'min': 1, 'max': 12},
                            'anio': {'type': 'integer', 'min': 1970, 'max': 2030}
                            }
                        },
                    'fecha_de_vencimiento': {
                        'type': 'dict',
                        'schema': {
                            'dia': {'type': 'integer', 'min': 1, 'max': 31},
                            'mes': {'type': 'integer', 'min': 1, 'max': 12},
                            'anio': {'type': 'integer', 'min': 2019, 'max': 2030}
                            }
                        },
                    }
                },
            'empresa': {
                'type': 'dict',
                'schema': {
                    'nombre': {'type': 'string'},
                    'direccion': {'type': 'string'},
                    'ultimo_recibo_de_sueldo': {
                        'type': 'dict',
                        'schema': {
                            'dia': {'type': 'integer', 'min': 1, 'max': 31},
                            'mes': {'type': 'integer', 'min': 1, 'max': 12},
                            'anio': {'type': 'integer', 'min': 1970, 'max': 2030}
                            }
                        },
                    'cuit': {'type': 'string'}
                    }
                }
        }

        return schema

if __name__ == '__main__':
    a2 = Anexo2()
    save_to = os.path.join(a2.templates_folder, 'res.html')

    data = {'dia': 3,
            'mes': 9,
            'anio': 2019,
            'hospital': {
                'nombre': 'HOSPITAL SAN ROQUE',  # https://www.sssalud.gob.ar/index.php?page=bus_hosp&cat=consultas
                'codigo_hpgd': '4321323'
                },
            'beneficiario': {
                'apellido_y_nombres': 'Juan Perez',
                'tipo_dni': 'DNI',  # | LE | LC
                'dni': '34100900',
                'tipo_beneficiario': 'titular',  # | no titular | adherente
                'parentesco': 'conyuge',  # hijo | otro
                'sexo': 'M',  # | F
                'edad': 88,
                },
            'atencion': {
                'tipo': 'consulta',  # | practica | internacion
                'especialidad': 'Va un texto al parecer largo, quizas sea del nomenclador',
                'codigos_N_HPGD': ['AA01', 'AA02', 'AA06', 'AA07'],  # no se de donde son estos códigos
                'fecha': {'dia': 3, 'mes': 9, 'anio': 2019},
                'diagnostico_ingreso_cie10': {'principal': 'W020', 'otros': ['w021', 'A189']}
                },
            'obra_social': {
                'codigo_rnos': '800501',
                'nombre': 'OBRA SOCIAL ACEROS PARANA',
                'nro_carnet_obra_social': '9134818283929101',
                'fecha_de_emision': {'dia': 11, 'mes': 9, 'anio': 2009},
                'fecha_de_vencimiento': {'dia': 11, 'mes': 9, 'anio': 2029}
                },
            'empresa': {
                'nombre': 'Telescopios Hubble',
                'direccion': 'Av Astronómica s/n',
                'ultimo_recibo_de_sueldo': {'mes': 7, 'anio': 2019},
                'cuit': '31-91203043-8'
                }
        }

    res = a2.get_html(data=data, save_path=save_to)
    if res is None:
        print('ERRORES al procesar pedido')
        for field, error in a2.errors.items():
            print(f' - {field}: {error}')
    else:
        print(f'Procesado correctamente y grabado en {save_to}')
        