# sparring_v1.py
# --------------
# League opponents (never submitted): specialists that stress the weaknesses found in E-005.
# Self-contained copy of the greedy_v1 machinery (MapInfo, V1Agent, GreedyAttacker,
# PatrolDefender; identical behaviour) plus three new opponent styles:
#   BorderCamper   (P-02) a defender that camps on its border where the enemy would cross
#   CapsuleRusher  (P-03) an attacker that eats the capsule first, then harvests while scared
#   ReflexAttacker / ReflexDefender (P-01) baseline-style reflex agents with a return-at-5 rule
#                  and a ghost-distance penalty ("baseline_plus")
# Do not edit after it has been benchmarked; copy to sparring_v2.py instead.
#
# Teams (create_team kwargs; league.json): camper = GreedyAttacker + BorderCamper,
# camper2 = 2x BorderCamper, rusher = CapsuleRusher + PatrolDefender,
# baseline_plus = ReflexAttacker + ReflexDefender.

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
MEMORY_PLIES = 40      # how long a camper trusts an enemy's last seen position (10 own moves)
RUSH_RETURN_AT = 12    # capsule rusher's return threshold while the enemy is scared
HUNT_DIST = 4          # capsule rusher chases scared ghosts this close


def create_team(first_index, second_index, is_red,
                first='GreedyAttacker', second='BorderCamper', num_training=0):
    roles = {
        'GreedyAttacker': GreedyAttacker,
        'DeadEndAttacker': DeadEndAttacker,
        'PatrolDefender': PatrolDefender,
        'BorderCamper': BorderCamper,
        'CapsuleRusher': CapsuleRusher,
        'ReflexAttacker': ReflexAttacker,
        'ReflexDefender': ReflexDefender,
    }
    agents = [roles[first](first_index), roles[second](second_index)]
    campers = [a for a in agents if isinstance(a, BorderCamper)]
    for rank, camper in enumerate(campers):
        camper.rank = rank
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


###################
# Sparring agents #
###################

class BorderCamper(PatrolDefender):
    """Stays on our side, standing on the border cell nearest to where the enemy it guards would
    cross (that enemy = seen now or within MEMORY_PLIES). Chases visible invaders, checks spots
    where our food vanished, and falls back to the PatrolDefender patrol when it knows nothing."""

    rank = 0  # 0 guards the enemy closest to our border, 1 the next one (set by create_team)

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
            nearest = min(invaders, key=lambda p: self.map.d(pos, p))
            if scared:
                return self.keep_distance(game_state, nearest)
            self.target = nearest
        if self.target == pos:
            self.target = None

        target = self.target if self.target is not None else self.guard_cell(game_state, pos)
        if target == pos:
            return Directions.STOP
        action, _ = self.bfs_action(game_state, [target], lambda cell, steps: self.map.is_ours(cell))
        if action is not None:
            return action
        self.target = None
        return Directions.STOP

    def guard_cell(self, game_state, pos):
        now = game_state.data.timeleft
        estimates = []
        for i in self.get_opponents(game_state):
            p = game_state.get_agent_position(i)
            if p is None and i in self.last_seen and self.last_seen[i][1] - now <= MEMORY_PLIES:
                p = self.last_seen[i][0]
            if p is not None and not self.map.is_ours(p):
                estimates.append(p)
        if not estimates or not self.map.home_border:
            return self.next_patrol_point(game_state, pos)
        estimates.sort(key=lambda p: self.map.dist_home[p])
        enemy = estimates[min(self.rank, len(estimates) - 1)]
        return min(self.map.home_border, key=lambda b: (self.map.d(enemy, b), self.map.d(pos, b)))


class CapsuleRusher(GreedyAttacker):
    """Goes for an enemy capsule first (when carrying nothing and no scared window is running).
    While the enemy is scared it carries up to RUSH_RETURN_AT food and hunts scared ghosts within
    HUNT_DIST; otherwise it plays exactly like GreedyAttacker."""

    def window_left(self, game_state):
        """Enemy moves left in the current scared window, minus the safety margin (<= 0: none)."""
        if self.scared_since is None:
            return 0
        enemy_moves = (self.scared_since - game_state.data.timeleft) // 4 + 1
        return SCARED_TIME - enemy_moves - SCARED_MARGIN

    def return_at(self, game_state):
        return RUSH_RETURN_AT if self.window_left(game_state) > 0 else RETURN_AT

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        pos = game_state.get_agent_position(self.index)
        ghosts = self.dangerous_ghosts(game_state)

        def safe(cell, steps):
            if self.map.is_ours(cell):
                return True
            return all(self.map.d(g, cell) > steps for g in ghosts)

        window = self.window_left(game_state)
        if window > 0:
            prey = [p for i, p, invader in self.visible_enemies(game_state)
                    if not invader and self.enemy_scared(i, game_state)
                    and self.map.d(pos, p) <= min(HUNT_DIST, window - 1)]
            if prey:
                action, _ = self.bfs_action(game_state, prey, safe)
                if action is not None:
                    return action
        elif game_state.get_agent_state(self.index).num_carrying == 0:
            capsules = self.get_capsules(game_state)
            if capsules:
                action, _ = self.bfs_action(game_state, capsules, safe)
                if action is not None:
                    return action
        return super().choose_action(game_state)


#######################################
# Baseline-style reflex agents (P-01) #
#######################################

class ReflexAgent(CaptureAgent):
    """One-step lookahead over legal actions, scoring each successor with a weighted feature sum
    (the structure of the framework's baseline), with our own RNG for tie breaks."""

    def __init__(self, index, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.rng = random.Random(4243 + index)
        self.start = None
        self.home_cells = []

    def register_initial_state(self, game_state):
        CaptureAgent.register_initial_state(self, game_state)
        self.start = game_state.get_agent_position(self.index)
        walls = game_state.get_walls()
        home_x = walls.width // 2 - 1 if self.red else walls.width // 2
        self.home_cells = [(home_x, y) for y in range(walls.height) if not walls[home_x][y]]

    def choose_action(self, game_state):
        actions = game_state.get_legal_actions(self.index)
        values = [self.evaluate(game_state, a) for a in actions]
        best = max(values)
        return self.rng.choice([a for a, v in zip(actions, values) if v == best])

    def evaluate(self, game_state, action):
        features = self.get_features(game_state, action)
        weights = self.get_weights()
        return sum(value * weights.get(name, 0) for name, value in features.items())


class ReflexAttacker(ReflexAgent):
    """Baseline offence (eat, approach the nearest food) plus: go home when carrying >= RETURN_AT
    or <= 2 food are left, and keep away from visible enemy ghosts while a Pacman."""

    def get_features(self, game_state, action):
        features = {}
        successor = game_state.generate_successor(self.index, action)
        me = successor.get_agent_state(self.index)
        my_pos = me.get_position()
        food = self.get_food(successor).as_list()
        features['successor_score'] = -len(food)
        if me.num_carrying >= RETURN_AT or (len(food) <= 2 and me.num_carrying > 0):
            features['home_distance'] = min(self.get_maze_distance(my_pos, h) for h in self.home_cells)
        elif food:
            features['distance_to_food'] = min(self.get_maze_distance(my_pos, f) for f in food)
        old_pos = game_state.get_agent_position(self.index)
        died = my_pos == self.start and self.get_maze_distance(old_pos, self.start) > 1
        if died:
            features['danger'] = 10
        elif me.is_pacman:
            ghosts = [game_state.get_agent_position(i) for i in self.get_opponents(game_state)]
            ghosts = [g for g in ghosts if g is not None and not self.is_our_side(game_state, g)]
            if ghosts:
                d = min(self.get_maze_distance(my_pos, g) for g in ghosts)
                if d <= 3:
                    features['danger'] = 4 - d
        return features

    def is_our_side(self, game_state, pos):
        return (pos[0] < game_state.get_walls().width // 2) == self.red

    def get_weights(self):
        return {'successor_score': 100, 'distance_to_food': -1, 'home_distance': -2, 'danger': -100}


class ReflexDefender(ReflexAgent):
    """Baseline defence: stay home, minimise the number of visible invaders and the distance to
    the nearest one, avoid stopping and reversing."""

    def get_features(self, game_state, action):
        features = {}
        successor = game_state.generate_successor(self.index, action)
        me = successor.get_agent_state(self.index)
        my_pos = me.get_position()
        features['on_defense'] = 0 if me.is_pacman else 1
        width = game_state.get_walls().width
        invaders = [successor.get_agent_position(i) for i in self.get_opponents(successor)]
        invaders = [p for p in invaders if p is not None and (p[0] < width // 2) == self.red]
        features['num_invaders'] = len(invaders)
        if invaders:
            features['invader_distance'] = min(self.get_maze_distance(my_pos, p) for p in invaders)
        if action == Directions.STOP:
            features['stop'] = 1
        direction = game_state.get_agent_state(self.index).configuration.direction
        if action == Directions.REVERSE[direction]:
            features['reverse'] = 1
        return features

    def get_weights(self):
        return {'num_invaders': -1000, 'on_defense': 100, 'invader_distance': -10, 'stop': -100,
                'reverse': -2}
