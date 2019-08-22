from os import listdir, path

data_dir = "data/instagram"


ikeys_connections = set(open(
    data_dir + '/ikeybenz/connections.txt').read().splitlines())


def correct_mutual_follwers():
    for account in listdir(data_dir):
        mutuals_path = f"{data_dir}/{account}/mutuals_with_ikeybenz.txt"
        if account is "ikeybenz" or not path.exists(mutuals_path):
            continue

        mutuals = set(open(mutuals_path).read().splitlines())
        corrected = mutuals.intersection(ikeys_connections)

        with open(mutuals_path, 'w') as out:
            out.write("\n".join(corrected))


def check_mutual_correctness():
    for account in listdir(data_dir):
        mutuals_path = f"{data_dir}/{account}/mutuals_with_ikeybenz.txt"
        if account is "ikeybenz" or not path.exists(mutuals_path):
            continue

        stored_mutuals = set(open(mutuals_path).read().splitlines())
        extras = stored_mutuals.difference(ikeys_connections)
        if len(extras) > 0:
            print(account, "has extra mutuals:", extras)


if __name__ == '__main__':
    correct_mutual_follwers()
    check_mutual_correctness()
