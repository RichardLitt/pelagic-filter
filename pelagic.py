import argparse
import zipfile
import xml.etree.ElementTree as ET
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point, MultiPolygon, mapping

def extract_kml_from_kmz(kmz_path):
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        # Assuming there's only one .kml file in the KMZ
        kml_file = [name for name in kmz.namelist() if name.endswith('.kml')][0]
        with kmz.open(kml_file) as kml:
            return kml.read()

def kml_to_geojson(kml_content):
    root = ET.fromstring(kml_content)

    # Extracting exterior and interior rings
    exterior_ring = []
    interior_rings = []

    for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        polygon = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon')
        coordinates = polygon.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()

        # Extracting coordinates from the KML
        coordinates_list = [list(map(float, coord.split(','))) for coord in coordinates.split()]

        # Identify exterior and interior rings
        if len(exterior_ring) == 0:
            exterior_ring = coordinates_list
        else:
            interior_rings.append(coordinates_list)

    # Create a Polygon with holes
    polygon_with_holes = Polygon(exterior_ring, interior_rings)

    # Convert the Polygon with holes to GeoJSON
    geojson_data = {
        "type": "Feature",
        "geometry": mapping(MultiPolygon([polygon_with_holes])),
        "properties": {}
    }

    return json.dumps(geojson_data, indent=2)

def kmz_to_geojson(kmz_path, output_geojson_path):
    kml_content = extract_kml_from_kmz(kmz_path)
    geojson_content = kml_to_geojson(kml_content)

    with open(output_geojson_path, 'w') as output_file:
        output_file.write(geojson_content)

def filter_csv_by_polygon(csv_path, geojson_path, output_csv_path):
    # Read the GeoJSON file into a GeoDataFrame
    gdf_polygon = gpd.read_file(geojson_path)

    # Read the CSV file into a DataFrame with tab-separated values
    df = pd.read_csv(csv_path, delimiter='\t', low_memory=False)

    # Identify the columns containing latitude and longitude
    lat_col = 'LATITUDE'  # Replace with the actual column name
    lon_col = 'LONGITUDE'  # Replace with the actual column name

    # Create a GeoDataFrame from the CSV coordinates
    geometry = [Point(lon, lat) for lat, lon in zip(df[lat_col], df[lon_col])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs=gdf_polygon.crs)

    # Spatial join to filter points within the polygon
    filtered_gdf = gpd.sjoin(gdf_points, gdf_polygon, predicate='within')

    # Edit the Sampling Event Identifier column
    sampling_event_column = 'SAMPLING EVENT IDENTIFIER'
    filtered_gdf[sampling_event_column] = 'https://ebird.org/checklist/' + filtered_gdf[sampling_event_column].astype(str)

    # Save the DataFrame with modified Sampling Event Identifiers to CSV
    filtered_gdf.to_csv(output_csv_path, index=False)


def main():
    parser = argparse.ArgumentParser(description='Convert .kmz to GeoJSON and filter CSV by polygon.')
    parser.add_argument('kmz_path', help='Path to the .kmz file')
    parser.add_argument('output_geojson', help='Path to the output GeoJSON file')
    parser.add_argument('csv_path', help='Path to the CSV file')
    parser.add_argument('output_csv', help='Path to the output CSV file')

    args = parser.parse_args()

    # Step 1: Convert .kmz to GeoJSON
    kmz_to_geojson(args.kmz_path, args.output_geojson)

    # Step 2: Filter CSV by polygon
    filter_csv_by_polygon(args.csv_path, args.output_geojson, args.output_csv)

if __name__ == "__main__":
    main()
