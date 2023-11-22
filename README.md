## Shruby

This library provides one kind of object dubbed "ShrubyFrame". This modified dataframe mimics a GeoDataframe with a few special tweaks. It is designed to work hand in hand with the ArcGIS API for Python. This project is in progress but version 0.1.0 will have the following methods:

- [create_buffers](#create_buffers): creates a buffer around a point.
- [create_cones](#create_cones): creates triangle like cones that show a range and direction of a point.
- [create_rings](#create_rings): creates rings based on a buffer around a point

### Installation

```bash
pip install shruby
```

### Usage

```python
import pandas as pd
from shruby import ShrubyFrame

df = pd.read_csv("data.csv")
sdf = ShrubyFrame(df, lat_field="lat", lon_field="lon", crs="EPSG:4326")
sdf.create_buffers(distance=100, metric="meters")
```

### ShrubyFrame

##### Constructor

| Parameter        | Type                                          | Default   | Details                                                            |
| ---------------- | --------------------------------------------- | --------- | ------------------------------------------------------------------ |
| sdf              | Pandas DF, GeoDF, ArcGIS spacially enabled DF |           | The input data in the form of a dataframe.                         |
| lat_field        | string                                        | None      | The latitude or Y field. If None, defaults to SHAPE from ArcGIS.   |
| lon_field        | string                                        | None      | The longitude or X field. If None, defaults to SHAPE from ArcGIS.  |
| crs              | string                                        | EPSG:4326 | The spatial reference/projection in the form of EPSG:XXXX.         |
| using_arcgis_api | bool                                          | False     | Whether to return GeoAccessor Objects for use with the ArcGIS API. |
| args             |                                               |           | args for a GeoDataframe                                            |

#### create_buffers

| Argument  | Type             | Default | Details                                                                                                                                                       |
| --------- | ---------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| distance  | numerical/string | None    | The distance of the radius. Can be a plain number or a field in the dataframe that contains the distance for each row.                                        |
| metric    | string           | None    | The unit of measurement for the distance. Can be any of the following: "meters", "kilometers", "feet", "miles", "nautical_miles".                             |
| quad_segs | int              | 8       | The number of segments to use to create the buffer. The more segments that are used, the more circular the buffer will be, at the expense of processing time. |

Returns a ShrubyFrame with a geometry set to column "buffer_geometry" containing polygons. If using ArcGIS API, returns a GeoAccessor object.

#### create_cones

| Argument    | Type             | Default | Details                                                                                                                                                          |
| ----------- | ---------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| distance    | numerical/string | None    | The distance of the radius. Can be a plain number or a field in the dataframe that contains the distance for each row.                                           |
| metric      | string           | None    | The unit of measurement for the distance. Can be any of the following: "meters", "kilometers", "feet", "miles", "nautical_miles".                                |
| orientation | numerical/string | None    | The orientation of the cone. Can be a plain number or a field in the dataframe that contains the orientation for each row. Must be a number between 0 and 360.   |
| offset      | numerical        | 20      | The offset of the cone. This offset will decide how wide the cones angle is.                                                                                     |
| precision   | int              | 50      | The number of points to use to create the cone. The more points that are used, the more circular the end of the cone will be, at the expense of processing time. |

Returns a ShrubyFrame with a geometry set to column "cone_geometry" containing polygons. If using ArcGIS API, returns a GeoAccessor object.

#### create_rings

| Argument  | Type             | Default | Details                                                                                                                                                       |
| --------- | ---------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| distance  | numerical/string | None    | The distance of the radius. Can be a plain number or a field in the dataframe that contains the distance for each row.                                        |
| metric    | string           | None    | The unit of measurement for the distance. Can be any of the following: "meters", "kilometers", "feet", "miles", "nautical_miles".                             |
| quad_segs | int              | 8       | The number of segments to use to create the buffer. The more segments that are used, the more circular the buffer will be, at the expense of processing time. |

Returns a ShrubyFrame with a geometry set to column "ring_geometry" containing polygons. If using ArcGIS API, returns a GeoAccessor object.
