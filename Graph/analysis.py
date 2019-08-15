from os import listdir
from collections import Counter
from networkx.classes import Graph
import networkx as nx
from clustering import HCS
from networkx import drawing


DATA_PATH = '../data/instagram'


def make_graph():
    g = Graph()
    accounts = listdir(DATA_PATH)

    for account in accounts:
        g.add_node(account)

    direct_connections = open(
        '../data/instagram/ikeybenz/connections.txt').read().splitlines()
    for connection in direct_connections:
        g.add_edge('ikeybenz', connection)
        g.add_edge(connection, 'ikeybenz')

    for account in accounts:
        try:  # Some connections have no mutual followers with me
            mutual_followers_of_account = open(
                f'{DATA_PATH}/{account}/mutuals_with_ikeybenz.txt').read().splitlines()
        except:  # In that case, skip current account
            continue

        for follower in mutual_followers_of_account:
            g.add_edge(follower, account)

    return g


def order_influencers(g: Graph):
    influencers = {}
    for account in g.get_vertices():
        influencers[account] = len(g.get_vertex(account).get_neighbors())

    influencers = Counter(influencers)
    print(influencers.most_common(5))


if __name__ == '__main__':
    print('Making graph...')
    g = make_graph()
    print('GRAPH MADE')
    # g = HCS(g)
    print('Waiting for graph to draw maybe>??')
    drawing.draw_networkx(g, show_labels=True)
    print("Graph has supposedly been built")
