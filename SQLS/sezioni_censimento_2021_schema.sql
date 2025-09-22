-- Table: public.sezioni_censimento_2021

-- DROP TABLE IF EXISTS public.sezioni_censimento_2021;

CREATE TABLE IF NOT EXISTS public.sezioni_censimento_2021
(
    cod_reg bigint,
    cod_uts bigint,
    pro_com bigint,
    sez21 bigint,
    sez21_id double precision,
    cod_tipo_s bigint,
    tipo_loc bigint,
    loc21_id double precision,
    cod_zic bigint,
    cod_isam bigint,
    cod_acque bigint,
    cod_isole bigint,
    cod_mont_d bigint,
    cod_area_s bigint,
    com_asc1 double precision,
    com_asc2 double precision,
    com_asc3 double precision,
    pop21 double precision,
    fam21 double precision,
    cod_macro text COLLATE pg_catalog."default",
    den_macro text COLLATE pg_catalog."default",
    cod_a text COLLATE pg_catalog."default",
    den_a text COLLATE pg_catalog."default",
    shape_leng double precision,
    shape_area double precision,
    geom geometry(PolygonZ,32632)
) PARTITION BY LIST (cod_macro);


ALTER TABLE IF EXISTS public.sezioni_censimento_2021
    OWNER to postgres;
-- Index: idx_sezioni_censimento_2021_geometry

-- DROP INDEX IF EXISTS public.idx_sezioni_censimento_2021_geometry;

CREATE INDEX IF NOT EXISTS idx_sezioni_censimento_2021_geometry
    ON public.sezioni_censimento_2021 USING gist
    (geom);