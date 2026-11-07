"""Offline data-collection wrapper (local tooling, NEVER submitted): wraps a lab6 team and records,
for each of our agents' moves while it attacks, a feature vector of its own observation plus the
quantities needed for outcome labels. Nothing is written to disk: the log lives on the agent object
(`agent.rl_log`), and eval/rl/collect.py reads it from the finished Game in the same process.

create_team(first, second, is_red, team=<path>, **opts)
"""
import importlib.util
import os
import sys

_MODS = {}

FEATURE_NAMES = ['carried', 'dist_home', 'ghost1', 'ghost2', 'scared1', 'food_left', 'food_near1',
                 'food_in5', 'time_left', 'score', 'is_pacman', 'capsule_d', 'deadend_depth',
                 'ghost1_visible', 'mate_attacking']


def _load(path):
    if path not in _MODS:
        name = 'rl_team_%d' % len(_MODS)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MODS[path] = mod
    return _MODS[path]


def features(agent, gs):
    """Features of the agent's state from its own observation (lab6 agent internals)."""
    m = agent.map
    pos = gs.get_agent_position(agent.index)
    me = gs.get_agent_state(agent.index)
    carried = me.num_carrying
    food = agent.get_food(gs).as_list()
    ghosts = agent.plan_ghosts(gs)  # [(cell, scared)] visible or belief cells
    vis = set(p for i, p, inv in agent.visible_enemies(gs) if not inv)
    gd = sorted((m.d(g, pos), s, g in vis) for g, s in ghosts)
    g1 = gd[0] if gd else (99, 0, False)
    g2 = gd[1] if len(gd) > 1 else (99, 0, False)
    row = m.dist[pos]
    fds = sorted(row.get(f, 999) for f in food)
    caps = agent.get_capsules(gs)
    mate = [t for t in agent.get_team(gs) if t != agent.index]
    mate_att = 0.0
    if mate:
        st = gs.get_agent_state(mate[0])
        mate_att = 1.0 if st.is_pacman else 0.0
    return [
        min(carried, 20) / 20.0,
        min(m.dist_home[pos], 40) / 40.0,
        min(g1[0], 15) / 15.0,
        min(g2[0], 15) / 15.0,
        min(g1[1], 40) / 40.0,
        len(food) / 30.0,
        (min(fds[0], 30) / 30.0) if fds else 1.0,
        sum(1 for d in fds if d <= 5) / 10.0,
        (gs.data.timeleft // 4) / 300.0,
        max(-20, min(20, agent.get_score(gs))) / 20.0,
        1.0 if me.is_pacman else 0.0,
        (min(min(row.get(c, 999) for c in caps), 30) / 30.0) if caps else 1.0,
        min(m.depth.get(pos, 0), 10) / 10.0,
        1.0 if g1[2] else 0.0,
        mate_att,
    ]


def create_team(first_index, second_index, is_red, team=None, **opts):
    mod = _load(team)
    agents = mod.create_team(first_index, second_index, is_red, **opts)
    for a in agents:
        _wrap(a)
    return agents


def _wrap(agent):
    orig_choose = agent.choose_action
    orig_register = agent.register_initial_state

    def register(gs):
        orig_register(gs)
        agent.rl_log = []
        agent.rl_start = gs.get_agent_position(agent.index)

    def choose(gs):
        action = orig_choose(gs)  # perceive() runs inside, so the belief is current
        try:
            st = gs.get_agent_state(agent.index)
            attacking = getattr(agent, 'role', 'attack') == 'attack' or st.is_pacman
            agent.rl_log.append((features(agent, gs), st.num_carrying, st.num_returned,
                                 gs.get_agent_position(agent.index), attacking))
        except Exception as exc:  # tooling must never break the game; keep the reason
            agent.rl_log.append(('error', repr(exc)))
        return action

    agent.register_initial_state = register
    agent.choose_action = choose
