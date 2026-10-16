# sentinel_team.py
# ----------------
# LOCAL EVALUATION WRAPPER - never submit this file.
#
# Loaded by capture.py as a "team"; it loads the real team file, builds its agents with the
# forwarded options, and wraps register_initial_state / choose_action / final to record:
#   * per-move wall time (perf_counter) and moves over the budget,
#   * integrity violations: walls mutated, shared Configuration objects mutated, global RNG
#     seeded/read, threads started, subprocesses spawned, files opened for writing,
#     observation_function overridden, illegal action returned.
# At the end of the game it writes one JSON file (path given by the `log` option).
#
# Usage (normally via eval/evaluate.py):
#   python capture.py -r <repo>/eval/sentinel_team.py --redOpts team=<team.py>,log=<out.json>[,k=v...]
#
# The tripwires replace a few stdlib functions ONLY while the wrapped agent code runs, so they
# cannot change the game; they only make forbidden behaviour visible in evaluation reports.

import builtins
import importlib.machinery
import importlib.util
import json
import os
import random
import subprocess
import threading
import time

from contest.capture_agents import CaptureAgent

_SENTINEL_OPTS = ('team', 'log', 'budget')


def create_team(first_index, second_index, is_red, team=None, log=None, budget='1.0', **opts):
    if team is None:
        raise ValueError('sentinel_team needs team=<path to team file>')
    module = _load_team(team, is_red)
    agents = module.create_team(first_index, second_index, is_red, **opts)
    recorder = _Recorder(log, team, is_red, float(budget), opts)
    for agent in agents:
        _wrap(agent, recorder)
    return agents


def _load_team(path, is_red):
    path = os.path.abspath(path)
    name = 'sentinel_target_%s_%s' % ('red' if is_red else 'blue',
                                      os.path.splitext(os.path.basename(path))[0])
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class _Tripwires:
    """Context manager: forbidden calls are recorded (and still executed, so behaviour is unchanged)."""

    def __init__(self, recorder, index):
        self.recorder, self.index = recorder, index
        self.saved = []

    def _patch(self, owner, attr, label):
        original = getattr(owner, attr)
        recorder, index = self.recorder, self.index

        def tripwire(*args, **kwargs):
            recorder.violation(index, label)
            return original(*args, **kwargs)

        self.saved.append((owner, attr, original))
        setattr(owner, attr, tripwire)

    def __enter__(self):
        self._patch(random, 'seed', 'global random.seed called')
        self._patch(random, 'setstate', 'global random.setstate called')
        self._patch(random, 'getstate', 'global random.getstate called')
        self._patch(subprocess, 'Popen', 'subprocess spawned')
        self._patch(os, 'system', 'os.system called')
        self._patch(threading.Thread, 'start', 'thread started')
        original_open = builtins.open
        recorder, index = self.recorder, self.index

        def guarded_open(file, mode='r', *args, **kwargs):
            if any(flag in mode for flag in 'wax+'):
                recorder.violation(index, 'file opened for writing: %s' % (file,))
            return original_open(file, mode, *args, **kwargs)

        self.saved.append((builtins, 'open', original_open))
        builtins.open = guarded_open
        return self

    def __exit__(self, *exc):
        for owner, attr, original in reversed(self.saved):
            setattr(owner, attr, original)
        self.saved = []
        return False  # never swallow exceptions (incl. the framework's timeout)


def _config_snapshot(game_state):
    return [(st.configuration, st.configuration.pos, st.configuration.direction)
            for st in game_state.data.agent_states if st.configuration is not None]


def _wrap(agent, recorder):
    index = agent.index
    recorder.expect(index)
    if not isinstance(agent, CaptureAgent):
        recorder.violation(index, 'agent is not a CaptureAgent')
    elif type(agent).observation_function is not CaptureAgent.observation_function:
        recorder.violation(index, 'observation_function overridden')

    original_register = agent.register_initial_state
    original_choose = agent.choose_action
    original_final = getattr(agent, 'final', None)

    def register_initial_state(game_state):
        walls_before = [column[:] for column in game_state.get_walls().data]
        start = time.perf_counter()
        with _Tripwires(recorder, index):
            original_register(game_state)
        recorder.startup(index, time.perf_counter() - start)
        if game_state.get_walls().data != walls_before:
            recorder.violation(index, 'walls mutated')

    def choose_action(game_state):
        # Snapshots are taken per call, so a violation is attributed to the agent that caused it.
        walls_before = [column[:] for column in game_state.get_walls().data]
        configs = _config_snapshot(game_state)
        threads = threading.active_count()
        legal = game_state.get_legal_actions(index)
        start = time.perf_counter()
        with _Tripwires(recorder, index):
            action = original_choose(game_state)
        recorder.move(index, time.perf_counter() - start)
        if game_state.get_walls().data != walls_before:
            recorder.violation(index, 'walls mutated')
        for config, pos, direction in configs:
            if config.pos != pos or config.direction != direction:
                recorder.violation(index, 'shared Configuration mutated')
        if threading.active_count() > threads:
            recorder.violation(index, 'thread still running after move')
        if action not in legal:
            recorder.violation(index, 'illegal action %r' % (action,))
        return action

    def final(game_state):
        if original_final is not None:
            original_final(game_state)
        recorder.finish(index)

    agent.register_initial_state = register_initial_state
    agent.choose_action = choose_action
    agent.final = final


class _Recorder:

    def __init__(self, log, team, is_red, budget, opts):
        self.log, self.team, self.is_red, self.budget = log, team, is_red, budget
        self.opts = {k: v for k, v in opts.items() if k not in _SENTINEL_OPTS}
        self.agents = {}
        self.finished = set()

    def expect(self, index):
        self.agents[index] = {'startup_s': None, 'times': [], 'violations': []}

    def startup(self, index, seconds):
        self.agents[index]['startup_s'] = seconds

    def move(self, index, seconds):
        self.agents[index]['times'].append(seconds)

    def violation(self, index, label):
        violations = self.agents[index]['violations']
        if label not in violations and len(violations) < 20:
            violations.append(label)

    def finish(self, index):
        self.finished.add(index)
        if self.finished >= set(self.agents) and self.log:
            self._write()

    def _write(self):
        report = {'team': self.team, 'is_red': self.is_red, 'budget_s': self.budget,
                  'opts': self.opts, 'agents': {}}
        for index, data in self.agents.items():
            times = sorted(data['times'])
            n = len(times)
            report['agents'][str(index)] = {
                'moves': n,
                'startup_s': data['startup_s'],
                'max_s': times[-1] if n else None,
                'p95_s': times[min(n - 1, int(0.95 * n))] if n else None,
                'mean_s': sum(times) / n if n else None,
                'over_budget': sum(1 for t in times if t > self.budget),
                'violations': data['violations'],
            }
        directory = os.path.dirname(os.path.abspath(self.log))
        os.makedirs(directory, exist_ok=True)
        with open(self.log, 'w') as f:
            json.dump(report, f, indent=1)
