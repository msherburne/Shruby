import geopandas as gpd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from shapely import Point, Polygon, LineString, LinearRing
import pyproj
from shapely.ops import transform
import numpy as np
import math

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

DISTANCE_METRICS = ['meters', 'kilometers', 'feet', 'miles', 'nautical_miles']

def enrich_points(data, lat_field, lon_field):
    points = []
    if lat_field and lon_field:
        for _, row in data.iterrows():
            points.append(Point(row[lon_field], row[lat_field]))
    else:
        for _, row in data.iterrows():
            points.append(Point(row["SHAPE"]["x"], row["SHAPE"]["y"]))
    return points

class ShapeAccessor:
    def __init__(self, data, lat_field=None, lon_field=None):
        if lat_field and lon_field:
            self._init_data = data
            try:
                self.x = data[lon_field]
                self.y = data[lat_field]
            except KeyError:
                raise KeyError("lat_field and lon_field must be valid fields in the GeoDataFrame")
        else:
            try:
                self._init_data = data["SHAPE"]
                self.x = self._init_data["x"]
                self.y = self._init_data["y"]
            except KeyError:
                raise KeyError("SHAPE field was not found in the GeoDataFrame. Please provide lat_field and lon_field or use a GeoDataFrame with a SHAPE field.")
def to_meters(distance, metric):
    if metric == "nautical_miles":
        return distance * 1852
    elif metric == "miles":
        return distance * 1609.344
    elif metric == "feet":
        return distance * 0.3048
    elif metric == "kilometers":
        return distance * 1000
    elif metric == "meters":
        return distance
    else:
        raise ValueError("metric must be one of {}".format(DISTANCE_METRICS))

def get_crs(crs):
    if crs is None:
        return "EPSG:4326"
    else:
        return crs
class ShrubyFrame(gpd.GeoDataFrame):
    def __init__(self, sdf, lat_field=None, lon_field=None, crs=None, using_arcgis_api=False,*args, **kwargs):
        super().__init__(sdf, geometry=enrich_points(sdf, lat_field, lon_field), crs=get_crs(crs), *args, **kwargs)
        self._lat_field = lat_field
        self._lon_field = lon_field
        self._using_arcgis_api = using_arcgis_api
        if crs is None:
            self._crs = "EPSG:4326"
        else:
            self._crs = crs
        # sdf['geometry'] = enrich_points(sdf, lat_field, lon_field)
        # print(sdf['geometry'])
        # super().__init__(data=sdf, crs=self._crs, geometry='geometry', **kwargs)
    def _access_shape(self, data):
        """
        Returns the shape of the geometry or geometries.
        
        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        data                 Required GeoDataFrame or GeoSeries. The GeoDataFrame to access the shape of.
        ================     ====================================================================
        """
        try:
            if isinstance(data, gpd.GeoDataFrame):
                return [ShapeAccessor(row, lat_field=self._lat_field, lon_field=self._lon_field) for _ , row in data.iterrows()]
            elif isinstance(data, gpd.GeoSeries):
                return ShapeAccessor(data,  lat_field=self._lat_field, lon_field=self._lon_field)
        except Exception as e:
            raise e
    def _project_to_web_mercator(self, point):
        """
        Projects the GeoDataFrame to Web Mercator.
        """
        proj = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)
        if isinstance(point, Point):
            return Point(proj.transform(point.x, point.y))
        elif isinstance(point, Polygon):
            return Polygon([proj.transform(x, y) for x, y in point.exterior.coords])
        elif isinstance(point, LineString):
            return LineString([proj.transform(x, y) for x, y in point.coords])
        else:
            raise ValueError("geometry must be a Point, Polygon, or LineString")
    def _project_from_web_mercator(self, geometry):
        """
        Projects the GeoDataFrame from Web Mercator to the original crs.
        """
        
        proj = pyproj.Transformer.from_crs(3857, 4326, always_xy=True)
        if isinstance(geometry, Point):
            return Point(proj.transform(geometry.x, geometry.y))
        elif isinstance(geometry, Polygon):
            return Polygon([proj.transform(x, y) for x, y in geometry.exterior.coords])
        elif isinstance(geometry, LineString):
            return LineString([proj.transform(x, y) for x, y in geometry.coords])
        else:
            raise ValueError("geometry must be a Point, Polygon, or LineString")
   
    def create_buffers(self, distance, metric, *args, **kwargs):
        """
        Creates a new ShrubyFrame with buffers around each geometry.

        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        distance             Required Float or String. The distance around each geometry to create a buffer or the field that contains it.
        ----------------     --------------------------------------------------------------------
        metric               Required String. The unit of measure for the buffer distance.
        ================     ====================================================================

        :returns: A new ShrubyFrame with the buffers added as a new column.
        """
        if metric not in DISTANCE_METRICS:
            raise ValueError("metric must be one of {}".format(DISTANCE_METRICS))
        if isinstance(distance, int) or isinstance(distance, float):
            distance_type = "distance"
        elif isinstance(distance, str):
            distance_type = "field"
        else:
            raise ValueError("distance must be a number or a string")
        
        rows = [row for _, row in self.iterrows()]

        new_rows = []

        for row in rows:
            geometry = row["geometry"]
            point = Point(geometry.x, geometry.y)
            meters_point = self._project_to_web_mercator(point)
            if distance_type == "distance":
                meters_buffer = meters_point.buffer(to_meters(distance, metric), *args, **kwargs)
            elif distance_type == "field":
                meters_buffer = meters_point.buffer(to_meters(row[distance], metric), *args, **kwargs)
            row["buffer_geometry"] = self._project_from_web_mercator(meters_buffer)
            new_rows.append(row)
        geodataframe = gpd.GeoDataFrame(new_rows, geometry="buffer_geometry", crs=self._crs)

        if self._using_arcgis_api:
            return GeoAccessor.from_geodataframe(geodataframe)
        return ShrubyFrame(geodataframe, using_arcgis_api=self._using_arcgis_api, crs=self._crs, lat_field=self._lat_field, lon_field=self._lon_field)
    
    def find_in_buffer(self, distance, metric):
        """
        Returns a filtered ShrubyFrame with geometries that intersect the buffer.

        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        distance             Required Float. The distance around each geometry to create a buffer.
        ----------------     --------------------------------------------------------------------
        metric               Required String. The unit of measure for the buffer distance.
        ================     ====================================================================

        :returns: A new ShrubyFrame with the geometries that intersect the buffer.
        """

        if metric not in DISTANCE_METRICS:
            raise ValueError("metric must be one of {}".format(DISTANCE_METRICS))
        if isinstance(distance, int) or isinstance(distance, float):
            distance_type = "distance"
        elif isinstance(distance, str):
            distance_type = "field"
        else:
            raise ValueError("distance must be a number or a string")
        
        return ShrubyFrame()

    def create_cones(self, distance, metric, orientation, offset=20, precision=50):
        """
        Creates a new ShrubyFrame with cones around each geometry.

        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        distance             Required Float. The distance around each geometry to create a cone.
        ----------------     --------------------------------------------------------------------
        metric               Required String. The unit of measure for the cone distance.
        ----------------     --------------------------------------------------------------------
        orientation          Required String. The orientation of the cone.
        ================     ====================================================================

        :returns: A new ShrubyFrame with the cones added as a new column.
        """
        # check errors
        if isinstance(distance, int) or isinstance(distance, float):
            distance_type = "distance"
        elif isinstance(distance, str):
            distance_type = "field"
        else:
            raise ValueError("distance must be a number or a string")
        
        if isinstance(orientation, str):
            orientation_type = "field"
        elif isinstance(orientation, int) or isinstance(orientation, float):
            if orientation < 0 or orientation > 360:
                raise ValueError("orientation must be between 0 and 360")
            orientation_type = "angle"
        else:
            raise ValueError("orientation must be a number or a string")
        if metric not in DISTANCE_METRICS:
            raise ValueError("metric must be one of {}".format(DISTANCE_METRICS))
        
        rows = [row for _, row in self.iterrows()]

        new_rows = []
        num_points = precision
        
        for row in rows:
            original_center_point = row["geometry"]
            center_point = self._project_to_web_mercator(original_center_point)
            center_x = center_point.x
            center_y = center_point.y
            if orientation_type == "field":
                orientation_rad = math.radians(row[orientation])
            elif orientation_type == "angle":
                orientation_rad = math.radians(orientation)
            if distance_type == "distance":
                distance_meters = to_meters(distance, metric)
            elif distance_type == "field":
                distance_meters = to_meters(row[distance], metric)
            offset_rad = math.radians(offset)
            arc = []
            for i in range(num_points + 1):
                angle_rad = orientation_rad + offset_rad * (i / num_points)
                arc_x = center_x + distance_meters * math.cos(angle_rad)
                arc_y = center_y + distance_meters * math.sin(angle_rad)
                arc.append((arc_x, arc_y))
            arc_line = LineString(arc)
            cone_polygon = Polygon([(center_x, center_y)] + list(arc_line.coords))
            row["cone_geometry"] = self._project_from_web_mercator(cone_polygon)
            new_rows.append(row)
        geodataframe = gpd.GeoDataFrame(new_rows, geometry="cone_geometry", crs=self._crs)

        if self._using_arcgis_api:
            return GeoAccessor.from_geodataframe(geodataframe)
        return ShrubyFrame(geodataframe, using_arcgis_api=self._using_arcgis_api, crs=self._crs, lat_field=self._lat_field, lon_field=self._lon_field)

    def create_rings(self, distance, metric, *args, **kwargs):
        """
        Creates a new ShrubyFrame with rings around each geometry.

        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        distance             Required Float or String. The distance around each geometry to create a ring or the field that contains it.
        ----------------     --------------------------------------------------------------------
        metric               Required String. The unit of measure for the ring distance.
        ================     ====================================================================
        """
        if metric not in DISTANCE_METRICS:
            raise ValueError("metric must be one of {}".format(DISTANCE_METRICS))
        if isinstance(distance, int) or isinstance(distance, float):
            distance_type = "distance"
        elif isinstance(distance, str):
            distance_type = "field"
        else:
            raise ValueError("distance must be a number or a string")
        
        rows = [row for _, row in self.iterrows()]

        new_rows = []

        for row in rows:
            geometry = row["geometry"]
            point = Point(geometry.x, geometry.y)
            meters_point = self._project_to_web_mercator(point)
            if distance_type == "distance":
                meters_buffer = meters_point.buffer(to_meters(distance, metric), *args, **kwargs)
                ring_geos = LinearRing(meters_buffer.exterior.coords)
            elif distance_type == "field":
                meters_buffer = meters_point.buffer(to_meters(row[distance], metric), *args, **kwargs)
                ring_geos = LinearRing(meters_buffer.exterior.coords)
            row["ring_geometry"] = self._project_from_web_mercator(ring_geos)
            new_rows.append(row)
        geodataframe = gpd.GeoDataFrame(new_rows, geometry="ring_geometry", crs=self._crs)

        if self._using_arcgis_api:
            return GeoAccessor.from_geodataframe(geodataframe)
        return ShrubyFrame(geodataframe, using_arcgis_api=self._using_arcgis_api, crs=self._crs, lat_field=self._lat_field, lon_field=self._lon_field)
        