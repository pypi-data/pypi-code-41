from normetapi import weathericon

img = weathericon(1, image_type='png', night=False, polar_night=False,
                  output_file='1.png')
weathericon(2, image_type='svg', night=False, polar_night=False,
            output_file='2.svg')
weathericon(3, image_type='svg+xml', night=False, polar_night=False,
            output_file='3.svg')
weathericon(3, image_type='svg+xml', night=True, polar_night=False,
            output_file='3_night.svg')
weathericon(3, image_type='svg+xml', night=False, polar_night=True,
            output_file='3_polar_night.svg')
