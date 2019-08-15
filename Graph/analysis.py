from os import listdir
from collections import Counter
from networkx.classes import Graph
from networkx.algorithms import community
import networkx as nx
from clustering import HCS


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


def order_influencers(g: Graph, n=5):
    '''
        Takes a networkx graph object and returns the n most connected vertices.
        In a social network, these would be the most influential accounts.
    '''
    influencers = {}
    for account in g.get_vertices():
        influencers[account] = len(g.get_vertex(account).get_neighbors())

    influencers = Counter(influencers)
    return influencers.most_common(n)


def get_connections_between(g: Graph, acc1: str, acc2: str):
    '''
      Takes a networkx graph object and two accounts. Returns the accounts in the
      smallest path between them.
    '''
    return nx.shortest_path(g, acc1, acc2)


def display_communities(g: Graph):
    '''
        Prints approzimations to stdout for 'communities' amongst the accounts
        in the input graph. 
    '''
    communities = community.girvan_newmnan(g)
    for community in communities:
        print("NEW COMMUNITY:")
        for group in community:
            print("\tNEW GROUP:")
            for member in group:
                print('\t\t' + member)


if __name__ == '__main__':
    g = make_graph()
    # print(order_influencers(g))
    # print(get_connections_between(g, 'your friend', 'your other friend'))
    # display_communities(g)
