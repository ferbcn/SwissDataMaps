import os
from string_decode import decode_string
import geopandas as gpd
import json
import requests
import time

TEMP_DIR = "temp"


class ZueriData:
    def __init__(self):
        self.end_url = "https://www.zuerich.com/en/api/v2/data"
        self.api_url = self.end_url + "?id="
        self.temp_dir = TEMP_DIR

    def get_endpoint_list(self):
        print('Retrieving Zürich Tourism API endpoints...')
        try:
            api_endpoints_raw = requests.get(self.end_url)
            api_ids_names = {item.get('id'): item.get('name').get('de') for item in api_endpoints_raw.json() if not item.get('name').get('de') is None}
        except Exception as e:
            print(f'Error: {e}')
            api_ids_names = {101: 'Error Retrieving data...'}
        return api_ids_names

    def get_api_data(self, api_id=101):
        print(f'Checking for cached version of API endpoint with id {api_id}')
        # Check if the data is already cached and not older than 24h
        if os.path.exists(f'{self.temp_dir}/{api_id}.json') and os.path.getctime(f'{self.temp_dir}/{api_id}.json') > time.time() - (60 * 60 * 24):
            print('Loading cached data...')
            with open(f'{self.temp_dir}/{api_id}.json', 'r') as f:
                data = json.load(f)
            return data
        else:
            print('No cached data found, retrieving fresh API data...')
            try:
                response = requests.get(self.api_url + str(api_id))
                data = response.json()
                with open(f'{self.temp_dir}/{api_id}.json', 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                print(f'Error: {e}')
                data = {}
        return data


def load_transform_save_antenna_data():
    # Prepare antenna data
    filepath = 'static/antennenstandorte-5g_de.json'
    ant_gdf = gpd.read_file(filepath)

    # Use WGS 84 (epsg:4326) as the geographic coordinate system
    ant_gdf = ant_gdf.to_crs(epsg=4326)

    # Convert powercode_de to integer value
    # dictionary to convert antenna power data
    powercodes = {"Sehr Klein": 2, "Klein": 3, "Mittel": 5, "Gross": 10}
    # convert powercode_de to integer value
    ant_gdf["power_int"] = ant_gdf["powercode_de"].apply(lambda x: powercodes.get(x))

    # create lat and lon columns in ant_gdf
    ant_gdf['lat'] = ant_gdf.geometry.y
    ant_gdf['lon'] = ant_gdf.geometry.x

    # Assuming `gdf` is your GeoPandas DataFrame
    ant_gdf.to_file("static/ant_gdf.json", driver='GeoJSON')


def load_transform_save_political_shape_geo_data():
    # Set the file path to the shapefile
    # shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_BEZIRKSGEBIET.shp"
    # shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp"
    shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_HOHEITSGEBIET.shp"
    # load Shape file into GeoDataFrame
    gdf = gpd.GeoDataFrame.from_file(shapefile)

    # Convert to WGS84
    gdf.crs = "EPSG:2056"  # Use CH1903+ / LV95 (epsg:2056)
    # Use WGS84 (epsg:4326) as the geographic coordinate system
    gdf = gdf.to_crs(epsg=4326)

    # print(gdf.columns)
    gdf['DICHTE'] = gdf['EINWOHNERZ'] / gdf['KANTONSFLA'] * 1000  # BEZIRKSFLA, KANTONSFLA

    # Correct string encoding for the NAME column
    gdf['NAME'] = gdf['NAME'].apply(decode_string)

    # Save the GeoDataFrame to a GeoJSON file
    gdf.to_file("static/gdf_gem.json", driver='GeoJSON')


def load_transform_ev_station_data():
    # Load Antenna data from JSON file
    print("Loading EV data...")
    filename = "static/ev_stations.json"
    # ev_gdf = gpd.read_file(filename)
    # count = len(ev_gdf)
    with open(filename, 'r') as f:
        data = json.load(f)
    stations = data.get("EVSEData")[0].get("EVSEDataRecord")

    coordinates = []
    plug_count = []
    for station in stations:
        coordinates.append(station.get("GeoCoordinates").get("Google"))
        plug_count.append(station.get("Plugs"))

    print("Count: ", len(coordinates))
    print("Plug count: ", len(plug_count))
    print("Sample coordinates: ", coordinates[:5])
    print("Sample plug count: ", plug_count[:5])

    from shapely.geometry import Point

    ev_gdf = gpd.GeoDataFrame()
    ev_gdf['lat'] = [float(coord.split(" ")[0]) for coord in coordinates]
    ev_gdf['lon'] = [float(coord.split(" ")[1]) for coord in coordinates]
    # ev_gdf['plugs'] = plug_count
    ev_gdf['geometry'] = [Point(xy) for xy in zip(ev_gdf['lon'], ev_gdf['lat'])]
    ev_gdf.set_geometry('geometry')

    # save to json file
    ev_gdf.to_file("static/ev_gdf.json", driver='GeoJSON')


if __name__ == "__main__":
    # load_transform_save_antenna_data()
    # load_transform_save_political_shape_geo_data()
    load_transform_ev_station_data()
    print("Done.")