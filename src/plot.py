"""Network views: a plain spring layout and a clustered allegiance layout."""

import matplotlib.pyplot as plt
import networkx as nx

STATE_COLORS = {'left': 'blue', 'right': 'red', 'neutral': 'black'}


def allegiance_positions(G, N, seed=None):
    """Positions with citizens clustered by allegiance: left | neutral | right.

    Each cluster gets its own internal spring layout, shifted onto its side
    of the canvas; influencers are pinned in columns at the outer edges.
    """
    pos = {}
    for state, x_offset in (('left', -2.5), ('neutral', 0.0), ('right', 2.5)):
        group = [n for n in range(N) if G.nodes[n]['state'] == state]
        for n, (x, y) in nx.spring_layout(G.subgraph(group), seed=seed).items():
            pos[n] = (0.9 * x + x_offset, 1.4 * y)

    for state, x_column in (('left', -4.0), ('right', 4.0)):
        column = [n for n in G.nodes if n >= N and G.nodes[n]['state'] == state]
        step = 2.8 / max(len(column) - 1, 1)
        for k, n in enumerate(column):
            pos[n] = (x_column, -1.4 + k * step)

    return pos


def draw_network(G, N, ax=None, clustered=False, seed=None, title=None):
    """Draw the network coloured by state (blue=left, black=neutral, red=right).

    Influencers are drawn larger with a gold outline. With clustered=True,
    citizens are grouped by allegiance instead of the plain spring layout.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    if clustered:
        pos = allegiance_positions(G, N, seed=seed)
    else:
        pos = nx.spring_layout(G, seed=seed)

    civilians = [n for n in G.nodes if n < N]
    influencers = [n for n in G.nodes if n >= N]

    nx.draw_networkx_edges(G, pos, ax=ax, width=0.05, alpha=0.4)
    nx.draw_networkx_nodes(
        G, pos, nodelist=civilians, node_size=20, ax=ax,
        node_color=[STATE_COLORS[G.nodes[n]['state']] for n in civilians])
    nx.draw_networkx_nodes(
        G, pos, nodelist=influencers, node_size=110, ax=ax,
        node_color=[STATE_COLORS[G.nodes[n]['state']] for n in influencers],
        edgecolors='goldenrod', linewidths=1.2)

    if title:
        ax.set_title(title)
    ax.set_axis_off()
    return ax


def plot_history(history, ax=None, title=None):
    """Plot left/right/neutral counts over time for one simulation run."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    x = list(range(1, len(history) + 1))
    ax.plot(x, [c[0] for c in history], color='blue', label='Left')
    ax.plot(x, [c[1] for c in history], color='red', label='Right')
    ax.plot(x, [c[2] for c in history], color='black', label='Neutral')
    ax.set_xlabel('Time step')
    ax.set_ylabel('Number of citizens')
    if title:
        ax.set_title(title)
    ax.legend()
    return ax
