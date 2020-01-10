ShapefileFeatureImporter
==========================
This is a simple utility tool which imports multiline geometric data from a shapefile and matches it with the specified LinkStation.

## Structure
The shapefile got created with QGIS and needs to contain these attributes for each feature:
- id   ... id matching the of the speicific Linkstation in database
- name ... the name of the speicific linkstation

## How it works!
shp2pgsql reads the shapefile and transforms it into a table in the database. With a query the new linegeometry is matched with each edge of the Linkstation and replaced. In the end the the table created by shp2pgsql gets deleted.

## Considerations
The shapefile can be found in the *links* folder and must keep the same name. Currently, on each change the pipeline gets triggered.
