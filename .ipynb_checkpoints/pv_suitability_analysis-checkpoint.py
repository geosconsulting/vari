import requests
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cdist
import warnings

warnings.filterwarnings("ignore")


class PVSuitabilityAnalyzer:
    """
    A comprehensive tool for evaluating photovoltaic suitability using PVGIS API
    and geospatial analysis techniques.
    """

    def __init__(self, api_base_url="https://re.jrc.ec.europa.eu/api/v5_2"):
        self.api_base_url = api_base_url
        self.pv_data = None
        self.suitability_scores = None

    def is_over_land(self, lat, lon):
        """
        Check if coordinates are over land using a simple heuristic.
        This is a basic check - for production use, consider using a proper land/sea mask.

        Parameters:
        -----------
        lat : float
            Latitude
        lon : float
            Longitude

        Returns:
        --------
        bool : True if likely over land
        """
        # Simple heuristic for common regions
        # This is very basic - in production, use proper land/sea datasets

        # Mediterranean Sea rough bounds
        if 30 <= lat <= 46 and -6 <= lon <= 36:
            # Exclude obvious sea areas
            if 36 <= lat <= 44 and -1 <= lon <= 8:  # Gulf of Lion area
                return False
            if 35 <= lat <= 42 and 12 <= lon <= 20:  # Adriatic Sea
                return False
            if 33 <= lat <= 40 and 24 <= lon <= 30:  # Eastern Mediterranean
                return False

        # Atlantic Ocean
        if lon < -10 or lon > 40:
            return False

        return True

    def validate_coordinates(self, lat, lon):
        """
        Validate if coordinates are suitable for PV analysis.

        Parameters:
        -----------
        lat : float
            Latitude
        lon : float
            Longitude

        Returns:
        --------
        bool : True if coordinates are valid for analysis
        """
        # Check basic coordinate bounds
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return False

        # Check if over land (basic heuristic)
        if not self.is_over_land(lat, lon):
            return False

        return True

    def fetch_pvgis_data(
        self,
        lat,
        lon,
        year=None,
        optimal_inclination=True,
        optimal_azimuth=True,
        system_power=1.0,
    ):
        """
        Fetch photovoltaic data from PVGIS API for a specific location.

        Parameters:
        -----------
        lat : float
            Latitude of the location
        lon : float
            Longitude of the location
        year : int, optional
            Specific year for analysis (default: typical meteorological year)
        optimal_inclination : bool
            Whether to use optimal inclination angle
        optimal_azimuth : bool
            Whether to use optimal azimuth angle
        system_power : float
            System power in kW

        Returns:
        --------
        dict : PVGIS response data
        """

        # Round coordinates to avoid floating point precision issues
        lat = round(lat, 6)
        lon = round(lon, 6)

        # Validate coordinates
        if not self.validate_coordinates(lat, lon):
            print(f"Skipping invalid coordinates ({lat}, {lon}) - likely over water")
            return None

        # Basic parameters for PVGIS API
        params = {
            "lat": lat,
            "lon": lon,
            "raddatabase": "PVGIS-SARAH2",
            "outputformat": "json",
            "usehorizon": 1,
            "pvtechchoice": "crystSi",
            "peakpower": system_power,
            "loss": 14,
            "mountingplace": "free",
        }

        # Add optimal angles if requested
        if optimal_inclination and optimal_azimuth:
            params["optimalinclination"] = 1
            params["optimalazimuth"] = 1
        else:
            params["angle"] = 35 if not optimal_inclination else 0
            params["aspect"] = 180 if not optimal_azimuth else 0

        # Add year if specified
        if year:
            params["startyear"] = year
            params["endyear"] = year

        try:
            response = requests.get(
                f"{self.api_base_url}/PVcalc", params=params, timeout=30
            )
            response.raise_for_status()

            # Check if response contains valid JSON
            data = response.json()
            if "outputs" not in data:
                print(f"Invalid response format for location ({lat}, {lon})")
                return None

            return data

        except requests.exceptions.Timeout:
            print(f"Timeout fetching data for location ({lat}, {lon})")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print(
                    f"Location ({lat}, {lon}) not supported by PVGIS (likely over water)"
                )
            else:
                print(
                    f"HTTP Error {e.response.status_code} for location ({lat}, {lon}): {e}"
                )
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error for location ({lat}, {lon}): {e}")
            return None
        except ValueError as e:
            print(f"JSON decode error for location ({lat}, {lon}): {e}")
            return None

    def analyze_grid_area(
        self, bounds, grid_spacing=0.01, max_retries=3, delay_between_requests=1.0
    ):
        """
        Analyze PV suitability for a grid of points within specified bounds.

        Parameters:
        -----------
        bounds : tuple
            (min_lon, min_lat, max_lon, max_lat)
        grid_spacing : float
            Distance between grid points in degrees
        max_retries : int
            Maximum number of retries for failed requests
        delay_between_requests : float
            Delay between API requests in seconds

        Returns:
        --------
        pd.DataFrame : Grid analysis results
        """
        import time

        min_lon, min_lat, max_lon, max_lat = bounds

        # Validate bounds
        if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")

        # Create grid of points
        lon_range = np.arange(min_lon, max_lon + grid_spacing, grid_spacing)
        lat_range = np.arange(min_lat, max_lat + grid_spacing, grid_spacing)

        lon_grid, lat_grid = np.meshgrid(lon_range, lat_range)
        grid_points = list(zip(lon_grid.flatten(), lat_grid.flatten()))

        results = []
        total_points = len(grid_points)

        print(f"Analyzing {total_points} grid points...")

        for i, (lon, lat) in enumerate(grid_points):
            if i % 10 == 0:
                print(f"Progress: {i}/{total_points} ({i/total_points*100:.1f}%)")

            # Add delay between requests to avoid rate limiting
            if i > 0:
                time.sleep(delay_between_requests)

            # Fetch PVGIS data for this point with retries
            pv_data = None
            for attempt in range(max_retries):
                pv_data = self.fetch_pvgis_data(lat, lon)
                if pv_data is not None:
                    break
                if attempt < max_retries - 1:
                    print(
                        f"Retry {attempt + 1}/{max_retries} for point ({lat:.4f}, {lon:.4f})"
                    )
                    time.sleep(2**attempt)  # Exponential backoff

            if pv_data and "outputs" in pv_data:
                try:
                    # Extract key metrics
                    outputs = pv_data["outputs"]

                    # Handle different response formats
                    if "totals" in outputs:
                        totals = outputs["totals"]
                        if "fixed" in totals:
                            annual_energy = totals["fixed"]["E_y"]
                            annual_irradiation = totals["fixed"]["H(i)_y"]
                        else:
                            annual_energy = totals["E_y"]
                            annual_irradiation = totals["H(i)_y"]
                    else:
                        # Fallback calculation from monthly data
                        monthly_data = outputs.get("monthly", [])
                        if monthly_data:
                            annual_energy = sum(month["E_m"] for month in monthly_data)
                            annual_irradiation = sum(
                                month["H(i)_m"] for month in monthly_data
                            )
                        else:
                            continue

                    # Get optimal angles from inputs
                    inputs = pv_data.get("inputs", {})
                    optimal_inclination = inputs.get("angle", 35)
                    optimal_azimuth = inputs.get("aspect", 180)

                    # Calculate seasonal variation if monthly data is available
                    monthly_data = outputs.get("monthly", [])
                    if monthly_data:
                        monthly_values = [month["E_m"] for month in monthly_data]
                        seasonal_variation = (
                            max(monthly_values) - min(monthly_values)
                        ) / np.mean(monthly_values)
                        performance_ratio = np.mean(
                            [month.get("PR", 0.8) for month in monthly_data]
                        )
                    else:
                        seasonal_variation = 0.2  # Default value
                        performance_ratio = 0.8  # Default value

                    results.append(
                        {
                            "longitude": lon,
                            "latitude": lat,
                            "annual_energy_kwh": annual_energy,
                            "annual_irradiation_kwh_m2": annual_irradiation,
                            "optimal_inclination": optimal_inclination,
                            "optimal_azimuth": optimal_azimuth,
                            "seasonal_variation": seasonal_variation,
                            "performance_ratio": performance_ratio,
                            "specific_yield": annual_energy / 1.0,  # kWh/kWp
                        }
                    )

                except (KeyError, TypeError) as e:
                    print(
                        f"Error processing data for point ({lat:.4f}, {lon:.4f}): {e}"
                    )
                    continue
            else:
                print(f"Failed to get valid data for point ({lat:.4f}, {lon:.4f})")

        if not results:
            raise ValueError(
                "No valid data points retrieved. Check your bounds and internet connection."
            )

        self.pv_data = pd.DataFrame(results)
        print(f"Successfully analyzed {len(results)} out of {total_points} points")
        return self.pv_data

    def calculate_suitability_score(self, weights=None):
        """
        Calculate comprehensive suitability scores for all analyzed points.

        Parameters:
        -----------
        weights : dict, optional
            Weights for different criteria

        Returns:
        --------
        pd.DataFrame : Data with suitability scores
        """

        if self.pv_data is None:
            raise ValueError("No PV data available. Run analyze_grid_area first.")

        # Default weights
        if weights is None:
            weights = {
                "annual_energy": 0.4,
                "annual_irradiation": 0.3,
                "performance_ratio": 0.2,
                "seasonal_stability": 0.1,
            }

        df = self.pv_data.copy()

        # Normalize metrics to 0-1 scale
        df["energy_score"] = (
            df["annual_energy_kwh"] - df["annual_energy_kwh"].min()
        ) / (df["annual_energy_kwh"].max() - df["annual_energy_kwh"].min())

        df["irradiation_score"] = (
            df["annual_irradiation_kwh_m2"] - df["annual_irradiation_kwh_m2"].min()
        ) / (
            df["annual_irradiation_kwh_m2"].max()
            - df["annual_irradiation_kwh_m2"].min()
        )

        df["performance_score"] = (
            df["performance_ratio"] - df["performance_ratio"].min()
        ) / (df["performance_ratio"].max() - df["performance_ratio"].min())

        # For seasonal variation, lower is better, so invert
        df["stability_score"] = 1 - (
            (df["seasonal_variation"] - df["seasonal_variation"].min())
            / (df["seasonal_variation"].max() - df["seasonal_variation"].min())
        )

        # Calculate weighted suitability score
        df["suitability_score"] = (
            weights["annual_energy"] * df["energy_score"]
            + weights["annual_irradiation"] * df["irradiation_score"]
            + weights["performance_ratio"] * df["performance_score"]
            + weights["seasonal_stability"] * df["stability_score"]
        )

        # Classify suitability levels
        df["suitability_class"] = pd.cut(
            df["suitability_score"],
            bins=[0, 0.3, 0.6, 0.8, 1.0],
            labels=["Low", "Moderate", "High", "Excellent"],
        )

        self.suitability_scores = df
        return df

    def identify_optimal_locations(self, top_n=10, min_distance_km=5):
        """
        Identify optimal locations for PV installations with spatial constraints.

        Parameters:
        -----------
        top_n : int
            Number of top locations to identify
        min_distance_km : float
            Minimum distance between selected locations in kilometers

        Returns:
        --------
        pd.DataFrame : Optimal locations
        """

        if self.suitability_scores is None:
            raise ValueError(
                "No suitability scores calculated. Run calculate_suitability_score first."
            )

        df = self.suitability_scores.copy()
        df = df.sort_values("suitability_score", ascending=False)

        # Convert to geodataframe for spatial operations
        geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        # Convert to projected CRS for distance calculations
        gdf = gdf.to_crs("EPSG:3857")  # Web Mercator

        selected_locations = []
        remaining_points = gdf.copy()

        min_distance_m = min_distance_km * 1000  # Convert to meters

        for i in range(min(top_n, len(remaining_points))):
            # Select point with highest suitability score
            best_point = remaining_points.iloc[0]
            selected_locations.append(best_point)

            # Remove points within minimum distance
            distances = remaining_points.geometry.distance(best_point.geometry)
            remaining_points = remaining_points[distances >= min_distance_m]

            if len(remaining_points) == 0:
                break

        # Convert back to WGS84 and return as DataFrame
        selected_gdf = gpd.GeoDataFrame(selected_locations, crs="EPSG:3857")
        selected_gdf = selected_gdf.to_crs("EPSG:4326")

        # Extract coordinates
        selected_gdf["longitude"] = selected_gdf.geometry.x
        selected_gdf["latitude"] = selected_gdf.geometry.y

        return selected_gdf.drop("geometry", axis=1)

    def create_suitability_map(self, figsize=(12, 8), save_path=None):
        """
        Create a visualization of the suitability analysis results.

        Parameters:
        -----------
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """

        if self.suitability_scores is None:
            raise ValueError(
                "No suitability scores calculated. Run calculate_suitability_score first."
            )

        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(
            "Photovoltaic Suitability Analysis Results", fontsize=16, fontweight="bold"
        )

        df = self.suitability_scores

        # 1. Suitability Score Map
        ax1 = axes[0, 0]
        scatter = ax1.scatter(
            df["longitude"],
            df["latitude"],
            c=df["suitability_score"],
            cmap="RdYlGn",
            s=50,
            alpha=0.7,
            edgecolors="black",
            linewidth=0.5,
        )
        ax1.set_xlabel("Longitude")
        ax1.set_ylabel("Latitude")
        ax1.set_title("Suitability Score Distribution")
        plt.colorbar(scatter, ax=ax1, label="Suitability Score")

        # 2. Annual Energy Production
        ax2 = axes[0, 1]
        scatter2 = ax2.scatter(
            df["longitude"],
            df["latitude"],
            c=df["annual_energy_kwh"],
            cmap="plasma",
            s=50,
            alpha=0.7,
            edgecolors="black",
            linewidth=0.5,
        )
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")
        ax2.set_title("Annual Energy Production (kWh/year)")
        plt.colorbar(scatter2, ax=ax2, label="Energy (kWh/year)")

        # 3. Suitability Class Distribution
        ax3 = axes[1, 0]
        class_counts = df["suitability_class"].value_counts()
        colors = ["red", "orange", "lightgreen", "darkgreen"]
        ax3.pie(
            class_counts.values,
            labels=class_counts.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        ax3.set_title("Suitability Class Distribution")

        # 4. Performance Metrics Correlation
        ax4 = axes[1, 1]
        correlation_data = df[
            [
                "annual_energy_kwh",
                "annual_irradiation_kwh_m2",
                "performance_ratio",
                "suitability_score",
            ]
        ].corr()
        sns.heatmap(
            correlation_data,
            annot=True,
            cmap="coolwarm",
            center=0,
            ax=ax4,
            square=True,
            linewidths=0.5,
        )
        ax4.set_title("Performance Metrics Correlation")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Map saved to {save_path}")

        plt.show()

    def generate_report(self, top_locations=None):
        """
        Generate a comprehensive analysis report.

        Parameters:
        -----------
        top_locations : pd.DataFrame, optional
            Top locations from identify_optimal_locations

        Returns:
        --------
        str : Formatted report
        """

        if self.suitability_scores is None:
            raise ValueError("No suitability scores calculated.")

        df = self.suitability_scores

        report = """
PHOTOVOLTAIC SUITABILITY ANALYSIS REPORT
=====================================

ANALYSIS SUMMARY:
- Total locations analyzed: {total_locations}
- Analysis area: {min_lat:.3f}°N to {max_lat:.3f}°N, {min_lon:.3f}°E to {max_lon:.3f}°E
- Average suitability score: {avg_score:.3f}
- Best location score: {best_score:.3f}

ENERGY PRODUCTION STATISTICS:
- Average annual energy production: {avg_energy:.1f} kWh/year
- Maximum annual energy production: {max_energy:.1f} kWh/year
- Average annual irradiation: {avg_irradiation:.1f} kWh/m²/year
- Average performance ratio: {avg_performance:.3f}

SUITABILITY CLASSIFICATION:
- Excellent locations: {excellent_count} ({excellent_pct:.1f}%)
- High suitability locations: {high_count} ({high_pct:.1f}%)
- Moderate suitability locations: {moderate_count} ({moderate_pct:.1f}%)
- Low suitability locations: {low_count} ({low_pct:.1f}%)

RECOMMENDATIONS:
{recommendations}
        """.format(
            total_locations=len(df),
            min_lat=df["latitude"].min(),
            max_lat=df["latitude"].max(),
            min_lon=df["longitude"].min(),
            max_lon=df["longitude"].max(),
            avg_score=df["suitability_score"].mean(),
            best_score=df["suitability_score"].max(),
            avg_energy=df["annual_energy_kwh"].mean(),
            max_energy=df["annual_energy_kwh"].max(),
            avg_irradiation=df["annual_irradiation_kwh_m2"].mean(),
            avg_performance=df["performance_ratio"].mean(),
            excellent_count=len(df[df["suitability_class"] == "Excellent"]),
            excellent_pct=len(df[df["suitability_class"] == "Excellent"])
            / len(df)
            * 100,
            high_count=len(df[df["suitability_class"] == "High"]),
            high_pct=len(df[df["suitability_class"] == "High"]) / len(df) * 100,
            moderate_count=len(df[df["suitability_class"] == "Moderate"]),
            moderate_pct=len(df[df["suitability_class"] == "Moderate"]) / len(df) * 100,
            low_count=len(df[df["suitability_class"] == "Low"]),
            low_pct=len(df[df["suitability_class"] == "Low"]) / len(df) * 100,
            recommendations=self._generate_recommendations(df, top_locations),
        )

        return report

    def _generate_recommendations(self, df, top_locations):
        """Generate recommendations based on analysis results."""

        recommendations = []

        # General recommendations
        excellent_locations = df[df["suitability_class"] == "Excellent"]
        if len(excellent_locations) > 0:
            best_location = excellent_locations.loc[
                excellent_locations["suitability_score"].idxmax()
            ]
            recommendations.append(
                f"- Best location identified at {best_location['latitude']:.3f}°N, "
                f"{best_location['longitude']:.3f}°E with {best_location['annual_energy_kwh']:.0f} kWh/year potential"
            )

        # Energy production recommendations
        high_energy_threshold = df["annual_energy_kwh"].quantile(0.75)
        high_energy_locations = len(
            df[df["annual_energy_kwh"] >= high_energy_threshold]
        )
        recommendations.append(
            f"- {high_energy_locations} locations show high energy production potential (≥{high_energy_threshold:.0f} kWh/year)"
        )

        # Seasonal stability recommendations
        stable_locations = df[
            df["seasonal_variation"] < df["seasonal_variation"].median()
        ]
        recommendations.append(
            f"- {len(stable_locations)} locations show good seasonal stability for consistent energy production"
        )

        # Performance ratio recommendations
        high_performance_locations = df[df["performance_ratio"] > 0.8]
        recommendations.append(
            f"- {len(high_performance_locations)} locations have high performance ratios (>0.8)"
        )

        return "\n".join(recommendations)


# Example usage with improved error handling and proper land coordinates
if __name__ == "__main__":
    # Initialize the analyzer
    analyzer = PVSuitabilityAnalyzer()

    # Example regions with proper land coordinates:

    # 1. Andalusia, Spain (excellent solar potential)
    andalusia_bounds = (-6.0, 36.0, -1.7, 38.7)

    # 2. Extremadura, Spain (good solar potential)
    extremadura_bounds = (-7.5, 38.0, -4.0, 40.5)

    # 3. Castilla-La Mancha, Spain (central Spain)
    castilla_bounds = (-5.5, 38.5, -1.0, 40.5)

    # 4. Provence, France (good solar potential)
    provence_bounds = (4.0, 43.0, 7.5, 44.5)

    # 5. Tuscany, Italy (good solar potential)
    tuscany_bounds = (9.5, 42.5, 12.5, 44.5)

    # Choose a region for analysis
    region_name = "Andalusia, Spain"
    bounds = andalusia_bounds

    print(f"Analyzing solar potential in {region_name}")
    print(f"Bounds: {bounds}")

    try:
        # Test with a single point first (Seville, Spain)
        test_lat, test_lon = 37.3891, -5.9845
        print(f"\nTesting API connection with coordinates: {test_lat}, {test_lon}")

        if analyzer.validate_coordinates(test_lat, test_lon):
            print("Coordinates validation passed!")
            test_data = analyzer.fetch_pvgis_data(test_lat, test_lon)
            if test_data:
                print("API connection successful!")
                print(f"Sample data structure: {list(test_data.keys())}")
                if "outputs" in test_data and "totals" in test_data["outputs"]:
                    totals = test_data["outputs"]["totals"]
                    if "fixed" in totals:
                        print(
                            f"Test location annual energy: {totals['fixed']['E_y']:.0f} kWh/year"
                        )
            else:
                print("API connection failed. Please check your internet connection.")
                exit(1)
        else:
            print("Test coordinates failed validation!")
            exit(1)

        # Analyze the grid area with appropriate spacing
        print(f"\nStarting PV suitability analysis for {region_name}...")
        grid_results = analyzer.analyze_grid_area(
            bounds, grid_spacing=0.2, delay_between_requests=0.3
        )

        if len(grid_results) > 0:
            print(f"Successfully analyzed {len(grid_results)} land-based locations")

            # Calculate suitability scores
            print("Calculating suitability scores...")
            suitability_results = analyzer.calculate_suitability_score()

            # Identify optimal locations
            print("Identifying optimal locations...")
            optimal_locations = analyzer.identify_optimal_locations(
                top_n=5, min_distance_km=20
            )

            # Create visualization
            print("Creating suitability map...")
            analyzer.create_suitability_map(figsize=(15, 10))

            # Generate report
            print(f"\nGenerating analysis report for {region_name}...")
            report = analyzer.generate_report(optimal_locations)
            print(report)

            # Display top locations
            print(f"\nTOP OPTIMAL LOCATIONS IN {region_name.upper()}:")
            print("=" * 50)
            for i, location in optimal_locations.iterrows():
                print(
                    f"{i+1}. Location: {location['latitude']:.3f}°N, {location['longitude']:.3f}°E"
                )
                print(f"   Suitability Score: {location['suitability_score']:.3f}")
                print(f"   Annual Energy: {location['annual_energy_kwh']:.0f} kWh/year")
                print(
                    f"   Irradiation: {location['annual_irradiation_kwh_m2']:.0f} kWh/m²/year"
                )
                print(f"   Performance Ratio: {location['performance_ratio']:.3f}")
                print()
        else:
            print(
                "No valid data points retrieved. All points may be over water or outside PVGIS coverage."
            )
            print("Try adjusting the bounds to focus on land areas.")

    except Exception as e:
        print(f"Analysis failed with error: {e}")
        print("Please check your internet connection and try again.")

    # Additional example for other regions
    print("\n" + "=" * 60)
    print("OTHER AVAILABLE REGIONS FOR ANALYSIS:")
    print("=" * 60)
    print("1. Andalusia, Spain:", andalusia_bounds)
    print("2. Extremadura, Spain:", extremadura_bounds)
    print("3. Castilla-La Mancha, Spain:", castilla_bounds)
    print("4. Provence, France:", provence_bounds)
    print("5. Tuscany, Italy:", tuscany_bounds)
    print("\nTo analyze a different region, change the 'bounds' variable in the code.")


# The code now defaults to Andalusia, Spain
analyzer = PVSuitabilityAnalyzer()

# Test with Seville first
test_data = analyzer.fetch_pvgis_data(37.3891, -5.9845)  # Seville

# Then analyze the full region
bounds = (-6.0, 36.0, -1.7, 38.7)  # Andalusia
grid_results = analyzer.analyze_grid_area(bounds, grid_spacing=0.2)
