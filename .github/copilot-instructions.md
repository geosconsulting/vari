# Copilot Instructions for AI Coding Agents

## Project Overview
This repository is a Python-based workspace focused on geospatial analysis, visualization, and dashboarding. It includes scripts, notebooks, and shell scripts for data processing, visualization, and integration with external services (e.g., GeoServer, PostGIS).

## Key Components
- **Python Scripts**: Core logic for data fetching, expansion analysis, and suitability analysis (e.g., `expansion_prova.py`, `geoserver_wfs_fetch.py`, `pv_suitability_analysis.py`).
- **Notebooks**: Interactive analysis and visualization (e.g., `voila_1.ipynb`, `getting_started_torchgeo.ipynb`).
- **Shell Scripts**: Data loading into PostGIS from GeoPackage files (`shell-scrips/`).
- **Tests**: Pytest-based unit tests in `tests/` and `vari_test/`.
- **Data**: Geospatial data stored in `gpkgs/`.

## Developer Workflows
- **Testing**: Run tests using `pytest` (configured via `pytest.ini`). Example: `pytest tests/` or `pytest vari_test/`.
- **Visualization**: Use Jupyter Notebooks and Voila for dashboarding. Notebooks often use Plotly for interactive charts.
- **Data Loading**: Use shell scripts in `shell-scrips/` to load `.gpkg` files into PostGIS. Example: `bash shell-scrips/load_gpkg_to_postgis.sh`.
- **Debugging**: Debug scripts interactively in notebooks or use `testing_debugger.py` in `vari_test/`.

## Project-Specific Patterns
- **Geospatial Data**: Data is primarily handled in GeoPackage format and processed using Pandas, NumPy, and geospatial libraries.
- **Visualization**: Plotly is the preferred library for interactive charts. Dashboards are rendered via Voila.
- **Warnings**: Suppressed globally in notebooks for cleaner output.
- **Display**: Use `IPython.display` for rich HTML output in notebooks.
- **Test Structure**: Tests are organized by feature/module, with separate folders for main and experimental code.

## Integration Points
- **GeoServer**: Fetches geospatial data via WFS in `geoserver_wfs_fetch.py`.
- **PostGIS**: Data loading via shell scripts; integration is manual and not automated in Python.
- **TorchGeo**: Experimental deep learning workflows in `torch-based/`.

## Conventions
- **File Naming**: Scripts and notebooks are named by function or experiment.
- **Folder Structure**: Main code in root, experiments in `torch-based/`, tests in `tests/` and `vari_test/`.
- **Python Version**: Multiple `.pyc` files suggest compatibility with Python 3.12+.

## Examples
- To visualize data, see `voila_1.ipynb` for Plotly and Voila usage.
- For data loading, use `shell-scrips/load_gpkg_to_postgis.sh`.
- For expansion analysis, see `expansion_prova.py` and related tests in `tests/test_expansion.py`.

---

If any section is unclear or missing important details, please provide feedback or specify which workflows or patterns need further documentation.