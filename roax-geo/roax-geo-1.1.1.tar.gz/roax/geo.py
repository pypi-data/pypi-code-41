"""Module that provides schema for GeoJSON data structures."""

import geomet.wkt as wkt
import geomet.wkb as wkb
import roax.schema as s


class _Object(s.dict):
    """Base class for all GeoJSON objects."""

    def __init__(self, properties={}, required=set(), **kwargs):
        super().__init__(
            properties={
                "type": s.str(enum={self.__class__.__name__}),
                "bbox": s.list(items=s.float(), min_items=4),
                **properties,
            },
            required={"type"}.union(set(required)),
            **kwargs,
        )
        self.required.add("type")


def _str_encode(schema, value):
    schema.validate(value)
    return wkt.dumps(value)


def _str_decode(schema, value):
    try:
        result = wkt.loads(value)
        if not schema.additional:
            result = schema.strip(result)
        schema.validate(result)
    except Exception as e:
        raise s.SchemaError(
            f"invalid WKT representation of {schema.__class__.__name__}"
        ) from e
    return result


def _bin_encode(schema, value):
    schema.validate(value)
    return wkb.dumps(value)


def _bin_decode(schema, value):
    try:
        result = wkb.loads(value)
        if not schema.additional:
            result = schema.strip(result)
        schema.validate(result)
    except Exception as e:
        raise s.SchemaError(
            f"invalid WKB representation of {schema.__class__.__name__}"
        ) from e
    return result


class _Geometry(_Object):
    """Base class for all geometry objects."""

    def __init__(self, coordinates_schema, properties={}, required=set(), **kwargs):
        super().__init__(
            properties={"coordinates": coordinates_schema, **properties},
            required={"coordinates"}.union(set(required)),
            **kwargs,
        )

    def str_encode(self, value):
        return _str_encode(self, value)

    def str_decode(self, value):
        return _str_decode(self, value)

    def bin_encode(self, value):
        return _bin_encode(self, value)

    def bin_decode(self, value):
        return _bin_decode(self, value)


class Point(_Geometry):
    """A geographical point."""

    def __init__(self, **kwargs):
        super().__init__(_PointCoordinates(), **kwargs)


class _PointCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=s.float(), min_items=2, max_items=2, **kwargs)

    def validate(self, value):
        super().validate(value)
        if value[0] < -180.0 or value[0] > 180.0:
            raise s.SchemaError("invalid longitude; must be -180.0 ≤ longitude ≤ 180.0")
        if value[1] < -90.0 or value[1] > 90.0:
            raise s.SchemaError("invalid latitude; must be -90.0 ≤ latitude ≤ 90.0")


class LineString(_Geometry):
    """A connected sequence of points."""

    def __init__(self, **kwargs):
        super().__init__(_LineStringCoordinates(), **kwargs)


class _LineStringCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_PointCoordinates(), **kwargs)


class Polygon(_Geometry):
    """
    A linear ring and zero or more interior linear rings.

    Parameters:
    • min_rings: Minimum number of linear rings.
    • max_rings: Maximum number of linear rings.
    """

    def __init__(self, min_rings=1, max_rings=None, **kwargs):
        if min_rings < 1:
            raise ValueError("min rings must be ≥ 1")
        if max_rings is not None and max_rings < min_rings:
            raise ValueError("max_rings must be ≥ min_rings")
        super().__init__(
            _PolygonCoordinates(min_items=min_rings, max_items=max_rings), **kwargs
        )


class _PolygonCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_LinearRingCoordinates(), **kwargs)


class _LinearRingCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_PointCoordinates(), min_items=4, **kwargs)

    def validate(self, value):
        super().validate(value)
        if value[0] != value[-1]:
            raise s.SchemaError(
                "last point in linear ring must be the same as the first point"
            )


class MultiPoint(_Geometry):
    """A collection of points."""

    def __init__(self, **kwargs):
        super().__init__(_MultiPointCoordinates(), **kwargs)


class _MultiPointCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_PointCoordinates(), **kwargs)


class MultiLineString(_Geometry):
    """A collection of line strings."""

    def __init__(self, **kwargs):
        super().__init__(_MultiLineStringCoordinates(), **kwargs)


class _MultiLineStringCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_LineStringCoordinates(), **kwargs)


class MultiPolygon(_Geometry):
    """A collection of polygons."""

    def __init__(self, **kwargs):
        super().__init__(_MultiPolygonCoordinates(), **kwargs)


class _MultiPolygonCoordinates(s.list):
    def __init__(self, **kwargs):
        super().__init__(items=_PolygonCoordinates(), **kwargs)


class GeometryCollection(_Object):
    """A collection of geometries."""

    def __init__(self, properties={}, required=set(), **kwargs):
        super().__init__(
            properties={"geometries": s.list(Geometry()), **properties},
            required={"geometries"}.union(set(required)),
            **kwargs,
        )

    def str_encode(self, value):
        return _str_encode(self, value)

    def str_decode(self, value):
        return _str_decode(self, value)

    def bin_encode(self, value):
        return _bin_encode(self, value)

    def bin_decode(self, value):
        return _bin_decode(self, value)


class Geometry(s.one_of):
    """One of: `Point`, `MultiPoint`, `LineString`, `MultiLineString`, `Polygon`, `MultiPolygon`."""

    def __init__(self, **kwargs):
        super().__init__(
            {
                Point(),
                MultiPoint(),
                LineString(),
                MultiLineString(),
                Polygon(),
                MultiPolygon(),
            },
            **kwargs,
        )


class Feature(_Object):
    """A spatially bounded thing."""

    def __init__(self, properties={}, required=set(), **kwargs):
        super().__init__(
            properties={
                "geometry": Geometry(nullable=True),
                "properties": s.dict(properties={}, additional=True, nullable=True),
                **properties,
            },
            required={"geometry", "properties"}.union(set(required)),
            **kwargs,
        )


class FeatureCollection(_Object):
    """A collection of features."""

    def __init__(self, properties={}, required=set(), **kwargs):
        super().__init__(
            properties={"features": s.list(Feature()), **properties},
            required={"features"}.union(set(required)),
            **kwargs,
        )
