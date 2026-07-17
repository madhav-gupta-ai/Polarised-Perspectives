"""Agent-based model of two competing political WhatsApp campaigns.

A population of neutral citizens is connected in a random regular graph.
Left- and right-aligned influencers broadcast their campaign to their
connections; a citizen whose net persuasion crosses their personal
susceptibility threshold joins that side and re-broadcasts the campaign
once to their own connections. The run ends when allegiances stabilise
(or after a fixed number of steps).
"""

from dataclasses import dataclass

import networkx as nx
import numpy as np

from . import config


@dataclass
class SimulationResult:
    graph: nx.Graph          # final network, node attributes hold each agent's state
    history: list            # (left, right, neutral) civilian counts after each step
    mood_changes: int        # times a convinced citizen reverted to neutral
    converged_at: int | None  # step at which counts stabilised (None if they never did)

    @property
    def final_counts(self):
        return self.history[-1]


def build_network(N, D, IL, IR, DL, DR, PL, PR, SM, SD, seed=None):
    """Build the citizen network, attach influencers, and deliver their initial broadcasts.

    Civilians are nodes 0..N-1 in a random regular graph of degree D.
    Influencers are extra nodes with fixed allegiance, each wired to a
    random set of civilians (DL/DR of them per influencer).
    """
    rng = np.random.default_rng(seed)
    G = nx.random_regular_graph(D, N, seed=seed)

    # Add influencers and connect them to civilians
    for i in range(IL):
        influencer = N + i
        G.add_node(influencer)
        for target in rng.choice(N, size=DL, replace=False):
            G.add_edge(influencer, int(target))
        G.nodes[influencer].update(
            persuasion=0, susceptibility=0, state='left', broadcast=False)

    for i in range(IR):
        influencer = N + IL + i
        G.add_node(influencer)
        for target in rng.choice(N, size=DR, replace=False):
            G.add_edge(influencer, int(target))
        G.nodes[influencer].update(
            persuasion=0, susceptibility=0, state='right', broadcast=False)

    # Initialize attributes for civilians
    susceptibilities = rng.normal(SM, SD, N)
    for i in range(N):
        G.nodes[i].update(
            persuasion=0.0, susceptibility=max(susceptibilities[i], 0),
            state='neutral', broadcast=False)

    # Broadcast initial messages from influencers (time step 0)
    for i in range(N, N + IL):
        for neighbor in G.neighbors(i):
            G.nodes[neighbor]['persuasion'] += PL

    for i in range(N + IL, N + IL + IR):
        for neighbor in G.neighbors(i):
            G.nodes[neighbor]['persuasion'] += PR

    return G


def simulate(N=config.N, D=config.D, IL=config.IL, IR=config.IR,
             DL=config.DL, DR=config.DR, PL=config.PL, PR=config.PR,
             SM=config.SM, SD=config.SD, max_steps=config.MAX_STEPS,
             early_stop=True, seed=None, verbose=False):
    """Run the simulation and return a SimulationResult.

    With early_stop=True the run ends as soon as the left/right/neutral
    counts repeat between consecutive steps (convergence); with
    early_stop=False it always runs the full max_steps, which is how the
    tuning objective evaluates a parameter set.
    """
    G = build_network(N, D, IL, IR, DL, DR, PL, PR, SM, SD, seed=seed)

    history = []
    mood_changes = 0
    converged_at = None
    prev_counts = None

    for step in range(max_steps):
        # Update states based on persuasions
        for i in range(N):  # Only update states for civilians
            p = G.nodes[i]['persuasion']
            s = G.nodes[i]['susceptibility']
            if p >= s and G.nodes[i]['state'] != 'right':
                # Newly turned right
                G.nodes[i]['state'] = 'right'
                G.nodes[i]['broadcast'] = True
            elif p <= -s and G.nodes[i]['state'] != 'left':
                # Newly turned left
                G.nodes[i]['state'] = 'left'
                G.nodes[i]['broadcast'] = True
            elif -s < p < s:
                if G.nodes[i]['state'] != 'neutral':
                    mood_changes += 1
                G.nodes[i]['state'] = 'neutral'

        # Newly convinced citizens re-broadcast their side's campaign once
        for i in range(N):
            if G.nodes[i]['broadcast']:
                if G.nodes[i]['state'] == 'right':
                    for neighbor in G.neighbors(i):
                        G.nodes[neighbor]['persuasion'] += PR
                elif G.nodes[i]['state'] == 'left':
                    for neighbor in G.neighbors(i):
                        G.nodes[neighbor]['persuasion'] += PL
                G.nodes[i]['broadcast'] = False

        states = [G.nodes[i]['state'] for i in range(N)]
        counts = (states.count('left'), states.count('right'), states.count('neutral'))
        history.append(counts)
        if verbose:
            print(f'step {step + 1}: left={counts[0]} right={counts[1]} neutral={counts[2]}')

        if early_stop and counts == prev_counts:
            converged_at = step + 1
            break
        prev_counts = counts

    return SimulationResult(graph=G, history=history,
                            mood_changes=mood_changes, converged_at=converged_at)
