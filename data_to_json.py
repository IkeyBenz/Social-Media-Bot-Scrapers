"""
Goes through the folders in data/instagram and writes a json object, containing
the nodes and all of their links, to data.json. Once data.json exists, you'll be
able to open index.html and see a D3.js visualization of your social network.

To be able to run this as a script right out of the box, replace all 'ikeybenz'
in this file, with your instagram username.
"""
import json
from os import listdir, path
from clean_data import correct_mutual_follwers

data_dir = "data/instagram"
ikeys_connections = set(open(
    data_dir + '/ikeybenz/connections.txt').read().splitlines())


def get_links():
    links = []
    for followed in listdir(data_dir):
        mutuals_path = f"{data_dir}/{followed}/mutuals_with_ikeybenz.txt"
        if followed is "ikeybenz" or not path.exists(mutuals_path):
            continue

        for follower in open(mutuals_path).read().splitlines():
            links.append({"source": follower, "target": followed})
    print("Links", len(links))
    return links


if __name__ == '__main__':
    correct_mutual_follwers()

    data = {
        "nodes": [
            {"id": acc, "group": 1}
            for acc in ikeys_connections
        ] + [{"id": "ikeybenz", "group": 1}],
        "links": get_links()
    }

    with open('data.json', 'w') as out:
        json.dump(data, out)
