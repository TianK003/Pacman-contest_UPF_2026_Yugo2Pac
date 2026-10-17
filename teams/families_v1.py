# families_v1.py
# --------------
# Two alternative agent families for the attacker (F1, F2 in docs/experiments.md E-008), each
# paired with greedy_v1's PatrolDefender so that only the attacker's decision method differs:
#   FeatureAttacker  F1  weighted-feature evaluation (M-02): scores each move by a weighted sum of
#                        features of the cell it leads to
#   FieldAttacker    F2  potential field / influence map: food and home pull, ghosts push, and the
#                        agent steps to the best neighbouring cell
# Both keep greedy's forced returns (out of time, winning trip, <= 2 food left) and its perception.
# Weights can be overridden for offline tuning with create_team kwargs w_<name>=<value>.
# Self-contained copy of the greedy_v1 machinery (identical MapInfo, V1Agent, GreedyAttacker,
# PatrolDefender). Do not edit after it has been benchmarked; copy to families_v2.py instead.

import random
from collections import deque

from contest.capture_agents import CaptureAgent
from contest.game import Actions, Directions

INF = 10 ** 6
RETURN_AT = 5          # carried food that triggers a return home
THREAT_DIST = 4        # maze distance at which a visible ghost makes a carrier go home
SCARED_TIME = 40       # framework constant (capture.py); enemy moves a capsule lasts
SCARED_MARGIN = 3      # treat enemies as dangerous this many of their moves before the timer ends
TIME_MARGIN = 3        # extra own moves kept in reserve when racing the clock home
LOOP_MEMORY = 8         # recent own positions remembered for the anti-oscillation term (H-S10)

FEATURE_WEIGHTS = {
    'eat': 10.0,           # the move eats a food dot
    'food_dist': -1.0,     # maze distance to the nearest food
    'carry_home': -0.25,   # food carried x distance home
    'ghost': -10.0,        # max(0, 5 - distance to the nearest dangerous ghost), enemy side only
    'caught': -1000.0,     # a dangerous ghost is within 1 of the cell
    'trapped': -100.0,     # the cell is in a dead end whose exit a ghost reaches before we get out
    'capsule_dist': -1.0,  # distance to the nearest enemy capsule, only while threatened
    'stop': -10.0,
    'reverse': -1.0,
    'loop': -2.0,          # times the cell was visited in the last LOOP_MEMORY moves
}

FIELD_WEIGHTS = {
    'food': 1.0,           # pull of one food dot at distance 0
    'food_decay': 0.75,    # pull factor per step of maze distance
    'pocket': 0.5,         # pull of food at dead-end depth k is divided by (1 + pocket * k) while a ghost is seen
    'home': 0.6,           # pull of home per food carried
    'home_decay': 0.9,
    'ghost': 8.0,          # push of a dangerous ghost at distance 1
    'ghost_decay': 0.5,
    'caught': 1000.0,      # penalty for a cell within 1 of a dangerous ghost
    'capsule': 3.0,        # pull of a capsule while threatened
    'stop': 0.5,
    'loop': 0.3,
}


def create_team(first_index, second_index, is_red,
                first='FeatureAttacker', second='PatrolDefender', num_training=0, **weights):
    roles = {
        'GreedyAttacker': GreedyAttacker,
        'PatrolDefender': PatrolDefender,
        'FeatureAttacker': FeatureAttacker,
        'FieldAttacker': FieldAttacker,
    }
    overrides = {}
    for key, value in weights.items():
        if not key.startswith('w_'):
            raise ValueError('unknown option %s' % key)
        overrides[key[2:]] = float(value)
    agents = [roles[first](first_index), roles[second](second_index)]
    for agent in agents:
        if isinstance(agent, EvalAttacker):
            agent.set_weights(overrides)
    return agents


##############
# Map helper #
##############

class MapInfo:
    """Static analysis of the layout, computed once per game from the (read-only) walls."""

    def __init__(self, walls, is_red):
        self.width, self.height = walls.width, walls.height
        self.cells = [(x, y) for x in range(self.width) for y in range(self.height) if not walls[x][y]]
        cell_set = set(self.cells)
        self.nbrs = {}
        for x, y in self.cells:
            self.nbrs[(x, y)] = [n for n in ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)) if n in cell_set]
        self.is_red = is_red
        self.mid = self.width // 2
        self.dist = self._all_pairs()

        home_x = self.mid - 1 if is_red else self.mid
        enemy_x = self.mid if is_red else self.mid - 1
        self.home_border = [(home_x, y) for y in range(self.height)
                            if (home_x, y) in cell_set and (enemy_x, y) in cell_set]
        self.dist_home = {c: min((self.dist[c].get(b, INF) for b in self.home_border), default=INF)
                          for c in self.cells}
        self.depth, self.entrance = self._dead_ends()

    def is_ours(self, pos):
        return (pos[0] < self.mid) == self.is_red

    def d(self, a, b):
        return self.dist[a].get(b, INF)

    def _all_pairs(self):
        dist = {}
        for s in self.cells:
            ds = {s: 0}
            queue = deque([s])
            while queue:
                c = queue.popleft()
                nd = ds[c] + 1
                for n in self.nbrs[c]:
                    if n not in ds:
                        ds[n] = nd
                        queue.append(n)
            dist[s] = ds
        return dist

    def _dead_ends(self):
        """Leaf pruning: cells removed by repeatedly deleting degree-1 cells lie in dead-end trees.
        depth = steps to the remaining core, entrance = the core cell the tree hangs off (H-M02)."""
        degree = {c: len(self.nbrs[c]) for c in self.cells}
        removed = set()
        queue = deque(c for c in self.cells if degree[c] <= 1)
        while queue:
            c = queue.popleft()
            if c in removed:
                continue
            removed.add(c)
            for n in self.nbrs[c]:
                if n not in removed:
                    degree[n] -= 1
                    if degree[n] == 1:
                        queue.append(n)
        core = [c for c in self.cells if c not in removed]
        depth = {c: 0 for c in core}
        entrance = {c: c for c in core}
        if not core:  # tree-shaped map: no notion of dead end
            return {c: 0 for c in self.cells}, {c: c for c in self.cells}
        queue = deque(core)
        while queue:
            c = queue.popleft()
            for n in self.nbrs[c]:
                if n not in depth:
                    depth[n] = depth[c] + 1
                    entrance[n] = entrance[c]
                    queue.append(n)
        for c in self.cells:  # unreachable pockets (should not exist) count as core
            depth.setdefault(c, 0)
            entrance.setdefault(c, c)
        return depth, entrance


##############
# Base agent #
##############

class V1Agent(CaptureAgent):

    def __init__(self, index, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.rng = random.Random(7919 + index)  # own RNG; never seed the global one (T-02)
        self.map = None
        self.food_to_win = None
        self.enemy_capsules = set()
        self.scared_since = None       # timeleft value at which we last saw an enemy capsule vanish
        self.unscared = set()          # enemies seen respawning since that capsule
        self.last_seen = {}            # enemy index -> (pos, timeleft)

    def register_initial_state(self, game_state):
        CaptureAgent.register_initial_state(self, game_state)
        self.map = MapInfo(game_state.get_walls(), self.red)
        self.food_to_win = len(self.get_food(game_state).as_list()) - 2
        self.enemy_capsules = set(self.get_capsules(game_state))
        self.scared_since = None
        self.unscared = set()
        self.last_seen = {}

    # --- perception (derived only from public observation data) ---

    def update_enemy_tracking(self, game_state):
        now = game_state.data.timeleft
        capsules = set(self.get_capsules(game_state))
        if self.enemy_capsules - capsules:  # only our pacmen can eat the capsules on the enemy side
            prev = self.get_previous_observation()
            self.scared_since = prev.data.timeleft if prev is not None else now
            self.unscared = set()
        self.enemy_capsules = capsules
        prev = self.get_previous_observation()
        prev_time = prev.data.timeleft if prev is not None else None
        team_prev = [prev.get_agent_position(t) for t in self.get_team(prev)] if prev is not None else []
        for i in self.get_opponents(game_state):
            pos = game_state.get_agent_position(i)
            if pos is None:
                # Seen within Manhattan 2 of one of us last turn and gone now: since then each agent
                # moved at most once, so it would still be within sight (<= 5) unless it was eaten.
                if i in self.last_seen and self.last_seen[i][1] == prev_time:
                    last_pos = self.last_seen[i][0]
                    if any(abs(last_pos[0] - t[0]) + abs(last_pos[1] - t[1]) <= 2 for t in team_prev if t):
                        self.unscared.add(i)
                        del self.last_seen[i]
                continue
            if i in self.last_seen:
                last_pos, last_time = self.last_seen[i]
                max_moves = (last_time - now) // 4 + 1
                if self.map.d(last_pos, pos) > max_moves + 1:  # teleported => respawned => not scared
                    self.unscared.add(i)
            self.last_seen[i] = (pos, now)

    def enemy_scared(self, i, game_state):
        if self.scared_since is None or i in self.unscared:
            return False
        enemy_moves = (self.scared_since - game_state.data.timeleft) // 4 + 1
        return SCARED_TIME - enemy_moves > SCARED_MARGIN

    def visible_enemies(self, game_state):
        """[(index, pos, is_invader)] for opponents we can see."""
        out = []
        for i in self.get_opponents(game_state):
            pos = game_state.get_agent_position(i)
            if pos is not None:
                out.append((i, pos, self.map.is_ours(pos)))
        return out

    def dangerous_ghosts(self, game_state):
        return [pos for i, pos, invader in self.visible_enemies(game_state)
                if not invader and not self.enemy_scared(i, game_state)]

    # --- movement ---

    def bfs_action(self, game_state, targets, allowed):
        """First action of a shortest path to the nearest target, expanding only cells for which
        allowed(cell, steps) is true. Returns (action, steps) or (None, None)."""
        start = game_state.get_agent_position(self.index)
        targets = set(targets)
        first = {}
        queue = deque()
        for action in game_state.get_legal_actions(self.index):
            if action == Directions.STOP:
                continue
            dx, dy = Actions.direction_to_vector(action)
            nxt = (int(start[0] + dx), int(start[1] + dy))
            if nxt not in first and allowed(nxt, 1):
                first[nxt] = action
                queue.append((nxt, 1))
        while queue:
            cell, steps = queue.popleft()
            if cell in targets:
                return first[cell], steps
            for n in self.map.nbrs[cell]:
                if n not in first and n != start and allowed(n, steps + 1):
                    first[n] = first[cell]
                    queue.append((n, steps + 1))
        return None, None

    def successors(self, game_state):
        pos = game_state.get_agent_position(self.index)
        out = []
        for action in game_state.get_legal_actions(self.index):
            dx, dy = Actions.direction_to_vector(action)
            out.append((action, (int(pos[0] + dx), int(pos[1] + dy))))
        return out


#############
# Attackers #
#############

class GreedyAttacker(V1Agent):
    """Eats the nearest food it can reach before any visible ghost (race-safe BFS, H-S03),
    goes home when carrying enough / threatened / out of time (H-S04, H-S05)."""

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        pos = game_state.get_agent_position(self.index)
        me = game_state.get_agent_state(self.index)
        carrying = me.num_carrying
        food = self.get_food(game_state).as_list()
        ghosts = self.dangerous_ghosts(game_state)
        returned = sum(game_state.get_agent_state(i).num_returned for i in self.get_team(game_state))
        my_moves_left = game_state.data.timeleft // 4
        threatened = any(self.map.d(g, pos) <= THREAT_DIST for g in ghosts)

        go_home = carrying > 0 and (
            carrying >= self.return_at(game_state)
            or len(food) <= 2
            or returned + carrying >= self.food_to_win
            or my_moves_left <= self.map.dist_home[pos] + TIME_MARGIN
            or threatened)

        def safe(cell, steps):
            if self.map.is_ours(cell):
                return True
            return all(self.map.d(g, cell) > steps for g in ghosts)

        if not go_home:
            targets = [f for f in food if self.food_is_safe(f, pos, ghosts)]
            if targets:
                action, _ = self.bfs_action(game_state, targets, safe)
                if action is not None:
                    return action
        home_targets = list(self.map.home_border)
        if threatened:
            home_targets += self.get_capsules(game_state)  # a capsule is also an escape
        action, _ = self.bfs_action(game_state, home_targets, safe)
        if action is not None:
            return action
        return self.evade(game_state, ghosts)

    def return_at(self, game_state):
        return RETURN_AT

    def food_is_safe(self, food, pos, ghosts):
        my_d = self.map.d(pos, food)
        return all(self.map.d(g, food) > my_d for g in ghosts)

    def evade(self, game_state, ghosts):
        """No safe path: maximise distance to the nearest ghost, then minimise distance home."""
        def key(item):
            action, cell = item
            gd = min((self.map.d(g, cell) for g in ghosts), default=INF) if not self.map.is_ours(cell) else INF
            return (gd, -self.map.dist_home[cell], action != Directions.STOP, self.rng.random())
        return max(self.successors(game_state), key=key)[0]


class DeadEndAttacker(GreedyAttacker):
    """GreedyAttacker that only enters a dead end if it can eat and get back out to the
    dead end's entrance before any visible ghost reaches that entrance (H-M02 + H-S03)."""

    def food_is_safe(self, food, pos, ghosts):
        if not super().food_is_safe(food, pos, ghosts):
            return False
        depth = self.map.depth[food]
        if depth == 0 or not ghosts:
            return True
        exit_cell = self.map.entrance[food]
        my_exit_time = self.map.d(pos, food) + depth + 1
        return all(self.map.d(g, exit_cell) > my_exit_time for g in ghosts)


############
# Defender #
############

class PatrolDefender(V1Agent):
    """Stays on our side. Chases visible invaders (keeps its distance while scared), otherwise
    goes to where our food just disappeared (H-S02), otherwise patrols border cells near our food."""

    def register_initial_state(self, game_state):
        super().register_initial_state(game_state)
        self.target = None
        self.patrol = []
        self.patrol_i = 0
        self.patrol_food_count = None

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        pos = game_state.get_agent_position(self.index)
        scared = game_state.get_agent_state(self.index).scared_timer > 0  # our own state
        invaders = [p for _, p, invader in self.visible_enemies(game_state) if invader]

        prev = self.get_previous_observation()
        if prev is not None:
            eaten = (set(self.get_food_you_are_defending(prev).as_list())
                     - set(self.get_food_you_are_defending(game_state).as_list()))
            if eaten:
                self.target = min(eaten, key=lambda f: self.map.d(pos, f))
        if invaders:
            self.target = min(invaders, key=lambda p: self.map.d(pos, p))
        if self.target == pos:
            self.target = None

        if invaders and scared:
            nearest = min(invaders, key=lambda p: self.map.d(pos, p))
            return self.keep_distance(game_state, nearest)

        target = self.target if self.target is not None else self.next_patrol_point(game_state, pos)
        if target == pos:
            return Directions.STOP
        action, _ = self.bfs_action(game_state, [target], lambda cell, steps: self.map.is_ours(cell))
        if action is not None:
            return action
        self.target = None
        return Directions.STOP

    def keep_distance(self, game_state, invader, wanted=3):
        def key(item):
            action, cell = item
            if not self.map.is_ours(cell):
                return (-INF, 0)
            return (-abs(self.map.d(cell, invader) - wanted), self.rng.random())
        return max(self.successors(game_state), key=key)[0]

    def next_patrol_point(self, game_state, pos):
        food = self.get_food_you_are_defending(game_state).as_list()
        if self.patrol_food_count != len(food) or not self.patrol:
            self.patrol_food_count = len(food)
            border = self.map.home_border
            if not food or not border:
                return pos
            centre = min(border, key=lambda b: sum(self.map.d(b, f) for f in food))
            self.patrol = sorted(border, key=lambda b: self.map.d(b, centre))[:3]
            self.patrol_i = 0
        if pos == self.patrol[self.patrol_i % len(self.patrol)]:
            self.patrol_i += 1
        return self.patrol[self.patrol_i % len(self.patrol)]


##############################
# Evaluation-based attackers #
##############################

class EvalAttacker(V1Agent):
    """Shared frame for F1/F2: greedy's perception and forced returns; otherwise every legal move
    is scored by score_move() and the best one is played (ties broken by our own RNG)."""

    DEFAULT_WEIGHTS = {}

    def __init__(self, index, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.w = dict(self.DEFAULT_WEIGHTS)
        self.recent = deque(maxlen=LOOP_MEMORY)

    def set_weights(self, overrides):
        for key, value in overrides.items():
            if key not in self.w:
                raise ValueError('unknown weight %s for %s' % (key, type(self).__name__))
            self.w[key] = value

    def register_initial_state(self, game_state):
        super().register_initial_state(game_state)
        self.recent = deque(maxlen=LOOP_MEMORY)

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        pos = game_state.get_agent_position(self.index)
        me = game_state.get_agent_state(self.index)
        food = self.get_food(game_state).as_list()
        ghosts = self.dangerous_ghosts(game_state)
        returned = sum(game_state.get_agent_state(i).num_returned for i in self.get_team(game_state))
        must_home = me.num_carrying > 0 and (
            len(food) <= 2
            or returned + me.num_carrying >= self.food_to_win
            or game_state.data.timeleft // 4 <= self.map.dist_home[pos] + TIME_MARGIN)
        action = None
        if must_home:
            action = self.go_home(game_state, ghosts)
        if action is None:
            ctx = {
                'pos': pos, 'carrying': me.num_carrying, 'food': food, 'food_set': set(food),
                'ghosts': ghosts, 'capsules': self.get_capsules(game_state),
                'threatened': any(self.map.d(g, pos) <= THREAT_DIST for g in ghosts),
                'reverse': Directions.REVERSE[me.configuration.direction],
            }
            best, best_value = [], None
            for action_, cell in self.successors(game_state):
                value = self.score_move(ctx, action_, cell)
                if best_value is None or value > best_value:
                    best, best_value = [action_], value
                elif value == best_value:
                    best.append(action_)
            action = self.rng.choice(best)
        self.recent.append(pos)
        return action

    def go_home(self, game_state, ghosts):
        def safe(cell, steps):
            if self.map.is_ours(cell):
                return True
            return all(self.map.d(g, cell) > steps for g in ghosts)
        action, _ = self.bfs_action(game_state, self.map.home_border, safe)
        return action

    def score_move(self, ctx, action, cell):
        raise NotImplementedError


class FeatureAttacker(EvalAttacker):
    """F1 (M-02): value = sum of weight x feature of the cell the move leads to (FEATURE_WEIGHTS)."""

    DEFAULT_WEIGHTS = FEATURE_WEIGHTS

    def features(self, ctx, action, cell):
        f = {}
        m = self.map
        f['eat'] = 1 if cell in ctx['food_set'] else 0
        f['food_dist'] = min((m.d(cell, x) for x in ctx['food']), default=0)
        f['carry_home'] = ctx['carrying'] * m.dist_home[cell]
        ghosts = ctx['ghosts']
        if ghosts and not m.is_ours(cell):
            gd = min(m.d(g, cell) for g in ghosts)
            f['ghost'] = max(0, 5 - gd)
            f['caught'] = 1 if gd <= 1 else 0
            if m.depth[cell] > 0:
                exit_cell = m.entrance[cell]
                f['trapped'] = 1 if min(m.d(g, exit_cell) for g in ghosts) <= m.depth[cell] + 1 else 0
            if ctx['threatened'] and ctx['capsules']:
                f['capsule_dist'] = min(m.d(cell, c) for c in ctx['capsules'])
        f['stop'] = 1 if action == Directions.STOP else 0
        f['reverse'] = 1 if action == ctx['reverse'] and action != Directions.STOP else 0
        f['loop'] = sum(1 for p in self.recent if p == cell)
        return f

    def score_move(self, ctx, action, cell):
        return sum(self.w[k] * v for k, v in self.features(ctx, action, cell).items())


class FieldAttacker(EvalAttacker):
    """F2: potential field. Every food dot pulls with food * food_decay^distance (weaker deep in a
    dead end while a ghost is seen), home pulls with carried * home * home_decay^distance, visible
    dangerous ghosts push with ghost * ghost_decay^(distance-1) on the enemy side, capsules pull
    while threatened; small penalties for stopping and revisiting cells (FIELD_WEIGHTS)."""

    DEFAULT_WEIGHTS = FIELD_WEIGHTS

    def score_move(self, ctx, action, cell):
        w, m = self.w, self.map
        ghosts = ctx['ghosts']
        value = 0.0
        for x in ctx['food']:
            pull = w['food'] * w['food_decay'] ** m.d(cell, x)
            if ghosts and m.depth[x] > 0:
                pull /= 1.0 + w['pocket'] * m.depth[x]
            value += pull
        value += ctx['carrying'] * w['home'] * w['home_decay'] ** m.dist_home[cell]
        if ghosts and not m.is_ours(cell):
            for g in ghosts:
                gd = m.d(g, cell)
                value -= w['ghost'] * w['ghost_decay'] ** max(0, gd - 1)
                if gd <= 1:
                    value -= w['caught']
        if ctx['threatened']:
            for c in ctx['capsules']:
                value += w['capsule'] * w['food_decay'] ** m.d(cell, c)
        if action == Directions.STOP:
            value -= w['stop']
        value -= w['loop'] * sum(1 for p in self.recent if p == cell)
        return value
