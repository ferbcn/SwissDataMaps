import os
import json
import time
import overpy


def get_data_overpy(country_iso_a2, tag_key, tag_value):
    names = []
    lats = []
    longs = []
    websites = []
    temp_dir = "temp"
    file_path = f'{temp_dir}/{tag_key}_{tag_value}.json'

    # if cached version exists and is not older than 24h, load from file
    if os.path.exists(file_path) and os.path.getctime(file_path) > time.time() - (60 * 60 * 24):
        print('Loading cached data...')
        with open(file_path, 'r') as f:
            data_dict = json.load(f)

    else:
        print('No cached data found, retrieving fresh API data...')
        api = overpy.Overpass()
        r = api.query("""
                ( area["ISO3166-1"="{0}"][admin_level=2]; )->.searchArea;
                ( node[{1}={2}]( area.searchArea );
                );
                out center;""".format(country_iso_a2, tag_key, tag_value))

        #print(f"Received {len(r.nodes)} nodes for {tag_value}")
        for node in r.nodes:
            try:  # not all entries have a name
                names.append(node.tags.get('name'))
            except KeyError:
                names.append("n/a")

            longs.append(float(node.lon))
            lats.append(float(node.lat))
            websites.append(node.tags.get('website'))

        data_dict = dict(
            names=names,
            longs=longs,
            lats=lats,
            websites=websites
        )

        with open(file_path, 'w') as f:
            json.dump(data_dict, f)

    return data_dict
