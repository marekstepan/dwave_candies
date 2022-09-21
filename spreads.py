import csv
from datetime import date

# Import networkx for graph tools
import networkx as nx

import os

# Import dwave_networkx for d-wave graph tools/functions
import dwave_networkx as dnx

# Set the solver we're going to use
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

sampler = EmbeddingComposite(DWaveSampler(endpoint='https://cloud.dwavesys.com/sapi',
                                          token=os.environ['SAPI_TOKEN'], solver='DW_2000Q_6'))

with open('/home/marek/projects/dwave_candies/data/commodity_spreads.csv', 'r') as read_spreads:
    csv_reader = csv.reader(read_spreads, delimiter=';')
    next(csv_reader)
    spreads = []
    for row in csv_reader:
        spreads.append(row)

# Create empty graph
G = nx.Graph()

# Add nodes average_net_profit/MAE * -1
nodes = []
for spread in spreads:
    node = (spread[0], {"profitability": float(spread[4]) / float(spread[5]) * (-1)})
    nodes.append(node)

G.add_nodes_from(nodes)

# Create list of edges
edges = []

for i in range(0, len(spreads) - 1):
    if (int(spreads[i][2][0:2].lstrip("0")) < int(spreads[i][3][0:2].lstrip("0"))) or \
            ((int(spreads[i][2][0:2].lstrip("0")) == int(spreads[i][3][0:2].lstrip("0"))) and
             (int(spreads[i][2][3:].lstrip("0")) <= int(spreads[i][3][3:].lstrip("0")))):
        exit_year1 = 2021
    else:
        exit_year1 = 2022

    entry_day = date(2021, int(spreads[i][2][0:2].lstrip("0")),
                     int(spreads[i][2][3:].lstrip("0"))).timetuple().tm_yday
    exit_day = date(exit_year1, int(spreads[i][3][0:2].lstrip("0")),
                    int(spreads[i][3][3:].lstrip("0"))).timetuple().tm_yday
    for j in range(0, len(spreads) - i - 1):
        if (int(spreads[j + i + 1][2][0:2].lstrip("0")) < int(spreads[i][3][0:2].lstrip("0"))) or \
                ((int(spreads[j + i + 1][2][0:2].lstrip("0")) == int(spreads[i][3][0:2].lstrip("0"))) and
                 (int(spreads[j + i + 1][2][3:].lstrip("0")) <= int(spreads[i][3][3:].lstrip("0")))):
            exit_year2 = 2021
        else:
            exit_year2 = 2022
        entry_day_compared = date(2021, int(spreads[j + i + 1][2][0:2].lstrip("0")),
                                  int(spreads[j + i + 1][2][3:].lstrip("0"))).timetuple().tm_yday
        exit_day_compared = date(exit_year2, int(spreads[j + i + 1][3][0:2].lstrip("0")),
                                 int(spreads[j + i + 1][3][3:].lstrip("0"))).timetuple().tm_yday
        if ((entry_day <= entry_day_compared and exit_day >= exit_day_compared) or
                (entry_day_compared < entry_day <= exit_day_compared) or
                (entry_day_compared <= exit_day < exit_day_compared)):
            spread_a_id = "Id_" + str(i + 1)
            spread_b_id = "Id_" + str(j + i + 2)
            edges.append((spread_a_id, spread_b_id))

# Add edges to graph - this also adds the nodes
G.add_edges_from(edges)

# Find the maximum weighted independent set, S
S = dnx.maximum_weighted_independent_set(G, weight="profitability", sampler=sampler, lagrange=2.0, num_reads=10,
                                         label='Spreads selection')

# Print the solution for the user
print('Selected spreads:')
print(S)
