# greedy_lab_v3.py
# ----------------
# Lab file for the successors of greedy_v2 (docs/experiments.md E-019): a copy of
# teams/greedy_v2.py plus a belief tracker for the defender and two switches that use it, all OFF
# by default, so that with no options it plays exactly like greedy_v2. Never submitted as is; a
# winner is frozen as teams/greedy_v3.py with its switches as defaults. Do not edit after it has
# been benchmarked.
#
# Switches (create_team kwargs):
#   breaker='1'    C2 standoff breaker (H-S12, H-M06): when a ghost blocks the border, take a
#                     capsule we reach first, or walk (on our side) to the entry farthest from it
#   intercept='1'  C4 the defender heads for the invader's way home / the exit of its dead end
#                     instead of chasing it (H-S07)
#   return_at='8'  C5 carried food that triggers a return home (greedy_v1: 5)
#   roles='0', tracker='0', adaptive='0'   screened in E-007/E-010, not adopted
#   hunt='0'       P-22 (H-S01 + H-S07): the defender keeps an exact belief over each enemy's cell
#                     (M-04, its own sonar readings only) and treats a hidden enemy that is
#                     probably on our side as an invader at its most likely cell
#   shadow='0'     P-23 (H-S01 + H-S07): with no invader evidence, the defender waits at the
#                     border entry across from where the enemy nearest our side probably is,
#                     instead of patrolling near our food
#
# Rules this file follows (docs/rules.md): public API only, no mutation of observation objects,
# own RNG instance, no reading of hidden opponents' AgentState fields (opponent ghost/pacman
# status is derived from its visible position; scared state is derived from capsule events).

import random
from collections import deque

from contest.capture_agents import CaptureAgent
from contest.game import Actions, Directions

INF = 10 ** 6
RETURN_AT = 5          # greedy_v1's return threshold (Config default); greedy_v2 plays with 8
THREAT_DIST = 4        # maze distance at which a visible ghost makes a carrier go home
SCARED_TIME = 40       # framework constant (capture.py); enemy moves a capsule lasts
SCARED_MARGIN = 3      # treat enemies as dangerous this many of their moves before the timer ends
TIME_MARGIN = 3        # extra own moves kept in reserve when racing the clock home

EVIDENCE_PLIES = 40    # C1: an invader counts as present this long after its last evidence
QUIET_MOVES = 25       # C1: own moves without invader evidence before the defender attacks too
ENDGAME_MOVES = 40     # C1: in the last own moves, ahead -> both defend, behind -> both attack
STANDOFF_MOVES = 3     # C2: blocked moves (within the last STANDOFF_WINDOW) before changing plan
STANDOFF_WINDOW = 12   # C2: own moves remembered for counting blocked moves
SIGHT = 5              # C3: framework sight range (capture.py SIGHT_RANGE, Manhattan)
SONAR_NOISE = 6        # C3: framework sonar = Manhattan + uniform integer noise in [-6, 6]
TRACK_MAX_CELLS = 20   # C3: a hidden ghost is a threat while its possible set is at most this big
ADAPT_LOW = 3          # C5: threshold while a defender was seen in the last ADAPT_RECENT moves
ADAPT_HIGH = 10        # C5: threshold after ADAPT_QUIET own moves without seeing a defender
ADAPT_RECENT = 5
ADAPT_QUIET = 15
ADAPT_BANK_DIST = 2    # C5: bank >= 2 carried food when home is this close
HUNT_MASS = 0.5        # P-22: belief mass on our side above which a hidden enemy counts as an invader
STAY_WEIGHT = 0.2      # P-22/23: motion model, weight of staying put against 1 per neighbour
                       # (no cell is ever dropped for a small probability: an enemy walking straight
                       # has a tiny random-walk probability, and dropping it lost the truth, E-019)


def _flag(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    """Experiment switches; one read-only object per team."""

    def __init__(self, roles='0', breaker='0', tracker='0', intercept='0', return_at=RETURN_AT,
                 adaptive='0', hunt='0', shadow='0'):
        self.roles = _flag(roles)
        self.breaker = _flag(breaker)
        self.tracker = _flag(tracker)
        self.intercept = _flag(intercept)
        self.return_at = int(return_at)
        self.adaptive = _flag(adaptive)
        self.hunt = _flag(hunt)
        self.shadow = _flag(shadow)


def create_team(first_index, second_index, is_red,
                first='GreedyAttacker', second='PatrolDefender', roles='0', breaker='1',
                tracker='0', intercept='1', return_at='8', adaptive='0', hunt='0', shadow='0',
                num_training=0):
    cfg = Config(roles, breaker, tracker, intercept, return_at, adaptive, hunt, shadow)
    if cfg.roles:
        return [FlexAgent(first_index, cfg, 'attack'), FlexAgent(second_index, cfg, 'defend')]
    classes = {
        'GreedyAttacker': GreedyAttacker,
        'DeadEndAttacker': DeadEndAttacker,
        'PatrolDefender': PatrolDefender,
    }
    return [classes[first](first_index, cfg), classes[second](second_index, cfg)]


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
        self.cross = {b: (enemy_x, b[1]) for b in self.home_border}  # enemy cell across each entry
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

    def __init__(self, index, cfg=None, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.cfg = cfg if cfg is not None else Config()
        self.rng = random.Random(7919 + index)  # own RNG; never seed the global one (T-02)
        self.map = None
        self.food_to_win = None
        self.enemy_capsules = set()
        self.scared_since = None       # timeleft value at which we last saw an enemy capsule vanish
        self.unscared = set()          # enemies seen respawning since that capsule
        self.last_seen = {}            # enemy index -> (pos, timeleft)
        self.just_respawned = set()    # enemies detected as eaten during the current update
        self.possible = {}             # C3: enemy index -> set of cells it may occupy
        self.belief = {}               # P-22/23: enemy index -> {cell: probability}

    def register_initial_state(self, game_state):
        CaptureAgent.register_initial_state(self, game_state)
        self.map = MapInfo(game_state.get_walls(), self.red)
        self.food_to_win = len(self.get_food(game_state).as_list()) - 2
        self.enemy_capsules = set(self.get_capsules(game_state))
        self.scared_since = None
        self.unscared = set()
        self.last_seen = {}
        self.just_respawned = set()
        self.possible = {i: {game_state.get_initial_agent_position(i)}
                         for i in self.get_opponents(game_state)}
        self.belief = {i: {game_state.get_initial_agent_position(i): 1.0}
                       for i in self.get_opponents(game_state)}

    # --- perception (derived only from public observation data) ---

    def update_enemy_tracking(self, game_state):
        now = game_state.data.timeleft
        self.just_respawned = set()
        capsules = set(self.get_capsules(game_state))
        if self.enemy_capsules - capsules:  # only our pacmen can eat the capsules on the enemy side
            prev = self.get_previous_observation()
            self.scared_since = prev.data.timeleft if prev is not None else now
            self.unscared = set()
        self.enemy_capsules = capsules
        prev = self.get_previous_observation()
        prev_time = prev.data.timeleft if prev is not None else None
        team_prev = [prev.get_agent_position(t) for t in self.get_team(prev)] if prev is not None else []
        if (self.cfg.hunt or self.cfg.shadow) and prev is not None:
            # P-22/23: one of us that was eaten since (it teleported home) no longer keeps the enemy
            # in sight, so only teammates that moved at most one cell count (E-019: without this,
            # a ghost that ate our attacker was taken for eaten itself)
            team_now = [game_state.get_agent_position(t) for t in self.get_team(game_state)]
            team_prev = [t if t and c and self.map.d(t, c) <= 1 else None
                         for t, c in zip(team_prev, team_now)]
        for i in self.get_opponents(game_state):
            pos = game_state.get_agent_position(i)
            if pos is None:
                # Seen within Manhattan 2 of one of us last turn and gone now: since then each agent
                # moved at most once, so it would still be within sight (<= 5) unless it was eaten.
                if i in self.last_seen and self.last_seen[i][1] == prev_time:
                    last_pos = self.last_seen[i][0]
                    if any(abs(last_pos[0] - t[0]) + abs(last_pos[1] - t[1]) <= 2 for t in team_prev if t):
                        self.unscared.add(i)
                        self.just_respawned.add(i)
                        del self.last_seen[i]
                continue
            if i in self.last_seen:
                last_pos, last_time = self.last_seen[i]
                max_moves = (last_time - now) // 4 + 1
                if self.map.d(last_pos, pos) > max_moves + 1:  # teleported => respawned => not scared
                    self.unscared.add(i)
                    self.just_respawned.add(i)
            self.last_seen[i] = (pos, now)
        if self.cfg.tracker:
            self.update_possible(game_state)

    def update_possible(self, game_state):
        """C3: for each enemy, the set of cells it can be in (the support of the H-S01 belief).
        Each enemy moves exactly once between two of our turns; the set grows by one step, then
        loses the cells we can see and the cells the sonar rules out (|Manhattan - reading| <= 6
        holds exactly). Food or a capsule of ours vanishing pins the one enemy that can be there."""
        team = [game_state.get_agent_position(t) for t in self.get_team(game_state)]
        me = game_state.get_agent_position(self.index)
        readings = game_state.get_agent_distances()
        eaten = set()
        prev = self.get_previous_observation()
        if prev is not None:
            eaten = (set(self.get_food_you_are_defending(prev).as_list())
                     - set(self.get_food_you_are_defending(game_state).as_list()))
            eaten |= (set(self.get_capsules_you_are_defending(prev))
                      - set(self.get_capsules_you_are_defending(game_state)))
        seen = [game_state.get_agent_position(i) for i in self.get_opponents(game_state)]
        unexplained = [f for f in eaten if all(p is None or self.map.d(p, f) > 1 for p in seen)]

        def consistent(cell, reading):
            if any(abs(cell[0] - t[0]) + abs(cell[1] - t[1]) <= SIGHT for t in team if t):
                return False
            return abs(abs(cell[0] - me[0]) + abs(cell[1] - me[1]) - reading) <= SONAR_NOISE

        hidden = {}
        for i in self.get_opponents(game_state):
            pos = game_state.get_agent_position(i)
            if pos is not None:
                self.possible[i] = {pos}
                continue
            if i in self.just_respawned:
                grown = {game_state.get_initial_agent_position(i)}
            else:
                grown = set()
                for c in self.possible.get(i, ()):
                    grown.add(c)
                    grown.update(self.map.nbrs[c])
            hidden[i] = {c for c in grown if consistent(c, readings[i])}
        for f in unexplained:
            owners = [i for i, cells in hidden.items() if f in cells]
            if len(owners) == 1:
                hidden[owners[0]] = {f}
        for i, cells in hidden.items():
            if not cells:  # contradiction (e.g. a respawn we missed): restart from the sonar alone
                cells = {c for c in self.map.cells if consistent(c, readings[i])}
            self.possible[i] = cells

    def update_belief(self, game_state):
        """P-22/23 (H-S01, M-04): exact forward filter over cells for each enemy, from this agent's
        own observation only (no shared memory, rules.md Q4). Call after update_enemy_tracking.
        Between two of our turns each enemy moves exactly once (modelled as staying with weight
        STAY_WEIGHT and each neighbour with weight 1). An enemy we cannot see is not within SIGHT (Manhattan) of either of
        us, and our sonar reading is Manhattan + a uniform integer in [-6, 6], so it has the same
        likelihood 1/13 on every cell with |Manhattan - reading| <= 6 and 0 elsewhere. A food or
        capsule of ours that vanished under no visible enemy was eaten by an enemy that has not
        moved since (each moves once between our turns), so it stands exactly there."""
        team = [game_state.get_agent_position(t) for t in self.get_team(game_state)]
        me = game_state.get_agent_position(self.index)
        readings = game_state.get_agent_distances()

        def consistent(cell, reading):
            if any(abs(cell[0] - t[0]) + abs(cell[1] - t[1]) <= SIGHT for t in team if t):
                return False
            return abs(abs(cell[0] - me[0]) + abs(cell[1] - me[1]) - reading) <= SONAR_NOISE

        hidden = {}
        for i in self.get_opponents(game_state):
            pos = game_state.get_agent_position(i)
            if pos is not None:
                self.belief[i] = {pos: 1.0}
                continue
            if i in self.just_respawned:
                prior = {game_state.get_initial_agent_position(i): 1.0}
            else:
                prior = self.belief.get(i) or {}
            moved = {}
            for c, p in prior.items():
                share = p / (len(self.map.nbrs[c]) + STAY_WEIGHT)
                moved[c] = moved.get(c, 0.0) + share * STAY_WEIGHT
                for n in self.map.nbrs[c]:
                    moved[n] = moved.get(n, 0.0) + share
            hidden[i] = {c: p for c, p in moved.items() if consistent(c, readings[i])}

        prev = self.get_previous_observation()
        if prev is not None and hidden:
            eaten = (set(self.get_food_you_are_defending(prev).as_list())
                     - set(self.get_food_you_are_defending(game_state).as_list()))
            eaten |= (set(self.get_capsules_you_are_defending(prev))
                      - set(self.get_capsules_you_are_defending(game_state)))
            seen = set(game_state.get_agent_position(i) for i in self.get_opponents(game_state))
            owners = set(hidden)
            for f in sorted(eaten - seen):
                if not owners:
                    break
                owner = max(sorted(owners), key=lambda i: (hidden[i].get(f, 0.0),
                                                           -self.expected_dist(hidden[i], f)))
                hidden[owner] = {f: 1.0}
                owners.discard(owner)

        for i, cells in hidden.items():
            total = sum(cells.values())
            if total <= 0:  # contradiction (e.g. a respawn we missed): restart from the sonar alone
                cells = {c: 1.0 for c in self.map.cells if consistent(c, readings[i])}
                if not cells:
                    cells = {game_state.get_initial_agent_position(i): 1.0}
                total = float(len(cells))
            self.belief[i] = {c: p / total for c, p in cells.items() if p > 0}

    def expected_dist(self, belief, cell):
        """Expected maze distance from an enemy with this belief to `cell` (INF if empty)."""
        if not belief:
            return INF
        return sum(p * self.map.d(c, cell) for c, p in belief.items())

    def remembered_ghosts(self, game_state):
        """C3: cells where a hidden, non-scared enemy ghost may be, while its possible set is small."""
        cells = []
        for i in self.get_opponents(game_state):
            if game_state.get_agent_position(i) is not None or self.enemy_scared(i, game_state):
                continue
            possible = self.possible.get(i, ())
            if len(possible) <= TRACK_MAX_CELLS:
                cells.extend(c for c in possible if not self.map.is_ours(c))
        return cells

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

    def safe_fn(self, ghosts):
        """Race-safety (H-S03): our side is safe; an enemy cell is safe if we get there strictly
        before every ghost in `ghosts`."""
        def safe(cell, steps):
            if self.map.is_ours(cell):
                return True
            return all(self.map.d(g, cell) > steps for g in ghosts)
        return safe


#############
# Attackers #
#############

class GreedyAttacker(V1Agent):
    """Eats the nearest food it can reach before any visible ghost (race-safe BFS, H-S03),
    goes home when carrying enough / threatened / out of time (H-S04, H-S05)."""

    def register_initial_state(self, game_state):
        super().register_initial_state(game_state)
        self.blocked = deque(maxlen=STANDOFF_WINDOW)  # C2: recent moves, True = blocked at the border
        self.entry = None        # C2: border entry we are walking to
        self.ghost_seen = None   # C5: timeleft when we last saw a dangerous ghost

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        return self.attack(game_state)

    def attack(self, game_state):
        pos = game_state.get_agent_position(self.index)
        me = game_state.get_agent_state(self.index)
        carrying = me.num_carrying
        food = self.get_food(game_state).as_list()
        visible_ghosts = self.dangerous_ghosts(game_state)
        if visible_ghosts:
            self.ghost_seen = game_state.data.timeleft
        ghosts = visible_ghosts + self.remembered_ghosts(game_state) if self.cfg.tracker else visible_ghosts
        returned = sum(game_state.get_agent_state(i).num_returned for i in self.get_team(game_state))
        my_moves_left = game_state.data.timeleft // 4
        threatened = any(self.map.d(g, pos) <= THREAT_DIST for g in ghosts)

        go_home = carrying > 0 and (
            carrying >= self.return_threshold(game_state, pos)
            or len(food) <= 2
            or returned + carrying >= self.food_to_win
            or my_moves_left <= self.map.dist_home[pos] + TIME_MARGIN
            or threatened)

        safe = self.safe_fn(ghosts)
        if not go_home:
            if self.cfg.breaker and self.entry is not None:
                action = self.follow_entry(game_state, pos, me)
                if action is not None:
                    return action
            targets = [f for f in food if self.food_is_safe(f, pos, ghosts)]
            if targets:
                action, _ = self.bfs_action(game_state, targets, safe)
                if action is not None:
                    if self.cfg.breaker:
                        self.blocked.append(False)
                    return action
            if self.cfg.breaker:
                action = self.break_standoff(game_state, pos, me, ghosts, safe)
                if action is not None:
                    return action
        return self.retreat(game_state, ghosts, threatened, safe)

    def retreat(self, game_state, ghosts, threatened, safe):
        home_targets = list(self.map.home_border)
        if threatened:
            home_targets += self.get_capsules(game_state)  # a capsule is also an escape
        action, _ = self.bfs_action(game_state, home_targets, safe)
        if action is not None:
            return action
        return self.evade(game_state, ghosts)

    def return_threshold(self, game_state, pos):
        if not self.cfg.adaptive:
            return self.cfg.return_at
        carrying = game_state.get_agent_state(self.index).num_carrying
        if carrying >= 2 and self.map.dist_home[pos] <= ADAPT_BANK_DIST:
            return carrying  # home is right here: bank it
        since = INF if self.ghost_seen is None else (self.ghost_seen - game_state.data.timeleft) // 4
        if since <= ADAPT_RECENT:
            return min(self.cfg.return_at, ADAPT_LOW)
        if since >= ADAPT_QUIET:
            return max(self.cfg.return_at, ADAPT_HIGH)
        return self.cfg.return_at

    def break_standoff(self, game_state, pos, me, ghosts, safe):
        """C2: on our side with no safe food because a ghost blocks us. After STANDOFF_MOVES such
        moves within the last STANDOFF_WINDOW (a back-and-forth loop is blocked only every other
        move), take a capsule we reach first; otherwise walk (on our side) to the border entry
        farthest from the ghosts, and wait there again. (A race-lead criterion picked the entries
        next to the ghosts: every lead is <= 0 against a guard standing opposite us, and the
        nearest entry won the tie.)"""
        if me.is_pacman or not ghosts:
            self.blocked.clear()
            self.entry = None
            return None
        self.blocked.append(True)
        if sum(self.blocked) < STANDOFF_MOVES:
            return None
        capsules = self.get_capsules(game_state)
        if capsules:
            action, _ = self.bfs_action(game_state, capsules, safe)
            if action is not None:
                return action
        candidates = [b for b in self.map.home_border if b != pos]
        if not candidates:
            return None

        def away(b):
            ghost_d = min(self.map.d(g, self.map.cross[b]) for g in ghosts)
            return ghost_d, -self.map.d(pos, b), b

        self.entry = max(candidates, key=away)
        self.blocked.clear()
        return self.follow_entry(game_state, pos, me)

    def follow_entry(self, game_state, pos, me):
        """C2: keep walking (on our side) to the chosen entry, even when the ghosts drop out of
        sight (forgetting them caused a back-and-forth loop, E-007); drop it on arrival."""
        if me.is_pacman or pos == self.entry:
            self.entry = None
            return None
        action, _ = self.bfs_action(game_state, [self.entry], lambda c, s: self.map.is_ours(c))
        if action is None:
            self.entry = None
        return action

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
        self.raider = None   # P-23: enemy index last evident on our side

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        if self.cfg.hunt or self.cfg.shadow:
            self.update_belief(game_state)
            self.update_raider(game_state)
        return self.defend(game_state)

    def defend(self, game_state):
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

        if self.cfg.hunt and not invaders:
            # P-22: the belief already holds the food events, so it replaces the eaten-food target
            self.target = None
            suspect = self.suspected_invader(pos)
            if suspect is not None and not scared:
                invaders = [suspect]

        if invaders and self.cfg.intercept:
            nearest = min(invaders, key=lambda p: self.map.d(pos, p))
            target = self.intercept_cell(pos, nearest)
            if target != nearest:
                action, _ = self.bfs_action(game_state, [target], lambda cell, steps: self.map.is_ours(cell))
                if action is not None:
                    return action
                if target == pos:
                    return Directions.STOP
            target = nearest
        elif invaders:  # without the intercept: the nearest invader (seen or, P-22, suspected)
            target = min(invaders, key=lambda p: self.map.d(pos, p))
        elif self.target is not None:
            target = self.target
        else:
            target = self.shadow_post(pos) if self.cfg.shadow else None
            if target is None:
                target = self.next_patrol_point(game_state, pos)
        if target == pos:
            return Directions.STOP
        action, _ = self.bfs_action(game_state, [target], lambda cell, steps: self.map.is_ours(cell))
        if action is not None:
            return action
        self.target = None
        return Directions.STOP

    def intercept_cell(self, pos, invader):
        """C4: where to meet a visible invader. Close by: go for it. In a dead end: hold its exit if
        we get there first (and walk in once we stand between it and the exit). Otherwise: the
        first cell on its shortest way home that we reach no later than it does."""
        if self.map.d(pos, invader) <= 2:
            return invader
        exit_cell = self.map.entrance[invader]
        if self.map.depth[invader] > 0 and self.map.is_ours(exit_cell):
            between = self.map.d(invader, exit_cell) == self.map.d(invader, pos) + self.map.d(pos, exit_cell)
            if between:
                return invader
            if self.map.d(pos, exit_cell) <= self.map.d(invader, exit_cell):
                return exit_cell
        if not self.map.home_border:
            return invader
        goal = min(self.map.home_border, key=lambda b: (self.map.d(invader, b), b))
        cell = invader
        while cell != goal:
            step = self.map.d(cell, goal) - 1
            cell = min((n for n in self.map.nbrs[cell] if self.map.d(n, goal) == step),
                       key=lambda n: (self.map.d(pos, n), n))
            if self.map.d(pos, cell) <= self.map.d(invader, cell):
                return cell
        return invader

    def suspected_invader(self, pos):
        """P-22: the most likely home cell of the hidden enemy with the most belief mass on our side,
        if that mass is at least HUNT_MASS (visible enemies have all their mass on their cell)."""
        best = None
        for i in sorted(self.belief):
            ours = dict((c, p) for c, p in self.belief[i].items() if self.map.is_ours(c))
            mass = sum(ours.values())
            if mass >= HUNT_MASS and (best is None or mass > best[0]):
                cell = max(ours, key=lambda c: (ours[c], -self.map.d(pos, c), c))
                best = (mass, cell)
        return best[1] if best is not None else None

    def update_raider(self, game_state):
        """P-23: the enemy most recently evident on our side (seen there, or with belief mass of at
        least HUNT_MASS there). Their defender is never it, unless it has come over."""
        for i, _, invader in self.visible_enemies(game_state):
            if invader:
                self.raider = i
        for i in sorted(self.belief):
            if game_state.get_agent_position(i) is None and \
                    sum(p for c, p in self.belief[i].items() if self.map.is_ours(c)) >= HUNT_MASS:
                self.raider = i

    def shadow_post(self, pos):
        """P-23: the border entry whose cell across is nearest (in expectation) to the raider, i.e.
        where it would most likely cross; None while no enemy has come over yet. (Shadowing the
        enemy nearest our side picked their border guard and showed it to our attacker, which
        then stood blocked: a 0-0 against baseline_team, E-019.)"""
        if self.raider is None or not self.map.home_border:
            return None
        belief = self.belief.get(self.raider)
        if not belief:
            return None
        return min(self.map.home_border,
                   key=lambda b: (self.expected_dist(belief, self.map.cross[b]), self.map.d(pos, b), b))

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


#####################
# C1: flexible role #
#####################

class FlexAgent(GreedyAttacker, PatrolDefender):
    """C1 (H-S08, H-S05): attacks or defends each turn. The home attacker defends while two
    invaders are evident; the home defender attacks after QUIET_MOVES own moves without any
    invader evidence and comes back on the first evidence; in the last ENDGAME_MOVES own moves
    both defend when we lead and both attack when we trail. Each agent decides from its own
    observation (no shared memory, rules.md Q4)."""

    def __init__(self, index, cfg, home_role):
        super().__init__(index, cfg)
        self.home_role = home_role
        self.role = home_role

    def register_initial_state(self, game_state):
        super().register_initial_state(game_state)
        self.role = self.home_role
        self.invader_time = {}     # enemy index -> timeleft of its last evidence on our side
        self.unknown_time = None   # timeleft of the last food event we could not attribute
        self.quiet_since = game_state.data.timeleft

    def choose_action(self, game_state):
        self.update_enemy_tracking(game_state)
        role = self.decide_role(game_state)
        if role != self.role:
            self.role = role
            self.target, self.entry = None, None
            self.blocked.clear()
        if role == 'attack':
            return self.attack(game_state)
        if game_state.get_agent_state(self.index).is_pacman:  # called back: get home first
            pos = game_state.get_agent_position(self.index)
            ghosts = self.dangerous_ghosts(game_state)
            threatened = any(self.map.d(g, pos) <= THREAT_DIST for g in ghosts)
            return self.retreat(game_state, ghosts, threatened, self.safe_fn(ghosts))
        return self.defend(game_state)

    def decide_role(self, game_state):
        now = game_state.data.timeleft
        invaders = self.count_invaders(game_state)
        if invaders:
            self.quiet_since = now
        if now // 4 <= ENDGAME_MOVES:
            score = self.get_score(game_state)
            if score > 0:
                return 'defend'
            if score < 0:
                return 'attack'
        if self.home_role == 'attack':
            return 'defend' if invaders >= 2 else 'attack'
        if invaders == 0 and (self.quiet_since - now) // 4 >= QUIET_MOVES:
            return 'attack'
        return 'defend'

    def count_invaders(self, game_state):
        """Number of distinct enemies with evidence of being on our side in the last
        EVIDENCE_PLIES: seen there, or the only hidden enemy when our food vanished out of reach
        of every visible invader. An unattributable event counts as one invader at most."""
        now = game_state.data.timeleft
        visible = self.visible_enemies(game_state)
        for i, _, invader in visible:
            if invader:
                self.invader_time[i] = now
            else:
                self.invader_time.pop(i, None)  # back on its own side
        for i in self.just_respawned:
            self.invader_time.pop(i, None)
        prev = self.get_previous_observation()
        if prev is not None:
            eaten = (set(self.get_food_you_are_defending(prev).as_list())
                     - set(self.get_food_you_are_defending(game_state).as_list()))
            eaten |= (set(self.get_capsules_you_are_defending(prev))
                      - set(self.get_capsules_you_are_defending(game_state)))
            seen_invaders = [p for _, p, invader in visible if invader]
            hidden = [i for i in self.get_opponents(game_state) if game_state.get_agent_position(i) is None]
            for f in eaten:
                if any(self.map.d(p, f) <= 1 for p in seen_invaders) or not hidden:
                    continue
                if len(hidden) == 1:
                    self.invader_time[hidden[0]] = now
                    continue
                known = [i for i in hidden
                         if i in self.invader_time and self.invader_time[i] - now <= EVIDENCE_PLIES]
                if known:
                    self.invader_time[known[0]] = now
                else:
                    self.unknown_time = now
        recent = [i for i, t in self.invader_time.items() if t - now <= EVIDENCE_PLIES]
        if not recent and self.unknown_time is not None and self.unknown_time - now <= EVIDENCE_PLIES:
            return 1
        return len(recent)
