# heldout_a.py
# ------------
# Held-out sparring team A. Used only as a local evaluation opponent; never
# submitted. Self-contained: imports only the contest framework and stdlib.

import heapq
import random
from collections import deque

from contest.capture_agents import CaptureAgent
from contest.game import Directions

BIG = 10 ** 6
SIGHT = 5
SCARED_TIME = 40
NOISE = 6
DIRS = (('North', 0, 1), ('South', 0, -1), ('East', 1, 0), ('West', -1, 0))


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def create_team(first_index, second_index, is_red,
                first='RaiderAgent', second='RaiderAgent', **kwargs):
    brain = TeamBrain(is_red)
    return [RaiderAgent(first_index, brain), RaiderAgent(second_index, brain)]


##############################################################################
# Static map analysis                                                        #
##############################################################################

class MapInfo(object):

    def __init__(self, walls, is_red):
        w, h = walls.width, walls.height
        self.width, self.height = w, h
        cells = []
        for x in range(w):
            col = walls[x]
            for y in range(h):
                if not col[y]:
                    cells.append((x, y))
        cellset = set(cells)
        self.cells = cells
        self.moves = {}
        self.nbrs = {}
        for c in cells:
            mv = []
            for name, dx, dy in DIRS:
                n = (c[0] + dx, c[1] + dy)
                if n in cellset:
                    mv.append((name, n))
            self.moves[c] = mv
            self.nbrs[c] = [n for _, n in mv]
        mid = w // 2
        if is_red:
            hx, ex = mid - 1, mid
        else:
            hx, ex = mid, mid - 1
        self.home = set(c for c in cells if (c[0] < mid) == is_red)
        self.home_list = [c for c in cells if c in self.home]
        self.enemy_cells = [c for c in cells if c not in self.home]
        self.boundary = [(hx, y) for y in range(h)
                         if (hx, y) in cellset and (ex, y) in cellset]
        self.enemy_boundary = [(ex, y) for (_, y) in self.boundary]
        self.home_dist = self.bfs_multi(self.boundary)
        self.dead_depth, self.dead_exit = self.dead_ends()

    def bfs_multi(self, sources):
        dist = {}
        q = deque()
        for s in sources:
            dist[s] = 0
            q.append(s)
        while q:
            c = q.popleft()
            d = dist[c] + 1
            for n in self.nbrs[c]:
                if n not in dist:
                    dist[n] = d
                    q.append(n)
        for c in self.cells:
            if c not in dist:
                dist[c] = BIG
        return dist

    def dead_ends(self):
        deg = dict((c, len(self.nbrs[c])) for c in self.cells)
        removed = set()
        q = deque(c for c in self.cells if deg[c] <= 1)
        while q:
            c = q.popleft()
            if c in removed:
                continue
            removed.add(c)
            for n in self.nbrs[c]:
                if n not in removed:
                    deg[n] -= 1
                    if deg[n] <= 1:
                        q.append(n)
        depth = {}
        exit_cell = {}
        q = deque()
        for c in self.cells:
            if c not in removed:
                depth[c] = 0
                exit_cell[c] = c
                q.append(c)
        while q:
            c = q.popleft()
            for n in self.nbrs[c]:
                if n in removed and n not in depth:
                    depth[n] = depth[c] + 1
                    exit_cell[n] = exit_cell[c]
                    q.append(n)
        for c in self.cells:
            if c not in depth:
                depth[c] = 0
                exit_cell[c] = c
        return depth, exit_cell


##############################################################################
# Shared team state: opponent tracking, roles, planning helpers             #
##############################################################################

class TeamBrain(object):

    def __init__(self, is_red):
        self.is_red = is_red
        self.registrations = 0
        self.map = None

    def register(self, agent, gs):
        self.registrations += 1
        if self.registrations % 2 == 1:
            self.reset(agent, gs)

    def reset(self, agent, gs):
        self.map = MapInfo(gs.get_walls(), self.is_red)
        self.team = list(agent.get_team(gs))
        self.opps = list(agent.get_opponents(gs))
        self.n_agents = gs.get_num_agents()
        self.start = {}
        self.belief = {}
        for o in self.opps:
            s = gs.get_initial_agent_position(o)
            self.start[o] = s
            self.belief[o] = {s: 1.0}
        self.scared = dict((o, 0) for o in self.opps)
        self.last_seen = dict((o, None) for o in self.opps)
        self.prev_def_food = set(agent.get_food_you_are_defending(gs).as_list())
        self.prev_def_caps = set(agent.get_capsules_you_are_defending(gs))
        self.prev_enemy_caps = set(agent.get_capsules(gs))
        self.tick = 0
        self.last_eaten = None
        self.threat_tick = -100
        self.ghost_seen_tick = -100
        self.defender = None
        self.defender_since = -100
        self.all_defend = False
        self.targets = {}
        self.patrol = {}

    def mate_of(self, index):
        for i in self.team:
            if i != index:
                return i
        return index

    # ---------------------------------------------------------------- beliefs
    def observe(self, agent, gs):
        self.tick += 1
        me = agent.index
        my_pos = gs.get_agent_position(me)
        mate_pos = gs.get_agent_position(self.mate_of(me))
        mover = (me - 1) % self.n_agents
        if mover in self.belief:
            self.elapse(mover)
            if self.scared[mover] > 0:
                self.scared[mover] -= 1

        cur_food = set(agent.get_food_you_are_defending(gs).as_list())
        cur_caps = set(agent.get_capsules_you_are_defending(gs))
        gone = (self.prev_def_food - cur_food) | (self.prev_def_caps - cur_caps)
        if gone:
            pos = min(gone)
            if mover in self.belief:
                self.belief[mover] = {pos: 1.0}
            self.last_eaten = (pos, self.tick)
            self.threat_tick = self.tick
        self.prev_def_food = cur_food
        self.prev_def_caps = cur_caps

        enemy_caps = set(agent.get_capsules(gs))
        if len(enemy_caps) < len(self.prev_enemy_caps):
            for o in self.opps:
                self.scared[o] = SCARED_TIME
        self.prev_enemy_caps = enemy_caps

        dists = gs.get_agent_distances()
        for o in self.opps:
            pos = gs.get_agent_position(o)
            if pos is not None:
                st = gs.get_agent_state(o)
                self.belief[o] = {pos: 1.0}
                self.scared[o] = st.scared_timer
                self.last_seen[o] = (pos, self.tick, st.is_pacman)
                if st.is_pacman:
                    self.threat_tick = self.tick
                elif st.scared_timer == 0:
                    self.ghost_seen_tick = self.tick
                continue
            reading = dists[o] if dists else None
            nb = {}
            for c, p in self.belief[o].items():
                if manhattan(c, my_pos) <= SIGHT or manhattan(c, mate_pos) <= SIGHT:
                    continue
                if reading is not None and abs(manhattan(c, my_pos) - reading) > NOISE:
                    continue
                nb[c] = p
            if not nb:
                nb = self.reinit(o, my_pos, mate_pos, reading)
            total = sum(nb.values())
            for c in nb:
                nb[c] = nb[c] / total
            self.belief[o] = nb

    def reinit(self, o, my_pos, mate_pos, reading):
        def ok(c):
            if manhattan(c, my_pos) <= SIGHT or manhattan(c, mate_pos) <= SIGHT:
                return False
            if reading is not None and abs(manhattan(c, my_pos) - reading) > NOISE:
                return False
            return True
        s = self.start[o]
        self.last_seen[o] = None
        if ok(s):
            self.scared[o] = 0
            return {s: 1.0}
        cand = [c for c in self.map.cells if ok(c)]
        if not cand:
            cand = list(self.map.cells)
        p = 1.0 / len(cand)
        return dict((c, p) for c in cand)

    def elapse(self, o):
        nbrs = self.map.nbrs
        nb = {}
        for c, p in self.belief[o].items():
            ns = nbrs[c]
            share = p / (len(ns) + 1)
            nb[c] = nb.get(c, 0.0) + share
            for n in ns:
                nb[n] = nb.get(n, 0.0) + share
        self.belief[o] = nb

    def most_likely(self, o):
        best, bp = None, -1.0
        for c, p in self.belief[o].items():
            if p > bp:
                best, bp = c, p
        return best

    def home_mass(self, o):
        home = self.map.home
        return sum(p for c, p in self.belief[o].items() if c in home)

    def home_argmax(self, o):
        home = self.map.home
        best, bp = None, -1.0
        for c, p in self.belief[o].items():
            if c in home and p > bp:
                best, bp = c, p
        return best

    # ---------------------------------------------------------------- threats
    def visible_invaders(self, gs):
        res = []
        for o in self.opps:
            p = gs.get_agent_position(o)
            if p is None:
                continue
            st = gs.get_agent_state(o)
            if st.is_pacman:
                res.append((o, p, st.num_carrying))
        return res

    def threat_position(self, gs):
        inv = self.visible_invaders(gs)
        if inv:
            inv.sort(key=lambda t: -t[2])
            return inv[0][1]
        if self.last_eaten is not None and self.tick - self.last_eaten[1] <= 8:
            return self.last_eaten[0]
        for o in self.opps:
            if self.home_mass(o) > 0.8:
                return self.home_argmax(o)
        return None

    def danger_ghosts(self, gs):
        res = []
        for o in self.opps:
            p = gs.get_agent_position(o)
            if p is not None:
                st = gs.get_agent_state(o)
                if st.is_pacman:
                    continue
                res.append((p, 0, st.scared_timer))
                continue
            ls = self.last_seen[o]
            if ls is None:
                continue
            lpos, ltick, was_pac = ls
            age = self.tick - ltick
            if was_pac or age > 6 or lpos in self.map.home:
                continue
            res.append((lpos, (age + 1) // 2, self.scared[o]))
        return res

    # ---------------------------------------------------------------- roles
    def update_roles(self, agent, gs):
        moves_left = gs.data.timeleft // 4
        score = agent.get_score(gs)
        self.all_defend = score > 0 and moves_left < 25
        threat = self.threat_position(gs)
        if threat is not None:
            self.threat_tick = self.tick
        if self.tick - self.threat_tick > 14:
            self.defender = None
            return
        if threat is None:
            threat = self.last_eaten[0] if self.last_eaten else None
        if threat is None:
            return
        costs = {}
        for i in self.team:
            st = gs.get_agent_state(i)
            p = gs.get_agent_position(i)
            c = agent.dist(p, threat)
            if st.is_pacman:
                c += 10 + 2 * st.num_carrying
            costs[i] = c
        best = min(self.team, key=lambda i: (costs[i], i))
        if self.defender is None:
            self.defender = best
            self.defender_since = self.tick
        elif best != self.defender and self.tick - self.defender_since > 10 \
                and costs[best] + 6 < costs[self.defender]:
            self.defender = best
            self.defender_since = self.tick

    def role_of(self, index):
        if self.all_defend or index == self.defender:
            return 'defend'
        return 'attack'

    # ---------------------------------------------------------------- planning
    def danger_map(self, agent, ghosts):
        dg = {}
        dist = agent.dist
        for c in self.map.enemy_cells:
            best = BIG
            for g, slack, sc in ghosts:
                v = dist(g, c) - slack
                if v < sc:
                    v = sc
                if v < best:
                    best = v
            dg[c] = best
        return dg

    def safe_reach(self, start, dg, margin):
        m = self.map
        home = m.home
        dist = {start: 0}
        first = {start: None}
        q = deque([start])
        while q:
            c = q.popleft()
            t = dist[c] + 1
            fc = first[c]
            for a, n in m.moves[c]:
                if n in dist:
                    continue
                if dg is not None and n not in home and t + margin >= dg.get(n, BIG):
                    continue
                dist[n] = t
                first[n] = a if fc is None else fc
                q.append(n)
        return dist, first

    def escape_latest(self, dg, margin, caps):
        m = self.map
        home = m.home
        L = dict.fromkeys(m.cells, -BIG)
        heap = []
        for c in m.home_list:
            L[c] = BIG
        for c in m.boundary:
            heap.append((-BIG, c))
        for c in caps:
            v = dg.get(c, BIG) - margin - 1
            if v > L[c]:
                L[c] = v
                heap.append((-v, c))
        heapq.heapify(heap)
        while heap:
            nv, c = heapq.heappop(heap)
            v = -nv
            if v < L[c]:
                continue
            for n in m.nbrs[c]:
                if n in home:
                    continue
                cand = min(v - 1, dg.get(n, BIG) - margin - 1)
                if cand > L[n]:
                    L[n] = cand
                    heapq.heappush(heap, (-cand, n))
        return L


##############################################################################
# Agent                                                                      #
##############################################################################

class RaiderAgent(CaptureAgent):

    def __init__(self, index, brain, time_for_computing=0.1):
        CaptureAgent.__init__(self, index, time_for_computing)
        self.brain = brain
        self.rng = random.Random(1009 + 31 * index)
        self.recent = deque(maxlen=16)
        self.forced = None

    def register_initial_state(self, gs):
        CaptureAgent.register_initial_state(self, gs)
        self.brain.register(self, gs)
        self.recent = deque(maxlen=16)
        self.forced = None

    def dist(self, a, b):
        return self.distancer.get_distance(a, b)

    def choose_action(self, gs):
        legal = gs.get_legal_actions(self.index)
        self.brain.observe(self, gs)
        action = self.decide(gs)
        if action is None or action not in legal:
            options = [a for a in legal if a != Directions.STOP]
            if not options:
                options = legal
            action = self.rng.choice(options)
        return action

    # ------------------------------------------------------------------ top
    def decide(self, gs):
        b = self.brain
        me = self.index
        my_state = gs.get_agent_state(me)
        my_pos = gs.get_agent_position(me)
        self.recent.append(my_pos)
        b.update_roles(self, gs)

        # An unscared ghost at home grabs any invader that comes close.
        if not my_state.is_pacman and my_state.scared_timer == 0:
            best = None
            for o, p, c in b.visible_invaders(gs):
                d = self.dist(my_pos, p)
                if d <= 3 and (best is None or d < best[0]):
                    best = (d, p)
            if best is not None:
                if best[0] == 2 and self.circling() and self.rng.random() < 0.6:
                    return Directions.STOP
                act = self.home_step(my_pos, best[1])
                if act is not None:
                    return act

        if b.role_of(me) == 'defend':
            return self.defend(gs, my_pos, my_state)
        return self.attack(gs, my_pos, my_state)

    # ------------------------------------------------------------------ attack
    def attack(self, gs, my_pos, my_state):
        b = self.brain
        m = b.map
        foods = self.get_food(gs).as_list()
        caps = self.get_capsules(gs)
        carry = my_state.num_carrying
        moves_left = gs.data.timeleft // 4
        ghosts = b.danger_ghosts(gs)
        margin = 1
        dg = b.danger_map(self, ghosts) if ghosts else None
        reach, first = b.safe_reach(my_pos, dg, margin)
        L = b.escape_latest(dg, margin, caps) if dg is not None else None
        dh = m.home_dist.get(my_pos, 0)
        close_ghost = BIG
        for g, slack, sc in ghosts:
            if sc <= 3:
                close_ghost = min(close_ghost, self.dist(g, my_pos) - slack)

        # Hunt scared ghosts that are close: they go back through the prison.
        for o in b.opps:
            p = gs.get_agent_position(o)
            if p is None or p in m.home:
                continue
            st = gs.get_agent_state(o)
            if st.is_pacman or st.scared_timer <= 0:
                continue
            dd = self.dist(my_pos, p)
            if dd <= 3 and st.scared_timer > dd + 2 and p in reach and first.get(p):
                return first[p]

        must_return = carry > 0 and (len(foods) <= 2 or moves_left <= dh + 5)
        thresh = self.return_threshold(dh)
        want_return = must_return or carry >= thresh or (carry >= 3 and close_ghost <= 4)

        mate = b.mate_of(self.index)
        mate_target = b.targets.get(mate) if b.role_of(mate) == 'attack' else None
        half = m.height / 2.0
        lower_index = self.index == min(b.team)
        prev_target = b.targets.get(self.index)
        best = None
        for f in foods:
            t = reach.get(f)
            if t is None:
                continue
            cost = t
            if L is not None and t > L.get(f, -BIG):
                # No guaranteed escape: only take open-floor food with a clear lead.
                if m.dead_depth.get(f, 0) > 0 or dg.get(f, BIG) - t < 3:
                    continue
                cost += 8
            if f == prev_target:
                cost -= 2
            if mate_target is not None and self.dist(f, mate_target) <= 5:
                cost += 6
            if b.tick < 60 and mate_target is not None:
                if (f[1] < half) == lower_index:
                    cost += 5
            if best is None or cost < best[0]:
                best = (cost, f)

        if want_return:
            if best is not None and not must_return and reach[best[1]] <= 1:
                return first[best[1]]
            act = self.toward_home(my_pos, reach, first)
            if act is not None:
                return act
            act = self.toward_capsule(caps, reach, first, dg, margin, 12)
            if act is not None:
                return act
            return self.flee(my_pos, dg, L, caps)

        if close_ghost <= 5 and caps:
            act = self.toward_capsule(caps, reach, first, dg, margin, 10)
            if act is not None:
                return act

        if best is not None:
            b.targets[self.index] = best[1]
            return first[best[1]]
        b.targets[self.index] = None
        if my_state.is_pacman:
            act = self.toward_home(my_pos, reach, first)
            if act is not None:
                return act
            act = self.toward_capsule(caps, reach, first, dg, margin, 12)
            if act is not None:
                return act
            return self.flee(my_pos, dg, L, caps)
        return self.probe(my_pos, ghosts)

    def return_threshold(self, dh):
        b = self.brain
        th = 6
        if b.tick - b.ghost_seen_tick > 24:
            th = 9
        if min(b.scared.values()) > dh + 8:
            th += 6
        return th

    def toward_home(self, my_pos, reach, first):
        m = self.brain.map
        if my_pos in m.home:
            return None
        best = None
        for c in m.boundary:
            t = reach.get(c)
            if t is not None and (best is None or t < best[0]):
                best = (t, c)
        if best is None:
            return None
        return first[best[1]]

    def toward_capsule(self, caps, reach, first, dg, margin, limit):
        best = None
        for c in caps:
            t = reach.get(c)
            if t is None or t > limit:
                continue
            if dg is not None and t + margin >= dg.get(c, BIG):
                continue
            if best is None or t < best[0]:
                best = (t, c)
        if best is None:
            return None
        return first[best[1]]

    def flee(self, my_pos, dg, L, caps):
        m = self.brain.map
        best = None
        options = list(m.moves[my_pos]) + [(Directions.STOP, my_pos)]
        recent = set(list(self.recent)[-8:])
        for a, n in options:
            if n in m.home:
                s = 1000.0
            else:
                g = dg.get(n, BIG) if dg is not None else BIG
                if g <= 1:
                    s = -1000.0 + g
                else:
                    s = 10.0 * min(g, 12)
                    if L is not None:
                        s += 2.0 * max(-10, min(L.get(n, -BIG), 10))
                    s -= 3.0 * m.dead_depth.get(n, 0)
                    s -= 0.5 * min(m.home_dist.get(n, 0), 40)
                    if n in caps:
                        s += 500.0
                    if n in recent:
                        s -= 4.0
            if a == Directions.STOP:
                s -= 5.0
            if best is None or s > best[0]:
                best = (s, a)
        return best[1]

    def probe(self, my_pos, ghosts):
        """At home with nothing safe to eat: shift to a lane far from the guards."""
        b = self.brain
        m = b.map
        live = [(g, slack) for g, slack, sc in ghosts if sc <= 3]
        if len(set(self.recent)) <= 3 and len(self.recent) >= 14:
            if self.forced is None or self.forced[1] < b.tick:
                far = [c for c in m.boundary if self.dist(c, my_pos) >= 6]
                if far:
                    self.forced = (self.rng.choice(far), b.tick + 12)
        if self.forced is not None and self.forced[1] >= b.tick and self.forced[0] != my_pos:
            act = self.home_step(my_pos, self.forced[0])
            if act is not None:
                return act
        best = None
        for bc, ec in zip(m.boundary, m.enemy_boundary):
            if live:
                gd = min(self.dist(g, ec) - s for g, s in live)
            else:
                gd = 15
            s = 2.0 * min(gd, 15) - self.dist(my_pos, bc)
            if best is None or s > best[0]:
                best = (s, bc)
        if best is None:
            return None
        return self.home_step(my_pos, best[1])

    # ------------------------------------------------------------------ defence
    def defend(self, gs, my_pos, my_state):
        b = self.brain
        m = b.map
        if my_pos not in m.home:
            ghosts = b.danger_ghosts(gs)
            dg = b.danger_map(self, ghosts) if ghosts else None
            reach, first = b.safe_reach(my_pos, dg, 1)
            act = self.toward_home(my_pos, reach, first)
            if act is not None:
                return act
            L = b.escape_latest(dg, 1, self.get_capsules(gs)) if dg is not None else None
            return self.flee(my_pos, dg, L, self.get_capsules(gs))
        scared = my_state.scared_timer
        invaders = b.visible_invaders(gs)
        if invaders:
            mate = b.mate_of(self.index)
            mate_pos = gs.get_agent_position(mate)
            if len(invaders) > 1 and b.role_of(mate) == 'defend':
                # split: take the invader the teammate is not closest to
                mine = min(invaders, key=lambda t: self.dist(my_pos, t[1]) - self.dist(mate_pos, t[1]))
            else:
                mine = min(invaders, key=lambda t: self.dist(my_pos, t[1]))
            ipos = mine[1]
            if scared > 0:
                return self.shadow(my_pos, ipos)
            if self.dist(my_pos, ipos) == 2 and self.circling():
                # chasing round a loop never ends: hold the cell instead
                if self.rng.random() < 0.6:
                    return Directions.STOP
            target = self.intercept(gs, my_pos, ipos, mine[2])
            return self.home_step(my_pos, target)
        est = b.threat_position(gs)
        if est is not None and est in m.home:
            return self.home_step(my_pos, est)
        return self.home_step(my_pos, self.patrol_point(gs, my_pos))

    def circling(self):
        tail = list(self.recent)[-8:]
        return len(tail) >= 8 and len(set(tail)) <= 4

    def intercept(self, gs, my_pos, ipos, carrying):
        m = self.brain.map
        if self.dist(my_pos, ipos) <= 3 or not m.boundary:
            return ipos
        if carrying < 4:
            # Ambush the food it is most likely heading for.
            foods = self.get_food_you_are_defending(gs).as_list()
            foods.sort(key=lambda f: self.dist(ipos, f))
            for f in foods[:3]:
                if self.dist(my_pos, f) < self.dist(ipos, f):
                    return f
        ex = min(m.boundary, key=lambda c: self.dist(ipos, c))
        dix = self.dist(ipos, ex)
        best = None
        for c in m.home_list:
            dic = self.dist(ipos, c)
            if dic > dix or dic + self.dist(c, ex) != dix:
                continue
            if self.dist(my_pos, c) < dic and (best is None or dic < best[0]):
                best = (dic, c)
        if best is not None:
            return best[1]
        return ipos

    def shadow(self, my_pos, ipos):
        m = self.brain.map
        best = None
        for a, n in list(m.moves[my_pos]) + [(Directions.STOP, my_pos)]:
            if n not in m.home:
                continue
            d = self.dist(n, ipos)
            s = -100.0 + d if d <= 1 else -abs(d - 2)
            if best is None or s > best[0]:
                best = (s, a)
        return best[1] if best is not None else Directions.STOP

    def patrol_point(self, gs, my_pos):
        b = self.brain
        m = b.map
        if not m.boundary:
            return my_pos
        ests = [b.most_likely(o) for o in b.opps]
        ests = [e for e in ests if e is not None]
        foods = self.get_food_you_are_defending(gs).as_list()
        scores = {}
        for bc in m.boundary:
            de = min(self.dist(bc, e) for e in ests) if ests else 0
            df = min(self.dist(bc, f) for f in foods) if foods else 0
            scores[bc] = de + 0.5 * df
        best = min(m.boundary, key=lambda c: scores[c])
        prev = b.patrol.get(self.index)
        if prev is not None and prev in scores and scores[prev] <= scores[best] + 2:
            best = prev
        b.patrol[self.index] = best
        return best

    def home_step(self, my_pos, target):
        m = self.brain.map
        if target == my_pos:
            return Directions.STOP
        if my_pos in m.home and target in m.home:
            first = {my_pos: None}
            q = deque([my_pos])
            while q:
                c = q.popleft()
                if c == target:
                    break
                fc = first[c]
                for a, n in m.moves[c]:
                    if n in first or n not in m.home:
                        continue
                    first[n] = a if fc is None else fc
                    q.append(n)
            if first.get(target) is not None:
                return first[target]
        best = None
        for a, n in m.moves[my_pos]:
            if my_pos in m.home and n not in m.home:
                continue
            d = self.dist(n, target)
            if best is None or d < best[0]:
                best = (d, a)
        return best[1] if best is not None else None
