# heldout_b.py
# ------------
# Held-out sparring team B. Used only as a local evaluation opponent; never
# submitted. Self-contained: imports only the contest framework and stdlib.

import heapq
import random
import time
from collections import deque

from contest.capture_agents import CaptureAgent
from contest.game import Directions

INF = 10 ** 6
SIGHT = 5
SCARED_TIME = 40
NOISE = 6
STEPS = (('North', 0, 1), ('South', 0, -1), ('East', 1, 0), ('West', -1, 0))
SEARCH_BUDGET = 0.12


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def create_team(first_index, second_index, is_red,
                first='Anchor', second='Raider', **kwargs):
    hq = Headquarters(is_red, first_index, second_index)
    return [FortressAgent(first_index, hq, 'anchor'),
            FortressAgent(second_index, hq, 'raider')]


##############################################################################
# Board geometry                                                             #
##############################################################################

class Board(object):

    def __init__(self, walls, is_red):
        self.width, self.height = walls.width, walls.height
        open_cells = []
        for x in range(self.width):
            for y in range(self.height):
                if not walls[x][y]:
                    open_cells.append((x, y))
        self.cells = open_cells
        cellset = set(open_cells)
        self.steps = {}
        self.adj = {}
        for c in open_cells:
            st = []
            for name, dx, dy in STEPS:
                n = (c[0] + dx, c[1] + dy)
                if n in cellset:
                    st.append((name, n))
            self.steps[c] = st
            self.adj[c] = [n for _, n in st]
        mid = self.width // 2
        own_x = mid - 1 if is_red else mid
        far_x = mid if is_red else mid - 1
        self.ours = set(c for c in open_cells if (c[0] < mid) == is_red)
        self.ours_list = [c for c in open_cells if c in self.ours]
        self.theirs_list = [c for c in open_cells if c not in self.ours]
        self.gates = [(own_x, y) for y in range(self.height)
                      if (own_x, y) in cellset and (far_x, y) in cellset]
        self.gate_dist = self._bfs(self.gates)
        self.pocket_depth, self.pocket_mouth = self._pockets()
        # cells near our border, used for patrol
        self.border_zone = [c for c in self.ours_list if self.gate_dist[c] <= 3]

    def _bfs(self, sources):
        dist = dict((s, 0) for s in sources)
        q = deque(sources)
        while q:
            c = q.popleft()
            for n in self.adj[c]:
                if n not in dist:
                    dist[n] = dist[c] + 1
                    q.append(n)
        for c in self.cells:
            dist.setdefault(c, INF)
        return dist

    def _pockets(self):
        """Depth of every cell inside a dead-end tree, and the tree's mouth."""
        degree = dict((c, len(self.adj[c])) for c in self.cells)
        pruned = set()
        q = deque(c for c in self.cells if degree[c] <= 1)
        while q:
            c = q.popleft()
            if c in pruned:
                continue
            pruned.add(c)
            for n in self.adj[c]:
                if n not in pruned:
                    degree[n] -= 1
                    if degree[n] <= 1:
                        q.append(n)
        depth, mouth = {}, {}
        q = deque()
        for c in self.cells:
            if c not in pruned:
                depth[c] = 0
                mouth[c] = c
                q.append(c)
        while q:
            c = q.popleft()
            for n in self.adj[c]:
                if n in pruned and n not in depth:
                    depth[n] = depth[c] + 1
                    mouth[n] = mouth[c]
                    q.append(n)
        for c in self.cells:
            if c not in depth:
                depth[c] = 0
                mouth[c] = c
        return depth, mouth


##############################################################################
# Team headquarters: shared tracking of the opponents                        #
##############################################################################

class Headquarters(object):

    def __init__(self, is_red, first_index, second_index):
        self.is_red = is_red
        self.members = [first_index, second_index]
        self.games_seen = 0
        self.board = None

    def setup(self, agent, gs):
        self.games_seen += 1
        if self.games_seen % 2 == 0:
            return
        self.board = Board(gs.get_walls(), self.is_red)
        self.enemies = list(agent.get_opponents(gs))
        self.n_agents = gs.get_num_agents()
        self.spawn = dict((e, gs.get_initial_agent_position(e)) for e in self.enemies)
        self.dist = dict((e, {self.spawn[e]: 1.0}) for e in self.enemies)
        self.fear = dict((e, 0) for e in self.enemies)
        self.seen = dict((e, None) for e in self.enemies)
        self.food_memory = set(agent.get_food_you_are_defending(gs).as_list())
        self.caps_memory = set(agent.get_capsules_you_are_defending(gs))
        self.their_caps = len(agent.get_capsules(gs))
        self.clock = 0
        self.bites = []          # (pos, clock) of our food eaten
        self.last_ghost_clock = -100
        self.mode = {}
        self.guard_post = {}
        self.plan = {}

    def partner(self, index):
        return self.members[1] if index == self.members[0] else self.members[0]

    # ------------------------------------------------------------- tracking
    def update(self, agent, gs):
        self.clock += 1
        me = agent.index
        here = gs.get_agent_position(me)
        buddy = gs.get_agent_position(self.partner(me))
        moved = (me - 1) % self.n_agents
        if moved in self.dist:
            self._spread(moved)
            if self.fear[moved] > 0:
                self.fear[moved] -= 1

        food_now = set(agent.get_food_you_are_defending(gs).as_list())
        caps_now = set(agent.get_capsules_you_are_defending(gs))
        lost = sorted((self.food_memory - food_now) | (self.caps_memory - caps_now))
        if lost:
            if moved in self.dist:
                self.dist[moved] = {lost[0]: 1.0}
            self.bites.append((lost[0], self.clock))
            self.bites = self.bites[-6:]
        self.food_memory = food_now
        self.caps_memory = caps_now

        n_caps = len(agent.get_capsules(gs))
        if n_caps < self.their_caps:
            for e in self.enemies:
                self.fear[e] = SCARED_TIME
        self.their_caps = n_caps

        noisy = gs.get_agent_distances()
        for e in self.enemies:
            pos = gs.get_agent_position(e)
            if pos is not None:
                st = gs.get_agent_state(e)
                self.dist[e] = {pos: 1.0}
                self.fear[e] = st.scared_timer
                self.seen[e] = (pos, self.clock, st.is_pacman)
                if not st.is_pacman and st.scared_timer == 0:
                    self.last_ghost_clock = self.clock
                continue
            r = noisy[e] if noisy else None
            kept = {}
            for c, p in self.dist[e].items():
                if manhattan(c, here) <= SIGHT or manhattan(c, buddy) <= SIGHT:
                    continue
                if r is not None and abs(manhattan(c, here) - r) > NOISE:
                    continue
                kept[c] = p
            if not kept:
                kept = self._restart(e, here, buddy, r)
            z = sum(kept.values())
            self.dist[e] = dict((c, p / z) for c, p in kept.items())

    def _restart(self, e, here, buddy, r):
        def fits(c):
            if manhattan(c, here) <= SIGHT or manhattan(c, buddy) <= SIGHT:
                return False
            return r is None or abs(manhattan(c, here) - r) <= NOISE
        self.seen[e] = None
        if fits(self.spawn[e]):
            self.fear[e] = 0
            return {self.spawn[e]: 1.0}
        pool = [c for c in self.board.cells if fits(c)] or list(self.board.cells)
        w = 1.0 / len(pool)
        return dict((c, w) for c in pool)

    def _spread(self, e):
        adj = self.board.adj
        out = {}
        for c, p in self.dist[e].items():
            ns = adj[c]
            w = p / (len(ns) + 1)
            out[c] = out.get(c, 0.0) + w
            for n in ns:
                out[n] = out.get(n, 0.0) + w
        self.dist[e] = out

    def mode_cell(self, e, region=None):
        best, bp = None, -1.0
        for c, p in self.dist[e].items():
            if region is not None and c not in region:
                continue
            if p > bp:
                best, bp = c, p
        return best

    def mass_in(self, e, region):
        return sum(p for c, p in self.dist[e].items() if c in region)

    def invaders(self, gs):
        out = []
        for e in self.enemies:
            pos = gs.get_agent_position(e)
            if pos is not None:
                st = gs.get_agent_state(e)
                if st.is_pacman:
                    out.append((e, pos, st.num_carrying))
        return out

    def hidden_invader_guess(self, gs):
        """Best guess of where an unseen invader is, or None."""
        if self.bites and self.clock - self.bites[-1][1] <= 10:
            return self.bites[-1][0]
        best, bm = None, 0.0
        for e in self.enemies:
            if gs.get_agent_position(e) is not None:
                continue
            mass = self.mass_in(e, self.board.ours)
            if mass > 0.55 and mass > bm:
                bm = mass
                best = self.mode_cell(e, self.board.ours)
        return best

    def threats(self, gs, here):
        """Enemy ghosts that can hurt a pacman: (pos, slack, scared)."""
        out = []
        for e in self.enemies:
            pos = gs.get_agent_position(e)
            if pos is not None:
                st = gs.get_agent_state(e)
                if not st.is_pacman:
                    out.append((pos, 0, st.scared_timer))
                continue
            s = self.seen[e]
            if s is None:
                continue
            spos, sclock, was_pac = s
            age = self.clock - sclock
            if was_pac or age > 8 or spos in self.board.ours:
                continue
            out.append((spos, (age + 1) // 2, self.fear[e]))
        return out

    # ------------------------------------------------------------- roles
    def decide_modes(self, agent, gs):
        left = gs.data.timeleft // 4
        lead = agent.get_score(gs)
        anchor, raider = self.members
        self.mode[anchor] = 'guard'
        self.mode[raider] = 'raid'
        if lead >= 1 and left <= 60:
            self.mode[raider] = 'guard'
        elif lead >= 8 and left <= 100:
            self.mode[raider] = 'guard'
        elif lead >= 18:
            self.mode[raider] = 'guard'
        elif lead <= 0 and left <= 90:
            self.mode[anchor] = 'raid'
        # if two invaders are on our side, the raider helps (if it is close to home)
        inv = self.invaders(gs)
        if len(inv) >= 2 and self.mode[raider] == 'raid':
            st = gs.get_agent_state(raider)
            if not st.is_pacman or st.num_carrying == 0:
                self.mode[raider] = 'guard'


##############################################################################
# Agent                                                                      #
##############################################################################

class FortressAgent(CaptureAgent):

    def __init__(self, index, hq, kind, time_for_computing=0.1):
        CaptureAgent.__init__(self, index, time_for_computing)
        self.hq = hq
        self.kind = kind
        self.rng = random.Random(4243 + 17 * index)
        self.trail = deque(maxlen=20)
        self.lane = None

    def register_initial_state(self, gs):
        CaptureAgent.register_initial_state(self, gs)
        self.hq.setup(self, gs)
        self.trail = deque(maxlen=20)
        self.lane = None

    def md(self, a, b):
        return self.distancer.get_distance(a, b)

    def choose_action(self, gs):
        self.t_start = time.perf_counter()
        legal = gs.get_legal_actions(self.index)
        self.hq.update(self, gs)
        self.hq.decide_modes(self, gs)
        act = self.pick(gs)
        if act is None or act not in legal:
            moves = [a for a in legal if a != Directions.STOP]
            act = self.rng.choice(moves) if moves else legal[0]
        return act

    def pick(self, gs):
        hq = self.hq
        me = self.index
        st = gs.get_agent_state(me)
        here = gs.get_agent_position(me)
        self.trail.append(here)
        # Any unscared ghost of ours snaps up an adjacent-ish invader.
        if not st.is_pacman and st.scared_timer == 0:
            near = [(self.md(here, p), p) for e, p, c in hq.invaders(gs)]
            near = [x for x in near if x[0] <= 2]
            if near:
                near.sort()
                if near[0][0] == 2 and self.circling() and self.rng.random() < 0.6:
                    return Directions.STOP
                return self.walk_home_side(here, near[0][1])
        if hq.mode[me] == 'guard':
            return self.guard(gs, here, st)
        return self.raid(gs, here, st)

    def circling(self):
        tail = list(self.trail)[-8:]
        return len(tail) >= 8 and len(set(tail)) <= 4

    # ================================================================ guard
    def guard(self, gs, here, st):
        hq = self.hq
        bd = hq.board
        if here not in bd.ours:
            return self.raid_home(gs, here, st)
        partner = hq.partner(self.index)
        partner_guards = hq.mode[partner] == 'guard'
        ppos = gs.get_agent_position(partner)
        inv = hq.invaders(gs)
        if inv:
            if partner_guards and len(inv) >= 2:
                inv.sort(key=lambda t: self.md(here, t[1]) - self.md(ppos, t[1]))
                target = inv[0]
            else:
                inv.sort(key=lambda t: (self.md(here, t[1]), -t[2]))
                target = inv[0]
            ipos = target[1]
            if st.scared_timer > 0:
                return self.keep_distance(here, ipos)
            if partner_guards and len(inv) == 1 and ppos in bd.ours and \
                    self.md(ppos, ipos) < self.md(here, ipos):
                # partner chases; we close the door it will run to
                return self.walk_home_side(here, self.exit_block(ipos))
            return self.walk_home_side(here, self.cut_off(gs, here, ipos, target[2]))
        guess = hq.hidden_invader_guess(gs)
        if guess is not None and guess in bd.ours:
            if partner_guards and ppos in bd.ours and self.md(ppos, guess) < self.md(here, guess):
                return self.walk_home_side(here, self.exit_block(guess))
            return self.walk_home_side(here, self.next_bite(gs, guess))
        return self.walk_home_side(here, self.post(gs, here, partner_guards, ppos))

    def keep_distance(self, here, ipos):
        bd = self.hq.board
        best = None
        for a, n in list(bd.steps[here]) + [(Directions.STOP, here)]:
            if n not in bd.ours:
                continue
            d = self.md(n, ipos)
            v = d - 100 if d <= 1 else -abs(d - 2) - 0.1 * bd.gate_dist[n]
            if best is None or v > best[0]:
                best = (v, a)
        return best[1] if best else Directions.STOP

    def exit_block(self, ipos):
        bd = self.hq.board
        if not bd.gates:
            return ipos
        return min(bd.gates, key=lambda g: self.md(ipos, g))

    def next_bite(self, gs, pos):
        """Where an invader last seen eating at pos will most likely go next."""
        foods = self.get_food_you_are_defending(gs).as_list()
        if not foods:
            return pos
        here = gs.get_agent_position(self.index)
        nxt = min(foods, key=lambda f: self.md(pos, f))
        if self.md(here, nxt) <= self.md(pos, nxt) + 2:
            return nxt
        return pos

    def cut_off(self, gs, here, ipos, carrying):
        bd = self.hq.board
        d_me = self.md(here, ipos)
        if d_me <= 3:
            return ipos
        # Trapped in a pocket: hold its mouth if we get there first.
        depth = bd.pocket_depth.get(ipos, 0)
        if depth > 0:
            mouth = bd.pocket_mouth[ipos]
            if mouth in bd.ours and self.md(here, mouth) <= self.md(ipos, mouth):
                return mouth
        if carrying <= 2:
            foods = self.get_food_you_are_defending(gs).as_list()
            foods.sort(key=lambda f: self.md(ipos, f))
            for f in foods[:2]:
                if self.md(here, f) < self.md(ipos, f):
                    return f
        if not bd.gates:
            return ipos
        gate = min(bd.gates, key=lambda g: self.md(ipos, g))
        dig = self.md(ipos, gate)
        best = None
        for c in bd.ours_list:
            dic = self.md(ipos, c)
            if dic > dig or dic + self.md(c, gate) != dig:
                continue
            if self.md(here, c) < dic and (best is None or dic < best[0]):
                best = (dic, c)
        return best[1] if best else ipos

    def post(self, gs, here, partner_guards, ppos):
        """Patrol point on our border facing the most dangerous enemy."""
        hq = self.hq
        bd = hq.board
        if not bd.gates:
            return here
        foods = self.get_food_you_are_defending(gs).as_list()
        looks = []
        for e in hq.enemies:
            c = hq.mode_cell(e)
            if c is not None:
                looks.append(c)
        scores = {}
        for g in bd.gates:
            de = min(self.md(g, c) for c in looks) if looks else 0
            df = 0.0
            if foods:
                near = sorted(self.md(g, f) for f in foods)[:4]
                df = sum(near) / float(len(near))
            v = de + 0.6 * df
            if partner_guards and ppos in bd.ours:
                post_p = hq.guard_post.get(hq.partner(self.index))
                if post_p is not None and self.md(g, post_p) < 6 and self.index != hq.members[0]:
                    v += 8
            scores[g] = v
        best = min(bd.gates, key=lambda g: scores[g])
        old = hq.guard_post.get(self.index)
        if old is not None and old in scores and scores[old] <= scores[best] + 3:
            best = old
        hq.guard_post[self.index] = best
        return best

    def walk_home_side(self, here, target):
        bd = self.hq.board
        if target is None or target == here:
            return Directions.STOP
        if here in bd.ours and target in bd.ours:
            first = {here: None}
            q = deque([here])
            while q:
                c = q.popleft()
                if c == target:
                    break
                for a, n in bd.steps[c]:
                    if n in first or n not in bd.ours:
                        continue
                    first[n] = a if first[c] is None else first[c]
                    q.append(n)
            if first.get(target) is not None:
                return first[target]
        best = None
        for a, n in bd.steps[here]:
            if here in bd.ours and n not in bd.ours:
                continue
            v = self.md(n, target)
            if best is None or v < best[0]:
                best = (v, a)
        return best[1] if best else Directions.STOP

    # ================================================================ raid
    def danger_costs(self, threats):
        bd = self.hq.board
        cost = {}
        live = [(g, s) for g, s, sc in threats if sc <= 3]
        if not live:
            return cost
        for c in bd.theirs_list:
            pen = 0.0
            for g, s in live:
                d = self.md(g, c) - s
                if d <= 1:
                    pen += 80.0
                elif d == 2:
                    pen += 25.0
                elif d == 3:
                    pen += 7.0
                elif d == 4:
                    pen += 2.0
            depth = bd.pocket_depth.get(c, 0)
            if depth > 0:
                mouth = bd.pocket_mouth[c]
                for g, s in live:
                    if self.md(g, mouth) - s <= 2 * depth + 3:
                        pen += 6.0 + 3.0 * depth
                        break
            if pen:
                cost[c] = pen
        return cost

    def dijkstra(self, here, extra):
        bd = self.hq.board
        dist = {here: 0.0}
        first = {here: None}
        heap = [(0.0, here)]
        done = set()
        while heap:
            d, c = heapq.heappop(heap)
            if c in done:
                continue
            done.add(c)
            for a, n in bd.steps[c]:
                nd = d + 1.0 + extra.get(n, 0.0)
                if nd < dist.get(n, INF):
                    dist[n] = nd
                    first[n] = a if first[c] is None else first[c]
                    heapq.heappush(heap, (nd, n))
        return dist, first

    def raid_home(self, gs, here, st):
        hq = self.hq
        threats = hq.threats(gs, here)
        near = [t for t in threats if t[2] <= 2 and self.md(t[0], here) - t[1] <= 5]
        if near:
            act = self.escape(gs, here, near, True)
            if act is not None:
                return act
        if not hq.board.gates:
            return None
        dist, first = self.dijkstra(here, self.danger_costs(threats))
        gate = min(hq.board.gates, key=lambda g: dist.get(g, INF))
        return first.get(gate)

    def raid(self, gs, here, st):
        hq = self.hq
        bd = hq.board
        foods = self.get_food(gs).as_list()
        caps = self.get_capsules(gs)
        carry = st.num_carrying
        left = gs.data.timeleft // 4
        home_d = bd.gate_dist[here]
        threats = hq.threats(gs, here)
        live = [t for t in threats if t[2] <= 2]
        radius = 4 if carry > 0 else 3
        near = [t for t in live if self.md(t[0], here) - t[1] <= radius]

        limit = 4
        if hq.clock - hq.last_ghost_clock > 24:
            limit = 6
        scared_left = min(hq.fear.values())
        if scared_left > home_d + 8:
            limit = 12
        must = carry > 0 and (len(foods) <= 2 or left <= home_d + 6)
        going_home = must or carry >= limit or (carry > 0 and near)

        if st.is_pacman and near:
            act = self.escape(gs, here, near, going_home)
            if act is not None:
                return act

        extra = self.danger_costs(threats)
        dist, first = self.dijkstra(here, extra)

        if going_home and here not in bd.ours:
            best = (INF, None)
            for g in bd.gates:
                v = dist.get(g, INF)
                if v < best[0]:
                    best = (v, g)
            if live and caps:
                for c in caps:
                    v = dist.get(c, INF) * 0.8
                    if v < best[0]:
                        best = (v, c)
            if best[1] is None:
                return None
            return first.get(best[1])

        # Use a capsule when a guard is around and it is close.
        if live and caps:
            for c in caps:
                if dist.get(c, INF) <= 6:
                    return first.get(c)

        # Hunt a scared ghost that is right next to us.
        for e in hq.enemies:
            p = gs.get_agent_position(e)
            if p is None or p in bd.ours:
                continue
            est = gs.get_agent_state(e)
            if not est.is_pacman and est.scared_timer > 4 and self.md(here, p) <= 2:
                return first.get(p)

        if not foods:
            return self.walk_home_side(here, self.post(gs, here, False, None)) if here in bd.ours else None

        stuck = len(self.trail) >= 16 and len(set(self.trail)) <= 4 and carry == 0
        if stuck and (self.lane is None or self.lane[1] < hq.clock):
            far = [g for g in bd.gates if self.md(g, here) >= 6]
            if far:
                self.lane = (self.rng.choice(far), hq.clock + 14)
        if self.lane is not None and self.lane[1] >= hq.clock and here in bd.ours and here != self.lane[0]:
            return self.walk_home_side(here, self.lane[0])

        w_home = 0.25 if carry == 0 else 0.6
        prev = hq.plan.get(self.index)
        best = None
        for f in foods:
            d = dist.get(f, INF)
            if d >= INF:
                continue
            v = d + w_home * bd.gate_dist[f]
            if f == prev:
                v -= 1.5
            if best is None or v < best[0]:
                best = (v, f)
        if best is None:
            return None
        hq.plan[self.index] = best[1]
        if best[0] > 60 and here in bd.ours:
            # everything is guarded: wait on our side near the safest gate
            return self.walk_home_side(here, self.post(gs, here, False, None))
        return first.get(best[1])

    # ------------------------------------------------------------- search
    def escape(self, gs, here, near, going_home):
        """Small alpha-beta search of us against the closest guards."""
        bd = self.hq.board
        ghosts = sorted(near, key=lambda t: self.md(t[0], here))[:2]
        gpos = tuple(g for g, s, sc in ghosts)
        foods = set(self.get_food(gs).as_list())
        caps = set(self.get_capsules(gs))
        carry = gs.get_agent_state(self.index).num_carrying
        self.recent_cells = set(list(self.trail)[-10:])
        self.search_aborted = False
        best_act = None
        depth = 1
        max_depth = 3 if len(gpos) == 1 else 2
        while depth <= max_depth:
            act, val = self.root_search(here, gpos, depth, foods, caps, carry, going_home)
            if self.search_aborted:
                break
            best_act = act
            if val <= -5000 and depth >= 2:
                pass
            depth += 1
        return best_act

    def root_search(self, here, gpos, depth, foods, caps, carry, going_home):
        bd = self.hq.board
        best_v, best_a = -INF, None
        options = list(bd.steps[here]) + [(Directions.STOP, here)]
        alpha = -INF
        for a, n in options:
            v = self.after_me(n, gpos, depth, 1, foods, caps, carry, going_home, (n,), alpha, INF)
            if a == Directions.STOP:
                v -= 3
            if n in self.recent_cells:
                v -= 4
            if v > best_v:
                best_v, best_a = v, a
            if v > alpha:
                alpha = v
            if self.search_aborted:
                break
        return best_a, best_v

    def after_me(self, me, gpos, depth, ply, foods, caps, carry, going_home, path, alpha, beta):
        bd = self.hq.board
        if me in bd.ours:
            return 5000.0 + 20 * carry - 10 * ply
        if me in gpos:
            return -10000.0 + ply
        if me in caps:
            return 3000.0 - 10 * ply
        return self.ghost_turn(me, gpos, 0, depth, ply, foods, caps, carry, going_home, path, alpha, beta)

    def ghost_turn(self, me, gpos, gi, depth, ply, foods, caps, carry, going_home, path, alpha, beta):
        if time.perf_counter() - self.t_start > SEARCH_BUDGET:
            self.search_aborted = True
            return 0.0
        bd = self.hq.board
        if gi >= len(gpos):
            if ply >= depth:
                return self.leaf(me, gpos, foods, carry, going_home, path)
            return self.my_turn(me, gpos, depth, ply + 1, foods, caps, carry, going_home, path, alpha, beta)
        g = gpos[gi]
        moves = [n for n in bd.adj[g] if n not in bd.ours] + [g]
        moves.sort(key=lambda n: self.md(n, me))
        v = INF
        for n in moves:
            if n == me:
                return -10000.0 + ply
            ng = gpos[:gi] + (n,) + gpos[gi + 1:]
            r = self.ghost_turn(me, ng, gi + 1, depth, ply, foods, caps, carry, going_home, path, alpha, beta)
            if r < v:
                v = r
            if v < beta:
                beta = v
            if alpha >= beta or self.search_aborted:
                break
        return v

    def my_turn(self, me, gpos, depth, ply, foods, caps, carry, going_home, path, alpha, beta):
        bd = self.hq.board
        v = -INF
        for a, n in list(bd.steps[me]) + [(Directions.STOP, me)]:
            r = self.after_me(n, gpos, depth, ply, foods, caps, carry, going_home, path + (n,), alpha, beta)
            if r > v:
                v = r
            if v > alpha:
                alpha = v
            if alpha >= beta or self.search_aborted:
                break
        return v

    def leaf(self, me, gpos, foods, carry, going_home, path):
        bd = self.hq.board
        gd = min(self.md(g, me) for g in gpos)
        v = 6.0 * min(gd, 6)
        v -= 8.0 * bd.pocket_depth.get(me, 0)
        if me in self.recent_cells:
            v -= 3.0
        eaten = len(set(path) & foods)
        if going_home:
            v -= 4.0 * bd.gate_dist[me]
        else:
            v += 12.0 * eaten
            if foods:
                v -= 1.0 * min(self.md(me, f) for f in foods)
            v -= 1.5 * bd.gate_dist[me]
        return v
