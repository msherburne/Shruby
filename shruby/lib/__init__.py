import geopandas as gpd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from shapely import Point

DISTANCE_METRICS = ['meters', 'kilometers', 'feet', 'miles', 'nautical_miles']

class ShrubyFrame(gpd.GeoDataFrame):
    def __init__(self, sdf):
        super().__init__(sdf)

    def _access_shape(data):
        """
        Returns the shape of the geometry or geometries.
        
        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        data                 Required GeoDataFrame or GeoSeries. The GeoDataFrame to access the shape of.
        ================     ====================================================================
        """
        return data["SHAPE"]

    def create_buffers(self, distance, metric):
        """
        Creates a new ShrubyFrame with buffers around each geometry.

        ================     ====================================================================
        **Argument**         **Description**
        ----------------     --------------------------------------------------------------------
        distance             Required Float. The distance around each geometry to create a buffer.
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
        
        return ShrubyFrame()
    
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

    def create_cones(self, distance, metric, orientation):
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
        

        return ShrubyFrame()