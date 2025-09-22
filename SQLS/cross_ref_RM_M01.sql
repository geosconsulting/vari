select * from public.province_24_wgs84 where sigla = 'RM';

explain (analyze,verbose) select * from public.sezioni_censimento_2021 where cod_macro = 'M01' limit 10;

SELECT f.pop21,f.fam21,f.cod_macro,
	   f.geometry, 
	   --ST_Transform(f.geometry, 4326),
	   r.cod_reg, r.cod_prov, r.cod_cm, r.sigla
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
	-- JOIN italian_regions r ON ST_Intersects(ST_Transform(f.geometry, 4326),ST_Transform(r.geometry, 4326))
WHERE cod_macro = 'M02' 
  AND	r.sigla = 'RM'
  AND ST_IsValid(r.geom)  -- Ensure valid geometries
  AND ST_IsValid(f.geometry);

-- If you need to check which partition the data comes from:
EXPLAIN (ANALYZE, VERBOSE)
SELECT f.*, r.cod_reg, r.cod_prov, r.cod_com
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
WHERE r.sigla = 'RM'
  AND ST_IsValid(r.geom)  -- Ensure valid geometries
  AND ST_IsValid(f.geometry);

EXPLAIN (ANALYZE, VERBOSE)
SELECT f.pop21,f.fam21,f.cod_macro,
	   f.geometry, 
	   -- ST_Transform(f.geometry, 4326) as geometry,
	   r.cod_reg, r.cod_prov, r.cod_cm, r.sigla
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
	-- JOIN province_24_wgs84 r ON ST_Intersects(ST_Transform(f.geometry, 4326),ST_Transform(r.geom, 4326))
WHERE cod_macro = 'M04' 
  AND r.sigla = 'VT';
  -- AND ST_IsValid(r.geom)  -- Ensure valid geometries
  -- AND ST_IsValid(f.geometry);  


SELECT f.pop21,f.fam21,f.cod_macro,f.den_macro,
	   f.geometry, 
	   -- ST_Transform(f.geometry, 4326) as geometry,
	   r.cod_reg, r.cod_prov, r.cod_cm, r.sigla
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
	-- JOIN province_24_wgs84 r ON ST_Intersects(ST_Transform(f.geometry, 4326),ST_Transform(r.geom, 4326))
WHERE cod_macro = 'M02' 
  AND r.sigla = 'VT';

SELECT f.pop21,f.fam21,f.cod_macro,f.den_macro,
	   f.geometry, 
	   -- ST_Transform(f.geometry, 4326) as geometry,
	   r.cod_reg, r.cod_prov, r.cod_cm, r.sigla
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
	-- JOIN province_24_wgs84 r ON ST_Intersects(ST_Transform(f.geometry, 4326),ST_Transform(r.geom, 4326))
WHERE cod_macro = 'M01' 
  AND r.sigla = 'VT';


SELECT f.pop21,f.fam21,f.cod_macro,f.den_macro,
	   f.geometry, 
	   -- ST_Transform(f.geometry, 4326) as geometry,
	   r.cod_reg, r.cod_prov, r.cod_cm, r.sigla
FROM sezioni_censimento_2021 f
	JOIN province_24_wgs84 r ON ST_Intersects(f.geometry, r.geom)
	-- JOIN province_24_wgs84 r ON ST_Intersects(ST_Transform(f.geometry, 4326),ST_Transform(r.geom, 4326))
WHERE cod_macro = 'M01' 
  AND r.sigla = 'VT';


SELECT sum(f.pop21), r.den_asc3, f.geometry
FROM sezioni_censimento_2021 f
	JOIN admin_liv3_wgs84 r ON ST_Intersects(f.geometry, r.geom)	
WHERE f.cod_macro = 'M01' 
  AND r.den_asc3 = 'Palocco'
 GROUP BY f.geometry,r.den_asc3;

SELECT sum(f.pop21)
FROM sezioni_censimento_2021 f
	JOIN admin_liv3_wgs84 r ON ST_Intersects(f.geometry, r.geom)	
WHERE f.cod_macro = 'M01' 
  AND r.den_asc3 = 'Acilia Sud';

SELECT sum(f.pop21)
FROM sezioni_censimento_2021 f
	JOIN admin_liv3_wgs84 r ON ST_Intersects(f.geometry, r.geom)	
WHERE f.cod_macro = 'M01' 
  AND r.den_asc3 = 'Palocco';

SELECT sum(f.pop21)
FROM sezioni_censimento_2021 f
	JOIN admin_liv3_wgs84 r ON ST_Intersects(f.geometry, r.geom)	
WHERE f.cod_macro = 'M01' 
  AND r.den_asc3 = 'Esquilino';

SELECT sum(f.pop21)
FROM sezioni_censimento_2021 f
	JOIN admin_liv3_wgs84 r ON ST_Intersects(f.geometry, r.geom)	
WHERE f.cod_macro = 'M01' 
  AND r.den_asc3 = 'Decima';   