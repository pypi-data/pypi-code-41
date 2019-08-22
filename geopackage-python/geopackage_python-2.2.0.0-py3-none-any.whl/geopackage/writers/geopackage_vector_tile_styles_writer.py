from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import \
    GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_styles.geopackage_stylesheets_table_adapter import \
    GeoPackageStylesheetsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_styles.styles_extension_constants import \
    GEOPACKAGE_STYLESHEETS_TABLE_NAME
from rgi.geopackage.extensions.vector_tiles.vector_styles.stylesheets_entry import StyleSheetsEntry
from rgi.geopackage.extensions.vector_tiles.vector_tiles_constants import GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME
from rgi.geopackage.utility.sql_utility import table_exists
from rgi.geopackage.writers.geopackage_writer import GeoPackageWriter


class GeoPackageVectorTileStylesWriter(GeoPackageWriter):
    """
    Writes style data for vector-tiles to a GeoPackage. Each instance will write to a single GeoPackage vector-tiles
    table.
    """

    def __init__(self, gpkg_file_path, timeout=500):
        """
        Constructor.

        :param gpkg_file_path: the path to the existing geopackage file
        :type gpkg_file_path: str

        :param timeout: the timeout for the database connection in miliseconds
         :type timeout: float
        """
        super(GeoPackageVectorTileStylesWriter, self).__init__(gpkg_file_path=gpkg_file_path,
                                                               timeout=timeout)
        cursor = self._database_connection().cursor()

        # create the styling tables
        if not table_exists(cursor=cursor, table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME):
            GeoPackageVectorLayersTableAdapter.create_vector_layers_table(cursor=cursor)

        if not table_exists(cursor=cursor,
                            table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            GeoPackageStylesheetsTableAdapter.create_stylesheets_table(cursor=cursor)

        self.add_version_information()
        # commit the new tables to the database
        self._database_connection().commit()

    def get_all_vector_layer_entries(self):
        """
        Returns any Vector Layer Entries in the GeoPackage.

        :return: Returns any Vector Layer Entries in the GeoPackage.
        parameter.

        :rtype: list of VectorLayerEntry
        """
        cursor = self._database_connection().cursor()

        return GeoPackageVectorLayersTableAdapter.get_all_vector_layers_entries(cursor=cursor)

    def get_all_vector_layer_entries_for_tileset(self,
                                                 vector_tiles_table_name):
        """
        Returns any Vector Layer Entries that apply to a specified vector-tiles table.

        :return: Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name
        parameter.

        :rtype: list of VectorLayerEntry
        """
        cursor = self._database_connection().cursor()

        return GeoPackageVectorLayersTableAdapter.get_vector_layer_entries_by_table_name(cursor=cursor,
                                                                                         vector_tiles_table_name=vector_tiles_table_name)

    def get_all_style_sheets(self):
        """
        Returns all the StyleSheetsEntry entries in the GeoPackage.

        :rtype list of StyleSheetsEntry
        """

        cursor = self._database_connection().cursor()
        return GeoPackageStylesheetsTableAdapter.get_all_stylesheet_entries(cursor=cursor)

    def add_new_stylesheet_to_gpkg(self,
                                   style_format,
                                   style_data,
                                   style_set,
                                   description='my style description',
                                   title='my-style', style='default'):
        """
        Add the new style to the GeoPackage. This style applies to all layers in the vector-tiles table.

        :param style_set: the name of a style group that many stylesheets can belong to (i.e. 'Mary's stylesheets')
        :type style_set: str

        :param style: alternative styles for the same set of layers (day, night)
        :type style: str

        :param style_format: the style encoding (i.e. SLD, MapBox, etc)
        :type style_format: str

        :param style_data: the stylesheet data (the JSON or xml as a binary)
        :type style_data: Binary
        """
        # check to see if a styleset exists already for this vector-tile set
        # get all vector layer entries and check for a styles_set id
        cursor = self._database_connection().cursor()

        # we set the styles_set to None and have the private method add_style update it with the correct value
        style_entry = StyleSheetsEntry(styles_set=style_set,
                                       style=style,
                                       style_format=style_format,
                                       stylesheet=style_data,
                                       title=title,
                                       description=description)

        # if a style_set already exists, add to existing
        self.__add_style(cursor=cursor, style_set_entry=style_entry)

    def __add_style(self,
                    cursor,
                    style_set_entry):
        """
        Helper function to add style data to the GeoPackage.

        :param style_set_entry: the StyleSheetEntry that needs to be added to the GeoPackage
        :type style_set_entry: StyleSheetsEntry
        """
        GeoPackageStylesheetsTableAdapter.insert_or_update_stylesheet_entry(cursor=cursor,
                                                                            stylesheet_entry=style_set_entry)

        self._database_connection().commit()
