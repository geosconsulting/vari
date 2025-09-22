SELECT osm_id,amenity,"addr:housename","addr:housenumber",way as geom
FROM planet_osm_point
WHERE amenity = 'post_office'
  AND ST_Contains(
        ST_Union(ARRAY(SELECT way FROM planet_osm_polygon WHERE name LIKE 'Roma')),  -- Combine polygons with ST_Union
        way
    );


-- REPROJECTED
SELECT osm_id,amenity,"addr:housename","addr:housenumber", ST_Transform(way, 4326)
FROM planet_osm_point
WHERE amenity = 'post_office'
  AND ST_Contains(
        ST_Union(ARRAY(SELECT way FROM planet_osm_polygon WHERE name LIKE 'Roma')),  -- Combine polygons with ST_Union
        way
    );


WITH RomaPolygons AS (
    SELECT ST_Union(ARRAY(SELECT way FROM planet_osm_polygon WHERE name LIKE 'Roma')) AS roma_geom
)
SELECT ST_Transform(way, 4326)
FROM planet_osm_line  -- Roads are usually lines
WHERE ST_Intersects(  -- Use ST_Intersects for lines and polygons
    (SELECT roma_geom FROM RomaPolygons),
    way
);

SELECT ST_SRID(way) FROM planet_osm_point LIMIT 1;