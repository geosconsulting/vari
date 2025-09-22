ogr2ogr -f "PostgreSQL" PG:"host=192.168.1.10 port=5432 user=postgres dbname=dbsm password=antarone" gpkgs/dbsm-v2-malta-R2025.gpkg -nln "malta" -progress -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI -overwrite -gt 50000 --config OGR_TRUNCATE YES

ogr2ogr -f "PostgreSQL" PG:"host=192.168.1.10 port=5432 user=postgres dbname=dbsm password=antarone" gpkgs/dbsm-v2-lithuania-R2025.gpkg -nln "lithuania" -progress -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI -overwrite -gt 50000 --config OGR_TRUNCATE YES

ogr2ogr -f "PostgreSQL" PG:"host=192.168.1.10 port=5432 user=postgres dbname=dbsm password=antarone" gpkgs/dbsm-v2-austria-R2025.gpkg -nln "austria" -progress -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI -overwrite -gt 50000 --config OGR_TRUNCATE YES

ogr2ogr -f "PostgreSQL" PG:"host=192.168.1.10 port=5432 user=postgres dbname=dbsm password=antarone" gpkgs/dbsm-v2-italy-R2025.gpkg -nln "italy" -progress -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI -overwrite -gt 50000 --config OGR_TRUNCATE YES

