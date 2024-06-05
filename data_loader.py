from string_decode import decode_string


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

    # Convert the GeoDataFrame to GeoJSON
    geojson_data = json.loads(gdf.to_json())
    print("GeoJSON data loaded")

    # print(gdf.columns)
    gdf['DICHTE'] = gdf['EINWOHNERZ'] / gdf['KANTONSFLA'] * 1000  # BEZIRKSFLA, KANTONSFLA
    z_max = 10000

    # Correct string encoding for the NAME column
    gdf['NAME'] = gdf['NAME'].apply(decode_string)

    # Save the GeoDataFrame to a GeoJSON file
    gdf.to_file("static/gdf_gem.json", driver='GeoJSON')

