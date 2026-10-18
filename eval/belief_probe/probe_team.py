# Probe team for eval/belief_probe/belief_check.py (E-019; local analysis only, never submitted).
# role=ours: loads a team file and logs the defender's belief after each of its moves.
# role=theirs: loads a team file and logs each agent's own true position at its own observation
# (an agent always knows its own position).
import importlib.machinery
import importlib.util
import os
import time

import probe_store


def _load(path, tag):
    path = os.path.abspath(path)
    name = 'probe_target_%s_%s' % (tag, os.path.splitext(os.path.basename(path))[0])
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def create_team(first_index, second_index, is_red, role='ours', team=None, **opts):
    module = _load(team, 'red' if is_red else 'blue')
    for k in [k for k in opts if k.startswith('K_')]:  # override a constant of the loaded lab module
        setattr(module, k[2:], float(opts.pop(k)))
    agents = module.create_team(first_index, second_index, is_red, **opts)
    if role == 'ours':
        defender = agents[1]
        original = defender.choose_action

        def choose_action(game_state):
            start = time.perf_counter()
            action = original(game_state)
            secs = time.perf_counter() - start
            visible = [i for i in defender.get_opponents(game_state)
                       if game_state.get_agent_position(i) is not None]
            probe_store.beliefs.append((defender.index, game_state.data.timeleft,
                                        dict((i, dict(b)) for i, b in defender.belief.items()),
                                        dict(defender.last_seen), secs, visible,
                                        [game_state.get_agent_position(t) for t in defender.get_team(game_state)],
                                        game_state.get_agent_position(defender.index),
                                        list(game_state.get_agent_distances()),
                                        sorted(defender.just_respawned)))
            return action
        defender.choose_action = choose_action
    else:
        for agent in agents:
            original = agent.choose_action

            def choose_action(game_state, agent=agent, original=original):
                probe_store.truth.append((agent.index, game_state.data.timeleft,
                                          game_state.get_agent_position(agent.index)))
                return original(game_state)
            agent.choose_action = choose_action
    return agents
