#!/bin/bash

# PostgreSQL/PostGIS connection parameters
HOST="192.168.1.10"
PORT="5432"
USER="postgres"
DBNAME="dbsm"
PASSWORD="antarone"

# Directory containing GeoPackage files
GPKG_DIR="gpkgs"


# Loop through all .gpkg files in the directory
for file in "$GPKG_DIR"/*.gpkg; do
  # Extract the country name from the filename (e.g., "germany")
  filename=$(basename "$file" .gpkg)
  country=$(echo "$filename" | awk -F'-' '{print $3}')  # Split on '-' and take 3rd field
  echo "Processing file: $file"
  echo "Extracted country name: $country"

  echo "Loading $file into table: $country"

  # Use ogr2ogr to load the GeoPackage into PostGIS
  ogr2ogr -f "PostgreSQL" \
    PG:"host=$HOST port=$PORT user=$USER dbname=$DBNAME password=$PASSWORD" \
    "$file" \
    -nln "$country" \             # Name the table after the country
    -progress \                   # Show progress (useful for large files)
    -lco GEOMETRY_NAME=geom \     # Rename geometry column to 'geom'
    -lco FID=id \                 # Rename primary key to 'id'
    -nlt PROMOTE_TO_MULTI \       # Avoid geometry type errors
    -overwrite \                  # Overwrite table if it exists
    -gt 50000 \  # Group transactions (50k features per transaction)
    #-active_schema "public"\                 
    --config OGR_TRUNCATE YES     # Truncate table before loading (alternative to -overwrite)
done

echo "All files loaded!"