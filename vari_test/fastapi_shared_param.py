from fastapi import FastAPI, Depends, HTTPException, Query
from pathlib import Path as PathLib
from typing import Annotated
import logging

app = FastAPI(
    title="Multi-Country API",
    description="API that supports multiple countries via iso2 query parameter"
)

# Configuration
VALID_ISO2_CODES = {"us", "uk", "de", "fr", "es", "it", "ca", "au"}
BASE_DATA_DIR = PathLib("data")

logger = logging.getLogger(__name__)

async def get_country_directory(
    iso2: Annotated[str, Query(
        pattern="^[a-zA-Z]{2}$", 
        description="ISO2 country code",
        examples="us",
        openapi_examples={
            "us": {"summary": "United States", "value": "us"},
            "de": {"summary": "Germany", "value": "de"},
            "fr": {"summary": "France", "value": "fr"},
        }
    )] = "us"
) -> PathLib:
    """Validate ISO2 and return country directory"""
    iso2_lower = iso2.lower()
    
    if iso2_lower not in VALID_ISO2_CODES:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Invalid ISO2 code",
                "provided": iso2,
                "supported_codes": sorted(VALID_ISO2_CODES)
            }
        )
    
    directory_path = BASE_DATA_DIR / iso2_lower
    
    if not directory_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Data directory for country '{iso2}' not found"
        )
    
    return directory_path

CountryDir = Annotated[PathLib, Depends(get_country_directory)]

@app.get("/users", tags=["Users"])
async def get_users(directory: CountryDir):
    """Get users for the specified country"""
    return {"country_directory": str(directory), "endpoint": "users"}

@app.get("/products", tags=["Products"]) 
async def get_products(directory: CountryDir):
    """Get products for the specified country"""
    return {"country_directory": str(directory), "endpoint": "products"}

# Health check endpoint that shows supported countries
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "supported_countries": sorted(VALID_ISO2_CODES),
        "usage_example": "/users?iso2=us"
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1.0", port=8000)    