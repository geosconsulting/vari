SELECT id, nuts_id,name_latn, ST_TRANSFORM(geom,4326) 
FROM nuts_rg_60m_2024 
WHERE levl_code = 2 AND cntr_code = 'IT'

