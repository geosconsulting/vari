#!/bin/bash
#!/bin/bash

# Configuration
DB_HOST="192.168.1.10"           # Database host
DB_PORT="5432"                # Database port
DB_NAME="dbsm"       # Database name
DB_USER="postgres"       # Database username
DB_PASSWORD="antarone"   # Database password
GPKG_DIR="gpkgs"  # Path to the directory containing GeoPackages

export PGPASSWORD=$DB_PASSWORD

# Iterate over all GeoPackage files in the specified directory
for gpkg in "$GPKG_DIR"/*.gpkg; do

    echo "Processing GeoPackage: $gpkg"
    # Extract the country name from the GeoPackage filename
    COUNTRY_NAME=$(basename "$gpkg" .gpkg)
    echo "Country name extracted: $COUNTRY_NAME"

    # Create the table name for PostGIS (prefix 'dbsm_' with the country name)
    TABLE_NAME="dbsm_${COUNTRY_NAME}"

    # Upload the GeoPackage data to PostGIS using ogr2ogr
    ogr2ogr -f "PostgreSQL" \
        PG:"host=$DB_HOST dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD port=$DB_PORT" \
        "$gpkg" \
        -nln "$TABLE_NAME" \      # Table name in PostGIS
        -overwrite                # Overwrite the table if it exists

    # Check for errors
    if [ $? -eq 0 ]; then
        echo "Successfully imported $gpkg into table $TABLE_NAME."
    else
        echo "Failed to import $gpkg"
    fi
done

# Unset the password environment variable for security
unset PGPASSWORD
