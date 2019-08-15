import random
from os import listdir

import networkx as nx
import matplotlib.pyplot as plt

from analysis import make_graph
from clustering import HCS


def random_nodelist():
    account_path = '../data/instagram/'
    accounts = listdir(account_path)
    rand_accounts = set((random.choice(accounts) for _ in range(10)))

    return rand_accounts


if __name__ == '__main__':
    G = make_graph()

    nx.draw_networkx(G, nodelist=random_nodelist())
    plt.show()
