import geopandas as gpd
import pandas as pd

from olmoearth_projects.utils.label_quality.spatial_clustering import spatial_clustering


def test_spatial_clustering_classification() -> None:
    df = pd.DataFrame(
        {
            "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            # highly clustered labels
            "label": [0, 0, 0, 1, 1],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
    )
    assert spatial_clustering(gdf[["label", "geometry"]], k=1) == 1

    # now we reduce the spatial clustering
    gdf.label = [1, 2, 3, 0, 1]
    assert spatial_clustering(gdf[["label", "geometry"]], k=1) == 0


def test_spatial_clustering_regression() -> None:
    df = pd.DataFrame(
        {
            "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            # highly clustered labels
            "label": [0.5, 0.5, 0.5, 1.5, 1.5],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
    )
    assert spatial_clustering(gdf[["label", "geometry"]], k=1) == 0.0

    # now we reduce the spatial clustering, so MSE goes up
    gdf.label = [1.5, 0.5, 2.5, 0.5, 1.5]
    assert spatial_clustering(gdf[["label", "geometry"]], k=1) == 1
