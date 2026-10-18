# trace_team.py
# -------------
# LOCAL ANALYSIS WRAPPER - never submit this file.
#
# Loaded by capture.py as a "team" (like sentinel_team.py): it loads one of OUR team files, builds
# its agents with the forwarded options, and records for every move WHICH RULE produced the action,
# so that a game can be read move by move next to its replay (eval/trace_game.py; E-022).
#
# How: it wraps our own agents' decision methods on the instances (follow_entry, break_standoff,
# retreat, evade, bfs_action, keep_distance, intercept_cell, shadow_post, next_patrol_point). The
# wrappers pass arguments and results through unchanged and only note which methods were called
# and what they returned. After each move it re-reads the agent's own observation and state to
# name the rule. It never touches an engine object. Methods a version lacks are not wrapped, so it
# works for greedy_v1 / greedy_v2 / greedy_v3 and the lab files.
#
# Usage (normally via eval/trace_game.py):
#   python capture.py -r <repo>/eval/trace_team.py --redOpts team=<team.py>,log=<out.json>[,k=v...]

import importlib.machinery
import importlib.util
import json
import os
import sys

from contest.game import Directions
from contest.util import TimeoutFunctionException

_TRACE_OPTS = ('team', 'log')
_WRAPPED = ('follow_entry', 'break_standoff', 'retreat', 'evade', 'bfs_action',
            'keep_distance', 'intercept_cell', 'shadow_post', 'next_patrol_point')


def create_team(first_index, second_index, is_red, team=None, log=None, **opts):
    if team is None:
        raise ValueError('trace_team needs team=<path to team file>')
    module = _load_team(team, is_red)
    agents = module.create_team(first_index, second_index, is_red, **opts)
    recorder = _Recorder(log, team, is_red, opts)
    for agent in agents:
        _wrap(agent, module, recorder)
    return agents


def _load_team(path, is_red):
    path = os.path.abspath(path)
    name = 'trace_target_%s_%s' % ('red' if is_red else 'blue',
                                   os.path.splitext(os.path.basename(path))[0])
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _cell(c):
    return None if c is None else (int(c[0]), int(c[1]))


def _wrap(agent, module, recorder):
    calls = {'top': [], 'stack': []}

    for name in _WRAPPED:
        if not hasattr(agent, name):
            continue
        original = getattr(agent, name)

        def wrapper(*args, _name=name, _original=original, **kwargs):
            rec = {'m': _name, 'args': args, 'children': []}
            parent = calls['stack'][-1] if calls['stack'] else None
            (parent['children'] if parent is not None else calls['top']).append(rec)
            calls['stack'].append(rec)
            try:
                result = _original(*args, **kwargs)
            finally:
                calls['stack'].pop()
            rec['ret'] = result
            return result
        setattr(agent, name, wrapper)

    original_choose = agent.choose_action
    original_final = getattr(agent, 'final', None)

    def choose_action(game_state):
        calls['top'], calls['stack'] = [], []
        action = original_choose(game_state)
        try:
            entry = _classify(agent, module, game_state, action, calls['top'])
        except TimeoutFunctionException:
            raise
        except Exception as e:  # a trace bug must not change the game: record it and move on
            entry = {'rule': 'trace-error', 'text': '%s: %s' % (type(e).__name__, e)}
        entry.update(index=agent.index, role=type(agent).__name__,
                     ply=1200 - game_state.data.timeleft, move=len(recorder.moves.get(agent.index, [])) + 1,
                     pos=_cell(game_state.get_agent_position(agent.index)), action=action,
                     score=agent.get_score(game_state),
                     carrying=game_state.get_agent_state(agent.index).num_carrying)
        recorder.moves.setdefault(agent.index, []).append(entry)
        return action

    def final(game_state):
        if original_final is not None:
            original_final(game_state)
        recorder.finish(agent.index, agent.get_score(game_state))

    agent.choose_action = choose_action
    agent.final = final


def _const(module, name, default):
    return getattr(module, name, default)


def _go_home_reasons(agent, module, gs):
    """The go-home conditions of GreedyAttacker that hold in this observation (greedy_v1..v3)."""
    pos = gs.get_agent_position(agent.index)
    carrying = gs.get_agent_state(agent.index).num_carrying
    if carrying <= 0:
        return []
    food = agent.get_food(gs).as_list()
    ghosts = agent.dangerous_ghosts(gs)
    returned = sum(gs.get_agent_state(i).num_returned for i in agent.get_team(gs))
    if hasattr(agent, 'return_threshold'):
        threshold = agent.return_threshold(gs, pos)
    else:
        threshold = _const(module, 'RETURN_AT', 5)
    reasons = []
    if carrying >= threshold:
        reasons.append('carrying %d >= %d' % (carrying, threshold))
    if len(food) <= 2:
        reasons.append('<= 2 food left')
    if returned + carrying >= agent.food_to_win:
        reasons.append('this trip wins')
    if gs.data.timeleft // 4 <= agent.map.dist_home[pos] + _const(module, 'TIME_MARGIN', 3):
        reasons.append('out of time')
    near = [g for g in ghosts if agent.map.d(g, pos) <= _const(module, 'THREAT_DIST', 4)]
    if near:
        reasons.append('ghost %d steps away' % min(agent.map.d(g, pos) for g in near))
    return reasons


def _flatten(calls):
    for c in calls:
        yield c
        for d in _flatten(c['children']):
            yield d


def _classify(agent, module, gs, action, top):
    pos = gs.get_agent_position(agent.index)
    names = [c['m'] for c in top]
    everything = [c['m'] for c in _flatten(top)]
    defender = any(n in names for n in ('keep_distance', 'intercept_cell', 'shadow_post',
                                        'next_patrol_point')) or not hasattr(agent, 'food_is_safe')
    if defender:
        return _classify_defender(agent, gs, action, top, names, pos)
    return _classify_attacker(agent, module, gs, action, top, names, everything, pos)


def _classify_attacker(agent, module, gs, action, top, names, everything, pos):
    ghosts = [_cell(g) for g in agent.dangerous_ghosts(gs)]
    home = set(agent.map.home_border) | set(agent.get_capsules(gs))
    detail = {'ghosts': ghosts}
    last = top[-1] if top else None
    if last is not None and last['m'] == 'follow_entry':
        return dict(detail, rule='entry', text='standoff breaker: walking to entry %s' % (_cell(agent.entry),))
    if last is not None and last['m'] == 'break_standoff':
        kids = [c['m'] for c in last['children']]
        if 'follow_entry' in kids:
            return dict(detail, rule='switch-entry',
                        text='standoff breaker: blocked 3 times, switching to entry %s' % (_cell(agent.entry),))
        return dict(detail, rule='capsule', text='standoff breaker: going for a capsule')
    food_bfs = [c for c in top if c['m'] == 'bfs_action' and not set(map(_cell, c['args'][1])) <= home]
    if last is not None and last['m'] == 'bfs_action' and food_bfs and last is food_bfs[-1]:
        steps = last['ret'][1]
        n = len(last['args'][1])
        return dict(detail, rule='eat', safe_food=n,
                    text='eat: nearest safe food, %d steps (%d safe of %d)'
                         % (steps, n, len(agent.get_food(gs).as_list())))
    reasons = _go_home_reasons(agent, module, gs)
    if 'evade' in everything:
        why = 'go home: %s' % ', '.join(reasons) if reasons else 'cut off: no safe food either'
        return dict(detail, rule='evade', reasons=reasons,
                    text='no safe way home (%s): stepping away from the nearest ghost' % why)
    if reasons:
        escape = ' (a capsule also counts as an escape)' if reasons[-1].startswith('ghost') else ''
        return dict(detail, rule='home', reasons=reasons, text='go home%s: %s' % (escape, ', '.join(reasons)))
    if 'break_standoff' in names:
        blocked = sum(agent.blocked) if hasattr(agent, 'blocked') else 0
        return dict(detail, rule='blocked',
                    text='blocked at the border by a ghost, waiting (%d of 3 blocked moves)' % blocked)
    if agent.map.is_ours(pos):
        return dict(detail, rule='no-safe-food', text='no safe food: staying on our side, towards the border')
    return dict(detail, rule='no-safe-food', text='no safe food: heading home')


def _belief_note(agent, raider):
    belief = getattr(agent, 'belief', {}).get(raider) if raider is not None else None
    if not belief:
        return None, None
    cell = max(belief, key=lambda c: (belief[c], c))
    return _cell(cell), round(belief[cell], 2)


def _classify_defender(agent, gs, action, top, names, pos):
    invaders = [_cell(p) for _, p, inv in agent.visible_enemies(gs) if inv]
    raider = getattr(agent, 'raider', None)
    detail = {'invaders': invaders, 'raider': raider}
    if raider is not None and hasattr(agent, 'belief'):
        cell, p = _belief_note(agent, raider)
        detail.update(raider_cell=cell, raider_p=p)
    by_name = dict((c['m'], c) for c in top)
    stop = action == Directions.STOP
    if 'keep_distance' in by_name:
        inv = _cell(by_name['keep_distance']['args'][1])
        return dict(detail, rule='scared', text='scared: keeping 3 steps from invader at %s' % (inv,))
    if 'intercept_cell' in by_name:
        c = by_name['intercept_cell']
        inv, target = _cell(c['args'][1]), _cell(c['ret'])
        if target == inv:
            return dict(detail, rule='chase', text='chase invader at %s' % (inv,))
        if stop:
            return dict(detail, rule='hold', text='hold %s: cuts off invader at %s' % (target, inv))
        return dict(detail, rule='cut-off', text='cut off invader at %s: go to %s' % (inv, target))
    if 'shadow_post' in by_name and by_name['shadow_post']['ret'] is not None:
        post = _cell(by_name['shadow_post']['ret'])
        where = ' (most likely at %s, p=%.2f)' % (detail['raider_cell'], detail['raider_p']) \
            if detail.get('raider_cell') else ''
        return dict(detail, rule='shadow', post=post,
                    text='shadow raider #%s%s: %s %s' % (raider, where, 'waiting at' if stop else 'going to', post))
    if 'next_patrol_point' in by_name:
        point = _cell(by_name['next_patrol_point']['ret'])
        why = ' (no raider seen yet)' if 'shadow_post' in by_name else ''
        return dict(detail, rule='patrol', text='patrol near our food: %s%s' % (point, why))
    if invaders:
        return dict(detail, rule='chase', text='chase invader at %s' % (min(invaders, key=lambda p: agent.map.d(pos, p)),))
    return dict(detail, rule='last-evidence',
                text='go to where food vanished / invader last seen: %s' % (_cell(getattr(agent, 'target', None)),))


class _Recorder:

    def __init__(self, log, team, is_red, opts):
        self.log, self.team, self.is_red = log, team, is_red
        self.opts = dict((k, v) for k, v in opts.items() if k not in _TRACE_OPTS)
        self.moves = {}
        self.final_score = None

    def finish(self, index, score):
        self.final_score = score
        if not self.log:
            return
        out = {'team': self.team, 'red': self.is_red, 'opts': self.opts, 'final_score': score,
               'moves': dict((str(i), m) for i, m in self.moves.items())}
        with open(self.log, 'w') as f:
            json.dump(out, f)
