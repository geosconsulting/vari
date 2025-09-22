CREATE TABLE sezioni_censimento_2021_m99
    PARTITION OF sezioni_censimento_2021
    FOR VALUES IN ('M99');