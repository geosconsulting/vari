SELECT ST_GeometryType(geom), ST_SRID(geom) FROM austria LIMIT 1;

CREATE INDEX idx_austria_geom ON austria USING GIST(geom);

CREATE INDEX idx_cyprus_geom ON cyprus USING GIST(geom);

CREATE INDEX idx_italy_geom ON italy USING GIST(geom);

CREATE INDEX idx_malta_geom ON malta USING GIST(geom);

CREATE INDEX idx_netherlands_geom ON public.netherlands USING GIST(geom);

DROP INDEX IF EXISTS germany_geom_geom_idx;

CREATE INDEX idx_germany_geom ON public.germany USING GIST(geom);

SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'germany';

CLUSTER germany USING idx_germany_geom;

