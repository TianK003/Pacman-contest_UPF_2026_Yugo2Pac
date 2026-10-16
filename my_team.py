# my_team.py
# ----------
# SUBMISSION FILE (the tournament loads this). Promoted 2026-10-16 from teams/greedy_v1.py
# (behaviour identical; only this header differs) - see docs/experiments.md E-002/E-003.
# Never edit this file directly: improve a new teams/<name>_vN.py, evaluate it, then copy it here.
#
# First non-trivial team (v1): greedy food collection with ghost evasion, plus a patrolling
# defender. Self-contained (stdlib + contest framework only) so it can be frozen as a league
# opponent. Do not edit after it has been benchmarked; copy to greedy_v2.py instead.
#
# Rules this file follows (docs/rules.md): public API only, no mutation of observation objects,
# own RNG instance, no reading of hidden opponents' AgentState fields (opponent ghost/pacman
# status is derived from its visible position; scared state is derived from capsule events).
#
# Variants (select via create_team kwargs; tournament uses the defaults):
#   first='GreedyAttacker'  | 'DeadEndAttacker' | 'PatrolDefender'
#   second='PatrolDefender' | 'GreedyAttacker'  | 'DeadEndAttacker'

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


def create_team(first_index, second_index, is_red,
                first='GreedyAttacker', second='PatrolDefender', num_training=0):
    roles = {
        'GreedyAttacker': GreedyAttacker,
        'DeadEndAttacker': DeadEndAttacker,
        'PatrolDefender': PatrolDefender,
    }
    return [roles[first](first_index), roles[second](second_index)]


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
            carrying >= RETURN_AT
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
