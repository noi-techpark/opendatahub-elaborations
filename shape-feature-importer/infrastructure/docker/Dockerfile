# image could be replaced with official postgis docker image but currently it gives an error
FROM debian:buster-slim

ARG PGPASSWORD

RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           postgis \
           postgresql-client-11

# THESE STPES RUN NOW DIRECLTY IN DOCKER COMPOSE, SO THERE IS NO PROBLEM WITH CACHE ETC...
# # Create geometry table
# RUN shp2pgsql -s 4326 links/LinkStationsGeometries.shp elaboration.bluetoothlinks_tmp | psql -h prod-pg-bdp.co90ybcr8iim.eu-west-1.rds.amazonaws.com -U bdp bdp

# # Update geometries
# RUN psql -h prod-pg-bdp.co90ybcr8iim.eu-west-1.rds.amazonaws.com -U bdp -d bdp -c "set search_path=public,intimev2,elaboration;update edge as e set linegeometry = tmp.geom from ( select s.id,ST_TRANSFORM(ST_LineMerge(t.geom),25832) as geom from elaboration.bluetoothlinks_tmp t join intimev2.station s on t.id=s.id) as tmp where tmp.id=e.edge_data_id;"

# # Clean
# RUN psql -h prod-pg-bdp.co90ybcr8iim.eu-west-1.rds.amazonaws.com -U bdp -d bdp -c "drop table elaboration.bluetoothlinks_tmp;"

