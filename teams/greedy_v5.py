# greedy_v5.py
# ------------
# 2026-11-08: candidate for validation V3 (docs/experiments.md E-038), user request.
# = teams/greedy_v4.py with ONE default changed: plan='override' instead of 'danger' (league entry
# `lab7_netf_override`, E-034: +0.06 [+0.00, +0.12] vs greedy_v4 over 1,440 tuning games). Greedy decides
# every move; near a non-scared ghost the width planner (same search, same learned leaf) runs and replaces
# greedy's move only when its best root value beats the value of greedy's own move by plan_margin = 0.3.
# Do not edit; new versions get new files.
#
# greedy_v4 header follows (its validation numbers are greedy_v4's, not this file's):
# Submission candidate promoted 2026-11-08 (user decision; docs/experiments.md E-031/E-032).
# = teams/greedy_lab_v7.py with the `lab7_danger_netf` options as DEFAULTS, so the tournament (which
# passes no create_team arguments) plays exactly the validated configuration:
#   lab5_smart (flags, shared belief, endgame roles, directed belief, open_goal) +
#   width-based planner (IW(1) over (cell, carried) atoms, planner v2) for the attacker while a
#   non-scared enemy ghost is modelled within 7 maze steps, with a learned leaf value (LEAF_NET,
#   12-16-1 tanh MLP, fast code path 'netf'), 2000-node cap per search, 0.3 s clock safety net.
# Validation (E-031 V1, seeds 221-260): +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs
# lab5_smart. Do not edit; new versions get new files.
#
# lab7 header follows.
# greedy_lab_v7.py
# ----------------
# 2026-11-08: greedy_lab_v6.py frozen (E-028/E-029 runs); v7 = v6 + the options below (all default
# off, so `lab7_off` must play exactly like lab6_off = lab5_smart). Advisor review, E-030:
#   plan_nodes='0'   node cap per search (deterministic; the clock budget stays as a safety net)
#   plan_kill='1', plan_cap='0.3'   planner rewards for eating a scared ghost / a capsule (were constants)
#   plan_hidden      '1'/'argmax' (v6 behaviour) | '0' off | 'near' (hidden ghost on the belief cell with
#                    mass >= 0.05 nearest to us: pessimistic) | 'both' (plan with argmax and near, min)
#   plan='shield'    greedy decides; the planner only vetoes: its best move replaces greedy's when greedy's
#                    root value < -0.5*plan_death and the best beats it by plan_margin
#   hunt_scared='0'  greedy rule without planner: chase a visible scared enemy ghost within hunt_d steps
#                    whose scared time exceeds our distance + 1
#   formation='power' SM-3: the home defender attacks while no enemy is a Pacman and the enemies stay
#                    scared long enough for a trip (or one respawned within the last 10 own moves)
#   dplan='0'        defender planner: IW(1) over (our defender cell, invader cell) atoms against a
#                    modelled invader (forages to the nearest food; flees home when carrying >= dplan_ret
#                    or when we are within 3); overrides the rule defender's move by dplan_margin
#
# v6 header follows.
# greedy_lab_v6.py
# ----------------
# Experiment file (docs/experiments.md E-027..): teams/greedy_lab_v5.py with lab5_smart's switches
# (flags, shared, endgame, directed, open_goal) as DEFAULTS, plus new switches, all OFF by default,
# so that the defaults play exactly like lab5_smart (identity check `lab6_off`).
# New switches (2026-11-08, overnight session):
#   plan='0'       width-based planning (IW(1) / novelty-pruned best-first search, docs/research/
#                  width_planning.md) over our own lightweight model of the attacker's world:
#                  'full'   = planner decides the attacker's move whenever it finds a plan worth > plan_min
#                  'danger' = only while a modelled enemy ghost is within plan_trigger maze steps
#                  'food'   = only instead of the food-target choice (greedy keeps all go-home rules)
#   plan_search='iw' ('iw' breadth-first IW(1) | 'best' best-first by value, novelty-pruned)
#   plan_atoms='pos_carry' ('pos' | 'pos_carry' | 'pos_food' | 'pos_carry_g')
#   plan_h, plan_r, plan_death, plan_a, plan_min, plan_hidden, plan_budget, plan_trigger: see Config
#   focus='none'   food-region mode for the attacker's target choice (map modes):
#                  top | bottom (in our own frame: blue's y is flipped, so a map gives both colours the
#                  same view) | deep | shallow | cluster | far (from the enemy ghosts' belief cells) |
#                  majority (the half holding more enemy food) | auto (map-feature selector)
#   focus_w='3'    weight of the focus penalty, in maze steps
# Self-contained (stdlib + contest framework only). Do not edit after it has been benchmarked;
# copy to greedy_lab_v7.py instead.
#
# lab5 header follows.
# Experiment file (docs/experiments.md E-025): teams/greedy_v3.py plus enemy-state switches.
# Research behind each switch: docs/heuristics.md Part D.
#
# Switches (create_team kwargs; defaults = greedy_v3's tournament configuration + new ones off):
#   breaker='1', intercept='1', return_at='8', shadow='1'   greedy_v3 (E-011..E-021)
#   roles='0', tracker='0', adaptive='0'   screened in E-007/E-010, not adopted
#   hunt='0'       P-22: the defender chases the most likely cell of a hidden enemy on our side
#                     (belief mass >= 0.5; with flags: the enemy's is_pacman)
#   flags='0'      #1 H-S14: read hidden enemies' is_pacman / num_carrying / scared_timer /
#                     num_returned (rules.md Q3: allowed) for the belief's side constraint, food
#                     attribution, respawns, the raider and exact scared timers
#   shared='0'     #3 H-S15: one team belief updated at both agents' turns (rules.md Q4)
#   endgame='0'    #4 H-S27/P-17c: last ENDGAME_MOVES own moves: ahead -> both defend, behind ->
#                     both attack and bank as soon as a trip would take the lead
#   directed='0'   H-S17 (needs flags): goal-directed motion model in the belief
#   open_goal='0'  H-S24 (needs flags): ignore return_at while no enemy can reach us before home
#   guard='0'      H-S16 (needs flags): the defender targets hidden invaders by their likely goal
#   recall='0'     H-S26 (needs flags): with two enemy Pacmen the attacker defends too
#
# Rules this file follows (docs/rules.md): public API only, no mutation of observation objects,
# own RNG instance. Hidden opponents' AgentState fields are read only in V1Agent.fields(), behind
# USE_HIDDEN_OPPONENT_FLAGS and the `flags` switch (Q3); with both off nothing hidden is read.

import heapq
import math
import random
import time
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

# Rules.md Q3 (answered 2026-10-22: allowed, recommended): the one switch for reading hidden
# opponents' AgentState fields. False turns every use off, whatever the `flags` option says.
USE_HIDDEN_OPPONENT_FLAGS = True
DIRECT_BONUS = 2.0        # directed: extra weight of a step towards the enemy's goal (others weigh 1)
ENEMY_RETURN_DEFAULT = 5  # directed/guard: food an enemy carries before it heads home, until seen banking
OPEN_MARGIN = 4           # open_goal: spare moves between the earliest enemy arrival and our way home
OPEN_QUANTILE = 0.1       # open_goal: pessimistic quantile of an enemy's distance under its belief
RECALL_HOME = 3           # recall: an empty-handed attacker this close to home comes back to defend


def _flag(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    """Experiment switches; one read-only object per team."""

    def __init__(self, roles='0', breaker='0', tracker='0', intercept='0', return_at=RETURN_AT,
                 adaptive='0', hunt='0', shadow='0', flags='0', shared='0', endgame='0',
                 directed='0', open_goal='0', guard='0', recall='0', **extra):
        self.roles = _flag(roles)
        self.breaker = _flag(breaker)
        self.tracker = _flag(tracker)
        self.intercept = _flag(intercept)
        self.return_at = int(return_at)
        self.adaptive = _flag(adaptive)
        self.hunt = _flag(hunt)
        self.shadow = _flag(shadow)
        self.flags = _flag(flags) and USE_HIDDEN_OPPONENT_FLAGS
        self.shared = _flag(shared)
        self.endgame = _flag(endgame)
        # the next four read the enemies' fields and do nothing without them
        self.directed = _flag(directed) and self.flags
        self.open_goal = _flag(open_goal) and self.flags
        self.guard = _flag(guard) and self.flags
        self.recall = _flag(recall) and self.flags
        # --- lab6 switches (defaults = off) ---
        e = dict(V6_DEFAULTS)
        for k, v in extra.items():
            if k not in e:
                raise ValueError('unknown lab6 option %r' % k)
            e[k] = v
        self.plan = str(e['plan']).strip().lower()
        if self.plan in ('', '0', 'none', 'off', 'false'):
            self.plan = None
        self.plan_search = str(e['plan_search'])
        self.plan_atoms = str(e['plan_atoms'])
        self.plan_h = int(e['plan_h'])
        self.plan_r = int(e['plan_r'])
        self.plan_death = float(e['plan_death'])
        self.plan_a = float(e['plan_a'])
        self.plan_min = float(e['plan_min'])
        hidden = str(e['plan_hidden']).strip().lower()
        if hidden in ('1', 'true', 'yes', 'on', 'argmax'):
            hidden = 'argmax'
        elif hidden in ('0', 'false', 'no', 'off', 'none', ''):
            hidden = None
        self.plan_hidden = hidden
        self.plan_nodes = int(e['plan_nodes'])
        self.plan_kill = float(e['plan_kill'])
        self.plan_cap = float(e['plan_cap'])
        self.hunt_scared = _flag(e['hunt_scared'])
        self.hunt_d = int(e['hunt_d'])
        self.dplan = _flag(e['dplan'])
        self.dplan_ret = int(e['dplan_ret'])
        self.dplan_margin = float(e['dplan_margin'])
        self.dplan_h = int(e['dplan_h'])
        self.dplan_nodes = int(e['dplan_nodes'])
        self.plan_budget = float(e['plan_budget'])
        self.plan_trigger = int(e['plan_trigger'])
        self.plan_gamma = float(e['plan_gamma'])
        self.plan_v = int(e['plan_v'])
        self.plan_novelty = str(e['plan_novelty'])
        self.plan_models = str(e['plan_models'])
        self.plan_leaf = str(e['plan_leaf'])
        self.plan_margin = float(e['plan_margin'])
        self.focus = str(e['focus']).strip().lower()
        self.focus_w = float(e['focus_w'])
        self.formation = str(e['formation']).strip().lower()
        self.form_lead = int(e['form_lead'])
        for k in ('fw_top', 'fw_depth', 'fw_cluster', 'fw_ghost', 'fw_deadend', 'fw_capsule', 'fw_mate'):
            setattr(self, k, float(e[k]))
        self.threat_dist = int(e['threat_dist'])
        self.open_margin = int(e['open_margin'])
        self.standoff_moves = int(e['standoff_moves'])


V6_DEFAULTS = {
    'plan': 'override', 'plan_search': 'iw', 'plan_atoms': 'pos_carry', 'plan_h': '30', 'plan_r': '6',
    'plan_death': '3', 'plan_a': '0.5', 'plan_min': '0.05', 'plan_hidden': '1',
    'plan_budget': '0.3', 'plan_trigger': '7', 'plan_gamma': '0.97',
    # plan_v='2': atoms only for surviving states, Stop generated; plan='override': greedy decides,
    # the planner overrides only if its best root value beats greedy's action by plan_margin
    'plan_v': '2', 'plan_margin': '0.3',
    # v3 options: 'piw' reward-aware novelty (p-IW); 'm1m2' chase + intercept ghost models, min over
    # root values; 'net' learned leaf value (LEAF_NET, trained offline on lab6 games)
    'plan_novelty': 'iw', 'plan_models': 'm1', 'plan_leaf': 'netf',
    # v7 options (see header)
    'plan_nodes': '2000', 'plan_kill': '1', 'plan_cap': '0.3', 'hunt_scared': '0', 'hunt_d': '10',
    'dplan': '0', 'dplan_ret': '5', 'dplan_margin': '0.3', 'dplan_h': '20', 'dplan_nodes': '3000',
    'focus': 'none', 'focus_w': '3',
    # focus='linear': learned food-choice weights (maze steps per unit feature)
    'fw_top': '0', 'fw_depth': '0', 'fw_cluster': '0', 'fw_ghost': '0', 'fw_deadend': '0',
    'fw_capsule': '0', 'fw_mate': '0',
    # formation='lead': the home defender attacks too while our score <= form_lead
    'formation': 'none', 'form_lead': '0',
    # lab5 module constants exposed for tuning (defaults = lab5 values)
    'threat_dist': str(THREAT_DIST), 'open_margin': str(OPEN_MARGIN),
    'standoff_moves': str(STANDOFF_MOVES),
}


# Map-mode selector for focus='auto': predicted gain (points per game over focus 'none') of each
# focus mode as a linear function of map_features(); the mode with the largest positive prediction
# is played, else 'none'. Empty until trained offline from a mode x map table (E-0xx).
FOCUS_MODELS = {}


def select_focus(feats):
    best, best_v = 'none', 0.0
    for mode in sorted(FOCUS_MODELS):
        bias, weights = FOCUS_MODELS[mode]
        v = bias + sum(w * feats.get(k, 0.0) for k, w in weights.items())
        if v > best_v:
            best, best_v = mode, v
    return best


def create_team(first_index, second_index, is_red,
                first='GreedyAttacker', second='PatrolDefender', roles='0', breaker='1',
                tracker='0', intercept='1', return_at='8', adaptive='0', hunt='0', shadow='1',
                flags='1', shared='1', endgame='1', directed='1', open_goal='1', guard='0',
                recall='0', num_training=0, **extra):
    cfg = Config(roles, breaker, tracker, intercept, return_at, adaptive, hunt, shadow,
                 flags, shared, endgame, directed, open_goal, guard, recall, **extra)
    memory = TeamMemory() if cfg.shared else None
    if cfg.roles:
        return [FlexAgent(first_index, cfg, 'attack'), FlexAgent(second_index, cfg, 'defend')]
    if cfg.endgame or cfg.recall:
        home_roles = {first_index: 'attack', second_index: 'defend'}
        return [RoleAgent(first_index, cfg, home_roles, memory),
                RoleAgent(second_index, cfg, home_roles, memory)]
    classes = {
        'GreedyAttacker': GreedyAttacker,
        'DeadEndAttacker': DeadEndAttacker,
        'PatrolDefender': PatrolDefender,
    }
    return [classes[first](first_index, cfg, memory), classes[second](second_index, cfg, memory)]


#################################
# lab6: width-based planner     #
#################################
# IW(1) (Lipovetzky & Geffner 2012) as used with simulators (Lipovetzky, Ramirez & Geffner 2015):
# breadth-first search that keeps a generated node only if it makes some atom true for the first
# time; the root action leading to the best-valued node is played. Our own model of the world
# (never the engine's objects): we move, then every modelled enemy ghost moves once:
#   scared  -> the step that maximises its maze distance to us (on its own side)
#   within plan_r of us -> the step that minimises it (on its own side)
#   else    -> stays (a guard on its post)
# Rewards (potential-style): eat +a, bank k food +k(1-a), death -(a*carried + D), eat a scared ghost
# +KILL, capsule +CAP. Node value = discounted reward + discounted leaf value of the carried food.

PLAN_KILL = 1.0
# plan_leaf='net': (W1 [hidden x 12], b1 [hidden], w2 [hidden], b2) of a 12-tanh-1 MLP predicting the
# food this agent banks minus the food it drops over its next 30 moves (trained offline, E-0xx).
# LEAF_NET_BEGIN
# trained by eval/rl/train_value.py on ['d1_lab6off']; test R2 0.464
LEAF_NET = (
    [[1.32101, 2.44586, 0.86889, -0.29104, -2.81819, 0.96851, 0.49415, 1.13925, 0.53717, -0.20696, 0.04484, 1.21986], [-0.27074, -1.43661, -0.13986, 0.08978, 2.81361, -0.54451, -0.254, -0.79726, -0.49688, 0.6469, -0.39889, 1.11399], [-2.10427, 2.33223, 0.92188, 0.3731, -2.7516, -0.45214, 0.64482, 1.18553, 0.74694, 0.13941, -0.68772, -0.95093], [-1.69754, 2.61436, 1.14851, 0.23447, -0.52276, -0.44927, 0.55034, -0.56698, 0.20881, -0.39489, 0.33326, 2.18693], [0.11116, 0.85167, 2.02005, 0.37439, 2.621, -0.69047, 1.65564, -0.31342, 0.84534, -0.56327, -0.59945, -1.96562], [1.80825, -2.02901, -1.20897, -0.10648, 0.05602, -0.0271, -1.15729, 0.00326, -0.55838, 0.38978, 0.30212, -1.88308], [1.95352, -1.73518, -0.90018, 0.15184, 0.47712, -0.23993, -1.32532, -0.47439, -1.53241, 0.4056, 0.68611, -0.65947], [1.61857, -2.25766, -1.2592, -0.06198, 0.79237, 0.18502, -0.99584, 0.76809, -0.18301, 0.62443, -0.36438, -2.14615], [-0.1812, -1.31417, -1.32502, 0.13609, 1.12467, 0.06889, -0.38067, 0.54522, -0.85376, 0.14584, -1.0772, 1.65458], [-1.8718, -0.91826, -1.54561, 0.24066, 0.08432, 0.57079, -0.02149, -0.103, -0.90957, 0.71189, 0.08456, 1.27184], [2.13781, 2.21829, 0.10515, 0.08248, -2.69719, 0.02909, 0.20773, 0.21289, 0.88612, -0.74334, 0.38019, 1.21857], [-1.25489, -1.68065, -0.42628, -0.18559, 1.95637, -0.55278, -0.00211, -0.61593, -0.23004, 0.27971, 0.58309, -1.15548], [-2.22016, 0.93747, 0.67882, 0.58179, -1.1253, -0.42522, 0.3706, 0.33103, 0.66698, 0.97715, -0.44853, -1.65185], [0.22681, -2.01006, -1.19726, 0.28723, 1.71138, -0.25907, -0.43861, 0.31493, -0.81374, 0.66594, 0.24681, -1.81535], [-2.36152, -0.93694, 0.83781, 0.59869, 4.04424, 0.24077, 1.26568, -0.05573, -0.36222, 0.01818, -0.18522, -0.61962], [1.06701, 1.60631, 1.33244, 0.0114, -1.10698, 0.32834, 0.36579, 0.06181, 0.34156, -0.1283, -0.70976, 0.36089]],
    [-0.16928, 0.31331, 0.24412, 0.23387, -0.16334, -0.38023, -0.61583, -0.31157, 0.25854, 0.4277, -0.3242, -0.37714, 0.41366, 0.56288, 0.47221, 0.10559],
    [2.1698, 1.74129, -1.44691, -1.51826, 1.7987, 1.46688, 1.52291, 1.564, -1.19931, -1.38286, 2.02773, -1.65537, -1.46316, 2.4537, 2.3987, 0.75911],
    0.05979)
# LEAF_NET_END
# plan_leaf=net2f: second iteration, trained on lab6_off + lab7_danger_net games (E-031)
# LEAF_NET2_BEGIN
# trained by eval/rl/train_value.py on ['d1_lab6off', 'd2_net']; test R2 0.588
LEAF_NET2 = (
    [[1.74558, 2.95369, 0.71134, -0.68654, -2.65612, 0.40943, 0.53254, 1.31184, 0.33937, -0.56305, 0.3797, 1.35364], [0.62108, 0.96382, 0.01758, 0.32913, 0.37102, -0.92738, 0.63971, -2.07803, 1.36055, 0.70519, 0.03177, -1.37602], [-2.49432, 2.4281, 0.28009, 0.28245, -3.89075, -1.00096, 0.64613, 0.44603, 1.49839, 0.09666, 0.47181, -1.11129], [-1.93731, 3.50777, 1.11705, -0.00089, -1.58588, 0.02659, 1.02909, 0.79586, 0.90272, -0.90609, -0.14564, 0.15235], [-0.10775, 0.92237, 3.00918, 0.18713, 1.69993, -0.84769, 0.81799, -0.87941, 1.08975, -0.35783, -0.35541, -2.91966], [1.37837, 0.5026, -3.61077, -0.12204, -1.15748, -0.92475, -1.15687, 0.17818, 0.68637, 0.12526, 0.85319, -4.83301], [1.53617, -2.04827, -2.10999, -0.13865, -1.41299, 0.33349, -0.0832, -0.30739, -0.65277, 0.42956, 0.27217, -3.12703], [1.52077, -1.96125, -2.11771, -0.06063, 0.56657, 0.20496, -1.74788, 1.04538, 1.09659, 0.57684, -0.72564, -0.47941], [1.84162, -2.36327, -1.01309, 0.26136, 0.86065, -0.05132, -0.95863, -0.04459, 0.55687, 0.19581, -5.12096, 3.81948], [-3.50732, 2.03461, -1.46666, -0.09925, -1.46416, 1.46048, 0.71815, -0.17386, -0.86999, 0.27977, 0.29858, 0.93153], [0.88728, 1.88674, -0.35298, 0.29278, -3.63349, 1.83937, -0.16406, 0.86352, -0.11538, -0.26272, 0.78254, -0.24255], [-1.7283, -1.75348, -0.26464, -0.02534, 2.10496, 0.05418, -0.05459, -0.10042, -0.54821, 0.75135, -0.01171, -1.55998], [-1.7321, 0.30683, 0.64871, 0.37461, -0.54212, -0.7298, -0.10259, 0.18642, 0.76909, 1.11565, -0.42124, -0.68177], [-0.03866, -2.55657, -1.33872, 0.46544, 2.59528, -0.06528, -0.5381, 0.13511, -0.62232, 0.9079, -0.1363, -1.39968], [-2.0477, -0.83227, 0.73664, 0.55672, 2.95678, 0.04647, 1.07961, -0.63527, -0.3876, -0.3858, 0.06376, 0.03075], [2.38483, 1.89179, 1.11415, 0.08437, -3.00106, 0.44978, 0.76258, 0.24785, -0.06422, 0.407, -0.64929, 1.50741]],
    [-0.49258, 0.31615, 0.92252, 0.07345, -0.13152, -0.79782, -0.88982, -0.54569, -0.46958, 0.36916, 0.25889, -0.04402, 0.70814, 0.72394, 0.4288, 0.42595],
    [2.54592, 0.37538, -2.19298, -2.16058, 2.18291, 2.48129, 1.94853, 1.8785, -3.27593, -1.70335, 2.56314, -1.87033, -1.49309, 3.10287, 2.61079, 1.61715],
    -0.24408)
# LEAF_NET2_END
# plan_leaf=net3f: second iteration, trained on lab7_danger_net games only (on-policy, E-031)
# LEAF_NET3_BEGIN
# trained by eval/rl/train_value.py on ['d2_net']; test R2 0.552
LEAF_NET3 = (
    [[1.90855, 1.40222, -0.10109, -0.06676, -2.74097, 1.20414, 0.89255, 1.21479, 0.28168, -0.25949, -0.11982, 2.04071], [0.49195, 0.57212, 0.29803, 0.52252, 0.71164, 0.54072, 0.66603, -0.14284, 0.38043, 0.61796, 0.27667, 0.37335], [-2.76994, 2.36626, 1.54083, 0.34794, -2.68552, -0.82362, 1.67694, 0.46312, -0.56847, 0.08055, 0.69468, -0.3717], [-1.68791, 2.89659, 0.82193, 0.2307, -2.06422, -0.32242, 0.51035, 0.37593, -0.08518, -0.63482, 0.61259, 0.01187], [0.85025, 0.61106, 2.14536, 0.38292, -1.00382, -0.38622, 0.44171, -0.11757, 0.6981, -0.84438, -0.21016, -1.93152], [1.54389, 0.28038, -2.92582, -0.15776, -0.44051, -0.61568, -1.70619, 0.06284, 0.41738, 0.24911, 0.72335, -2.54442], [1.44268, -0.84411, -2.18581, -0.0813, -0.21025, -0.05291, -0.37329, -0.3827, -0.29325, 0.43908, 0.98542, -2.93535], [1.81551, -2.0855, -1.69056, -0.0695, 1.8484, -0.22177, -1.15607, -0.39049, 0.50977, 0.69351, -0.06111, -0.42447], [0.73342, -1.53561, -0.59299, 0.02444, 1.35153, 0.26304, 0.28001, -0.12824, 0.37405, -0.0266, -3.13478, 2.10776], [-1.16199, 1.03059, -0.18485, -0.19924, -2.20198, 1.05121, -0.10609, -0.68657, -0.35495, -0.51153, 0.44444, 1.44205], [1.16004, 1.27973, 0.41424, 0.39033, -2.72933, 0.87004, 0.57437, 0.39839, -0.14222, -0.09315, 0.42432, 1.36503], [-2.03933, -1.60775, -0.36791, 0.02591, 1.6436, -0.0675, 0.12916, -0.60803, 0.01465, 0.21279, 0.56708, -0.75001], [-1.33816, 1.43609, 0.07937, 0.5174, -1.46272, -0.74431, 0.04445, 0.30759, 0.07919, 0.75514, -0.57969, -0.52627], [0.31538, -2.20102, -1.23469, 0.12489, 1.75184, 0.2546, -0.45742, 0.63413, 0.14697, 0.48379, 0.0074, -0.81157], [-1.50447, -0.70027, 0.74116, 0.31834, 3.03824, -0.29959, 1.26626, -0.67385, -0.55778, -0.34349, 0.7174, -0.30258], [1.36871, 2.97167, 1.41405, -0.19024, -2.1909, -0.76212, -0.03375, 0.78583, -0.7046, -0.17409, 0.28689, 1.76146]],
    [-0.03538, 0.75389, 0.83216, 0.21123, -0.32781, -0.9317, -1.02055, -0.54957, -0.30287, -0.10798, 0.16295, -0.20532, 0.33512, 0.54571, 0.30825, -0.04175],
    [1.99054, 0.66172, -1.61458, -1.83377, 1.75924, 1.93503, 1.54345, 1.75573, -1.75513, -1.31771, 1.64663, -1.60561, -1.01439, 2.23548, 2.12309, 1.48601],
    0.13256)
# LEAF_NET3_END
PLAN_CAPSULE = 0.3
PLAN_FOOD_SHAPE = 0.02
PLAN_CARRY_BUCKET = (0, 1, 2, 3, 4, 4, 5, 5, 5, 6, 6, 6, 6)


def _carry_bucket(c):
    return PLAN_CARRY_BUCKET[c] if c < 13 else 7


class WidthModel:
    """Static part of the planner's model, built once per game from MapInfo (index form)."""

    def __init__(self, mapinfo):
        cells = list(mapinfo.cells)
        index = dict((c, k) for k, c in enumerate(cells))
        self.cells = cells
        self.index = index
        n = len(cells)
        self.n = n
        nbr = []
        for c in cells:
            lst = []
            for nc in mapinfo.nbrs[c]:
                lst.append((Actions.vector_to_direction((nc[0] - c[0], nc[1] - c[1])), index[nc]))
            nbr.append(tuple(lst))
        self.nbr = nbr
        self.home = [mapinfo.is_ours(c) for c in cells]
        dist = []
        for c in cells:
            row = mapinfo.dist[c]
            dist.append([row.get(c2, INF) for c2 in cells])
        self.dist = dist
        self.dhome = [mapinfo.dist_home[c] for c in cells]
        self.gnbr = [tuple(j for _, j in nbr[i] if not self.home[j]) for i in range(n)]
        self.denemy = [mapinfo.dist_enemy_side[c] for c in cells]
        self.hnbr = [tuple((a, j) for a, j in nbr[i] if self.home[j]) for i in range(n)]
        self.depthv = [min(mapinfo.depth.get(c, 0), 10) / 10.0 for c in cells]
        # intercept target (ghost model M2): the enemy cell across our nearest home-border cell
        icept = []
        for c in cells:
            row = mapinfo.dist[c]
            if mapinfo.home_border:
                b = min(mapinfo.home_border, key=lambda bb: (row.get(bb, INF), bb))
                icept.append(index[mapinfo.cross[b]])
            else:
                icept.append(index[c])
        self.icept = icept


class WidthPlanner:
    def __init__(self, model, cfg):
        self.m = model
        self.cfg = cfg

    def plan(self, me, carried, food, capsules, ghosts, steps_left, budget_s):
        """me: (x, y); food/capsules: (x, y) lists on the enemy side; ghosts: [((x, y), scared)] for
        the modelled enemy ghosts. Returns (action or None, info dict).
        plan_models='m1m2': one search per ghost model (M1 chase-in-range, M2 intercept), root values
        aggregated by min (robust to the model), best root action by that min."""
        return self.plan_multi(me, carried, food, capsules, ghosts, steps_left, budget_s, None)

    def plan_multi(self, me, carried, food, capsules, ghosts, steps_left, budget_s, alt_ghosts):
        """v7: one search per scenario (ghost model M1 / M2, ghost placement argmax / near), root values
        aggregated by min, best root action by that min."""
        scen = [(ghosts, False)]
        if self.cfg.plan_models == 'm1m2' and ghosts:
            scen.append((ghosts, True))
        if alt_ghosts is not None and sorted(alt_ghosts) != sorted(ghosts):
            scen.append((alt_ghosts, False))
        if len(scen) == 1:
            return self._search(me, carried, food, capsules, ghosts, steps_left, budget_s, False)
        res = [self._search(me, carried, food, capsules, g, steps_left, budget_s / len(scen), m2)
               for g, m2 in scen]
        agg = dict(res[0][1]['root_values'])
        for _, inf in res[1:]:
            rv = inf['root_values']
            agg = dict((a, min(v, rv[a])) for a, v in agg.items() if a in rv)
        if not agg:
            return res[0]
        best = max(sorted(agg), key=lambda a: agg[a])
        info = {'expanded': sum(r[1]['expanded'] for r in res),
                'timed_out': any(r[1]['timed_out'] for r in res),
                'best_value': agg[best], 'time': sum(r[1]['time'] for r in res), 'root_values': agg}
        return best, info

    def _search(self, me, carried, food, capsules, ghosts, steps_left, budget_s, m2):
        t0 = time.perf_counter()
        m = self.m
        cfg = self.cfg
        idx = m.index
        dist = m.dist
        home = m.home
        dhome = m.dhome
        nbr = m.nbr
        gnbr = m.gnbr
        a = cfg.plan_a
        ret = 1.0 - a
        death = cfg.plan_death
        chase_r = cfg.plan_r
        gamma = cfg.plan_gamma
        horizon = min(cfg.plan_h, max(1, steps_left))
        atoms_kind = cfg.plan_atoms
        best_first = cfg.plan_search == 'best'
        v2 = cfg.plan_v >= 2
        root_best = {}
        piw = cfg.plan_novelty == 'piw'
        killv = cfg.plan_kill
        capv = cfg.plan_cap
        node_cap = cfg.plan_nodes
        icept = m.icept
        net = {'net': LEAF_NET, 'netf': LEAF_NET, 'net2f': LEAF_NET2,
               'net3f': LEAF_NET3}.get(cfg.plan_leaf)
        fast = cfg.plan_leaf in ('netf', 'net2f', 'net3f')
        if fast:
            # static part of the first layer per cell (dist_home, side, dead-end depth), once per game
            cache = getattr(m, 'net_static', None)
            if cache is None:
                cache = m.net_static = {}
            stat = cache.get(cfg.plan_leaf)
            if stat is None:
                w1, b1, _, _ = net
                stat = []
                for k in range(m.n):
                    xd = min(m.dhome[k], 40) / 40.0
                    xp = 0.0 if m.home[k] else 1.0
                    xs = m.depthv[k]
                    stat.append([bb + wr[1] * xd + wr[9] * xp + wr[11] * xs for wr, bb in zip(w1, b1)])
                cache[cfg.plan_leaf] = stat
            dyn_w = [(wr[0], wr[2], wr[3], wr[4], wr[5], wr[6], wr[7], wr[8], wr[10]) for wr in net[0]]
            w2n = net[2]
            b2n = net[3]
            tanh = math.tanh
        depthv = m.depthv
        cap_cells = [idx[c] for c in capsules]

        s0 = idx[me]
        fbit = {}
        for k, f in enumerate(food):
            fbit[idx[f]] = 1 << k
        cbit = {}
        for k, c in enumerate(capsules):
            cbit[idx[c]] = 1 << k
        fcells = list(fbit.keys())
        g0 = tuple(idx[g] for g, _ in ghosts)
        sc0 = tuple(int(s) for _, s in ghosts)
        ng = len(g0)

        n_cell = [s0]
        n_carry = [carried]
        n_food = [(1 << len(food)) - 1]
        n_cap = [(1 << len(capsules)) - 1]
        n_g = [g0]
        n_sc = [sc0]
        n_val = [0.0]
        n_depth = [0]
        n_root = [None]

        def gbucket(c, gl):
            best = 99
            row = dist[c]
            for g in gl:
                if g >= 0 and row[g] < best:
                    best = row[g]
            return 0 if best <= 2 else (1 if best <= 5 else 2)

        seen = set()
        seen_best = {}
        if atoms_kind == 'pos_carry':
            seen.add((s0, _carry_bucket(carried)))
        elif atoms_kind == 'pos_carry_g':
            seen.add((s0, _carry_bucket(carried), gbucket(s0, g0)))
        else:
            seen.add(s0)

        def leaf_net(c, carry, fm, cm, gl, sl, depth):
            row = dist[c]
            gds = sorted((row[g], sl[k]) for k, g in enumerate(gl) if g >= 0)
            g1 = gds[0] if gds else (99, 0)
            g2 = gds[1] if len(gds) > 1 else (99, 0)
            nf = 0
            near = 999
            in5 = 0
            for fc in fcells:
                if fm & fbit[fc]:
                    nf += 1
                    d = row[fc]
                    if d < near:
                        near = d
                    if d <= 5:
                        in5 += 1
            cd = 999
            for k, cc in enumerate(cap_cells):
                if cm & (1 << k) and row[cc] < cd:
                    cd = row[cc]
            x = (min(carry, 20) / 20.0, min(dhome[c], 40) / 40.0, min(g1[0], 15) / 15.0,
                 min(g2[0], 15) / 15.0, min(g1[1], 40) / 40.0, nf / 30.0,
                 (min(near, 30) / 30.0) if nf else 1.0, in5 / 10.0, (steps_left - depth) / 300.0,
                 0.0 if home[c] else 1.0, (min(cd, 30) / 30.0) if cd < 999 else 1.0, depthv[c])
            w1, b1, w2, b2 = net
            y = b2
            for wr, bb, wo in zip(w1, b1, w2):
                h = bb
                for wi, xi in zip(wr, x):
                    h += wi * xi
                if h > 15.0:
                    h = 15.0
                elif h < -15.0:
                    h = -15.0
                e2 = 2.718281828459045 ** (2.0 * h)
                y += wo * (e2 - 1.0) / (e2 + 1.0)
            if carry > 0 and dhome[c] > steps_left - depth:
                return -a * carry
            return y - a * carry

        def leaf_netf(c, carry, fm, cm, gl, sl, depth):
            row = dist[c]
            g1d, g1s, g2d = 99, 0, 99
            for k, g in enumerate(gl):
                if g >= 0:
                    dg = row[g]
                    if (dg, sl[k]) < (g1d, g1s):
                        g2d = g1d
                        g1d, g1s = dg, sl[k]
                    elif dg < g2d:
                        g2d = dg
            nf = 0
            near = 999
            in5 = 0
            for fc in fcells:
                if fm & fbit[fc]:
                    nf += 1
                    d = row[fc]
                    if d < near:
                        near = d
                    if d <= 5:
                        in5 += 1
            cd = 999
            for k, cc in enumerate(cap_cells):
                if cm & (1 << k) and row[cc] < cd:
                    cd = row[cc]
            x0 = min(carry, 20) / 20.0
            x2 = min(g1d, 15) / 15.0
            x3 = min(g2d, 15) / 15.0
            x4 = min(g1s, 40) / 40.0
            x5 = nf / 30.0
            x6 = (min(near, 30) / 30.0) if nf else 1.0
            x7 = in5 / 10.0
            x8 = (steps_left - depth) / 300.0
            x10 = (min(cd, 30) / 30.0) if cd < 999 else 1.0
            y = b2n
            st = stat[c]
            for k in range(len(w2n)):
                a0, a2, a3, a4, a5, a6, a7, a8, a10 = dyn_w[k]
                y += w2n[k] * tanh(st[k] + a0 * x0 + a2 * x2 + a3 * x3 + a4 * x4 + a5 * x5 + a6 * x6
                                   + a7 * x7 + a8 * x8 + a10 * x10)
            if carry > 0 and dhome[c] > steps_left - depth:
                return -a * carry
            return y - a * carry

        def leaf_value(c, carry, fm, depth):
            left = steps_left - depth
            v = 0.0
            if carry > 0:
                dh = dhome[c]
                if dh <= left:
                    v += carry * ret * (gamma ** dh)
                else:
                    v -= a * carry
            if carry < 3 and fm:
                best = 999
                row = dist[c]
                for fc in fcells:
                    if fm & fbit[fc]:
                        d = row[fc]
                        if d < best:
                            best = d
                v -= PLAN_FOOD_SHAPE * best
            return v

        best_i = -1
        best_v = -1e9
        if best_first:
            q = [(0.0, 0, 0)]
            counter = 1
        else:
            q = deque([0])
        expanded = 0
        timed_out = False
        while q:
            if node_cap and expanded >= node_cap:
                break
            if (expanded & 15) == 0 and time.perf_counter() - t0 > budget_s:
                timed_out = True
                break
            if best_first:
                i = heapq.heappop(q)[2]
            else:
                i = q.popleft()
            depth = n_depth[i]
            if depth >= horizon:
                continue
            expanded += 1
            c = n_cell[i]
            carry = n_carry[i]
            fm = n_food[i]
            cm = n_cap[i]
            gs = n_g[i]
            scs = n_sc[i]
            base = n_val[i]
            disc = gamma ** depth
            moves = nbr[c]
            if v2:
                moves = moves + ((Directions.STOP, c),)
            for act, j in moves:
                r = 0.0
                ncarry = carry
                nfm = fm
                ncm = cm
                dead = False
                gl = list(gs)
                sl = list(scs)
                if not home[j]:
                    b = fbit.get(j)
                    if b is not None and (nfm & b):
                        nfm &= ~b
                        ncarry += 1
                        r += a
                    b = cbit.get(j)
                    if b is not None and (ncm & b):
                        ncm &= ~b
                        r += capv
                        for k in range(ng):
                            if gl[k] >= 0:
                                sl[k] = SCARED_TIME - SCARED_MARGIN
                    for k in range(ng):
                        if gl[k] == j:
                            if sl[k] > 0:
                                gl[k] = -1
                                r += killv
                            else:
                                dead = True
                elif ncarry > 0:
                    r += ret * ncarry
                    ncarry = 0
                if not dead:
                    drow = dist[j]
                    for k in range(ng):
                        g = gl[k]
                        if g < 0:
                            continue
                        if sl[k] > 0:
                            sl[k] -= 1
                            bestn = g
                            bd = drow[g]
                            for nn in gnbr[g]:
                                if drow[nn] > bd:
                                    bd = drow[nn]
                                    bestn = nn
                            gl[k] = bestn
                        elif drow[g] <= chase_r or (m2 and drow[g] <= chase_r + 4):
                            trow = drow if (not m2 or drow[g] <= 2) else dist[icept[j]]
                            bestn = g
                            bd = trow[g]
                            for nn in gnbr[g]:
                                if trow[nn] < bd:
                                    bd = trow[nn]
                                    bestn = nn
                            gl[k] = bestn
                        if gl[k] == j and not home[j]:
                            if sl[k] > 0:
                                gl[k] = -1
                                r += killv
                            else:
                                dead = True
                if dead:
                    r -= a * ncarry + death
                v = base + disc * r
                if atoms_kind == 'pos_carry':
                    key = (j, _carry_bucket(ncarry))
                elif atoms_kind == 'pos_carry_g':
                    key = (j, _carry_bucket(ncarry), gbucket(j, gl))
                else:
                    key = j
                if dead:
                    tv = v
                elif fast:
                    tv = v + disc * gamma * leaf_netf(j, ncarry, nfm, ncm, gl, sl, depth + 1)
                elif net is not None:
                    tv = v + disc * gamma * leaf_net(j, ncarry, nfm, ncm, gl, sl, depth + 1)
                else:
                    tv = v + disc * gamma * leaf_value(j, ncarry, nfm, depth + 1)
                if piw:
                    old = seen_best.get(key)
                    atom_new = old is None or tv > old + 1e-9
                    if atom_new and not dead:
                        seen_best[key] = tv
                else:
                    atom_new = key not in seen
                if atom_new and not (v2 and dead):
                    seen.add(key)
                if atoms_kind == 'pos_food':
                    eaten = fm & ~nfm
                    if eaten:
                        fkey = ('f', eaten)
                        if fkey not in seen:
                            if not (v2 and dead):
                                seen.add(fkey)
                            atom_new = True
                if not atom_new and not dead and depth > 0:
                    continue  # (root children are always kept, so every root action gets a value)
                ni = len(n_cell)
                n_cell.append(j)
                n_carry.append(ncarry)
                n_food.append(nfm)
                n_cap.append(ncm)
                n_g.append(tuple(gl))
                n_sc.append(tuple(sl))
                n_val.append(v)
                n_depth.append(depth + 1)
                n_root.append(act if depth == 0 else n_root[i])
                if not dead:
                    if best_first:
                        heapq.heappush(q, (-tv, counter, ni))
                        counter += 1
                    else:
                        q.append(ni)
                ra = n_root[ni]
                if tv > root_best.get(ra, -1e9):
                    root_best[ra] = tv
                if tv > best_v:
                    best_v = tv
                    best_i = ni
        info = {'expanded': expanded, 'timed_out': timed_out, 'best_value': best_v,
                'time': time.perf_counter() - t0, 'root_values': root_best}
        if best_i < 0:
            return None, info
        return n_root[best_i], info


class DefPlanner:
    """v7 dplan: IW(1) over (defender cell, invader cell) atoms. We move (on our side, Stop allowed),
    then the invader moves: it flees to its side (nearest enemy-side cell, keeping away from us) when it
    carries >= dplan_ret or we are within 3 steps, else walks to its nearest food (avoiding cells next
    to us when it can). Capture +3 + carried (its food is dropped back), terminal; it eats a food
    -0.1 (it comes back if we catch it); it gets home -carried, terminal. Leaf: -0.5*carried
    - 0.05*distance to it. Root value = best node value in its subtree."""

    def __init__(self, model, cfg):
        self.m = model
        self.cfg = cfg

    def plan(self, me, inv, carried, food, budget_s):
        t0 = time.perf_counter()
        m = self.m
        cfg = self.cfg
        idx = m.index
        dist = m.dist
        home = m.home
        nbr = m.nbr
        hnbr = m.hnbr
        denemy = m.denemy
        ret_k = cfg.dplan_ret
        horizon = cfg.dplan_h
        cap = cfg.dplan_nodes
        d0 = idx[me]
        v0 = idx[inv]
        fbit = {}
        for k, f in enumerate(food):
            fbit[idx[f]] = 1 << k
        fcells = list(fbit.keys())
        nodes = [(d0, v0, carried, (1 << len(food)) - 1, 0.0, 0, None)]
        seen = {(d0, v0)}
        q = deque([0])
        root_best = {}
        expanded = 0
        while q:
            if expanded >= cap or ((expanded & 15) == 0 and time.perf_counter() - t0 > budget_s):
                break
            i = q.popleft()
            d, v, c, fm, val, depth, root = nodes[i]
            if depth >= horizon:
                continue
            expanded += 1
            disc = 0.97 ** depth
            moves = hnbr[d] + ((Directions.STOP, d),)
            for act, nd in moves:
                r = 0.0
                term = False
                nv = v
                nc = c
                nfm = fm
                if nd == v and home[v]:
                    r += 3.0 + c
                    term = True
                else:
                    drow = dist[nd]
                    cand = nbr[v]
                    flee = c >= ret_k or drow[v] <= 3
                    best = None
                    bkey = None
                    for _, n2 in cand:
                        adj = 1 if drow[n2] <= 1 else 0
                        if flee:
                            key = (adj, denemy[n2], -drow[n2], n2)
                        else:
                            fd = 999
                            row2 = dist[n2]
                            for fc in fcells:
                                if nfm & fbit[fc] and row2[fc] < fd:
                                    fd = row2[fc]
                            key = (adj, fd, -drow[n2], n2)
                        if bkey is None or key < bkey:
                            bkey = key
                            best = n2
                    if best is not None:
                        nv = best
                    if not home[nv]:
                        r -= nc
                        term = True
                    elif nv == nd:
                        r += 3.0 + nc
                        term = True
                    else:
                        b = fbit.get(nv)
                        if b is not None and nfm & b:
                            nfm &= ~b
                            nc += 1
                            r -= 0.1
                nval = val + disc * r
                key = (nd, nv)
                if key in seen and not term and depth > 0:
                    continue
                if not term:
                    seen.add(key)
                ra = act if depth == 0 else root
                if term:
                    tv = nval
                else:
                    tv = nval + disc * 0.97 * (-0.5 * nc - 0.05 * dist[nd][nv])
                    nodes.append((nd, nv, nc, nfm, nval, depth + 1, ra))
                    q.append(len(nodes) - 1)
                if tv > root_best.get(ra, -1e9):
                    root_best[ra] = tv
        return root_best, {'expanded': expanded, 'time': time.perf_counter() - t0}


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
        # an enemy Pacman's way home: distance to the nearest enemy-side border cell (H-S17)
        self.dist_enemy_side = {c: min((self.dist[c].get(x, INF) for x in self.cross.values()), default=INF)
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


###############
# Team memory #
###############

class TeamMemory:
    """shared (#3, H-S15; rules.md Q4: allowed): one belief per enemy, updated by both of our agents
    at their own turns. The engine's turn order is fixed (0, 1, 2, 3, 0, ...; game.py), so between
    two consecutive updates by our two agents exactly one enemy has moved: the agent just before the
    updater, (index - 1) % 4. Only that enemy is spread; every update applies the updater's own sonar
    readings (fresh noise each turn) and both agents' sight; a food or capsule of ours that vanished
    since the last update was eaten by that enemy, which still stands there. Respawns are detected
    here, once per update, against the previous update."""

    def __init__(self):
        self.belief = {}     # enemy index -> {cell: probability}; both agents hold this dict
        self.food, self.capsules = set(), set()
        self.seen = {}       # enemy index -> its cell at the last update (visible ones only)
        self.team = {}       # our agent index -> its cell at the last update
        self.fields = {}     # enemy index -> its fields at the last update (flags)

    def reset(self, agent, game_state):
        self.belief.clear()  # in place, so both agents keep the same dict
        for i in agent.get_opponents(game_state):
            self.belief[i] = {game_state.get_initial_agent_position(i): 1.0}
        self.food = set(agent.get_food_you_are_defending(game_state).as_list())
        self.capsules = set(agent.get_capsules_you_are_defending(game_state))
        self.seen, self.team, self.fields = {}, {}, {}

    def update(self, agent, game_state):
        m = agent.map
        opponents = agent.get_opponents(game_state)
        mover = (agent.index - 1) % game_state.get_num_agents()
        team_now = dict((t, game_state.get_agent_position(t)) for t in agent.get_team(game_state))
        # one of us that teleported since the last update (it was eaten) no longer keeps the enemy
        # in sight (T-55); one that moved at most one cell does
        steady = [p for t, p in team_now.items()
                  if p is not None and self.team.get(t) is not None and m.d(self.team[t], p) <= 1]
        fields_now = dict((i, agent.fields(game_state, i)) for i in opponents)
        respawned = set()
        for i in opponents:
            # seen within Manhattan 2 of one of us and gone now: since then one of us and one enemy
            # moved once, so it would still be within sight (<= 5) unless it was eaten
            if game_state.get_agent_position(i) is None and i in self.seen and \
                    any(abs(self.seen[i][0] - t[0]) + abs(self.seen[i][1] - t[1]) <= 2 for t in steady):
                respawned.add(i)
            if agent.field_respawn(self.fields.get(i), fields_now[i]):
                respawned.add(i)
        me = team_now[agent.index]
        readings = game_state.get_agent_distances()
        team = [p for p in team_now.values() if p is not None]

        def consistent(cell, reading):
            if any(abs(cell[0] - t[0]) + abs(cell[1] - t[1]) <= SIGHT for t in team):
                return False
            return abs(abs(cell[0] - me[0]) + abs(cell[1] - me[1]) - reading) <= SONAR_NOISE

        hidden = {}
        for i in opponents:
            pos = game_state.get_agent_position(i)
            if pos is not None:
                self.belief[i] = {pos: 1.0}
                continue
            if i in respawned:
                prior = {game_state.get_initial_agent_position(i): 1.0}
            else:
                prior = self.belief.get(i) or {}
            if i == mover:
                prior = agent.elapse(prior, i, game_state)
            hidden[i] = dict((c, p) for c, p in prior.items()
                             if consistent(c, readings[i]) and agent.side_ok(fields_now[i], c))

        food_now = set(agent.get_food_you_are_defending(game_state).as_list())
        capsules_now = set(agent.get_capsules_you_are_defending(game_state))
        eaten = (self.food - food_now) | (self.capsules - capsules_now)
        if mover in hidden and eaten:  # only the mover can have eaten it, and it has not moved since
            hidden[mover] = {max(sorted(eaten), key=lambda c: hidden[mover].get(c, 0.0)): 1.0}

        for i, cells in hidden.items():
            total = sum(cells.values())
            if total <= 0:  # contradiction (e.g. a respawn we missed): restart from the sonar alone
                cells = dict((c, 1.0) for c in m.cells
                             if consistent(c, readings[i]) and agent.side_ok(fields_now[i], c))
                if not cells:
                    cells = {game_state.get_initial_agent_position(i): 1.0}
                total = float(len(cells))
            self.belief[i] = dict((c, p / total) for c, p in cells.items() if p > 0)

        self.food, self.capsules = food_now, capsules_now
        self.seen = dict((i, game_state.get_agent_position(i)) for i in opponents
                         if game_state.get_agent_position(i) is not None)
        self.team, self.fields = team_now, fields_now


##############
# Base agent #
##############

class V1Agent(CaptureAgent):

    def __init__(self, index, cfg=None, memory=None, time_for_computing=.1):
        super().__init__(index, time_for_computing)
        self.cfg = cfg if cfg is not None else Config()
        self.memory = memory           # shared: the TeamMemory both of our agents update (Q4)
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
        self.raider = None             # P-23: enemy index last evident on our side
        self.bank_sizes = {}           # flags: enemy index -> food amounts it was seen banking
        self._food_goals = (None, None, None)  # (timeleft, distance to our nearest food, that food)

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
        self.raider = None
        self.bank_sizes = {}
        self._food_goals = (None, None, None)
        if self.memory is not None:
            # both agents reset it at the start of every game; resetting twice is harmless because
            # both registrations come before the first move
            self.memory.reset(self, game_state)
            self.belief = self.memory.belief

    # --- enemy fields (rules.md Q3) ---

    def fields(self, game_state, i):
        """(is_pacman, num_carrying, scared_timer, num_returned) of enemy i, hidden or not, or None
        unless USE_HIDDEN_OPPONENT_FLAGS and the `flags` switch are on. The only place in this file
        that reads an opponent's AgentState (rules.md Q3: allowed; keep behind one switch)."""
        if not (USE_HIDDEN_OPPONENT_FLAGS and self.cfg.flags) or game_state is None:
            return None
        state = game_state.get_agent_state(i)
        return state.is_pacman, state.num_carrying, state.scared_timer, state.num_returned

    @staticmethod
    def field_respawn(old, new):
        """H-S14: an eaten enemy drops its food without banking it (capture.py:666) and its scared
        timer is reset to 0 (capture.py:691-727). Between two updates it moves at most once, so a
        timer that was >= 2 cannot have run out on its own."""
        if old is None or new is None:
            return False
        if old[1] > 0 and new[1] == 0 and new[3] == old[3]:
            return True
        return old[2] >= 2 and new[2] == 0

    def side_ok(self, fields, cell):
        """H-S14: an enemy that is a Pacman is on our half, a ghost on its own (capture.py:487)."""
        return fields is None or self.map.is_ours(cell) == fields[0]

    def uses_belief(self):
        return self.cfg.shared

    def perceive(self, game_state):
        """Everything an agent updates at the start of its turn."""
        self.update_enemy_tracking(game_state)
        if self.uses_belief():
            if self.memory is not None:
                self.memory.update(self, game_state)
            else:
                self.update_belief(game_state)
            self.update_raider(game_state)
        if self.cfg.flags:
            self.update_bank_sizes(game_state)

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
        if self.cfg.flags and prev is not None:
            for i in self.get_opponents(game_state):
                if self.field_respawn(self.fields(prev, i), self.fields(game_state, i)):
                    self.unscared.add(i)
                    self.just_respawned.add(i)
                    if game_state.get_agent_position(i) is None:
                        self.last_seen.pop(i, None)
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

        prev = self.get_previous_observation()
        fields_now = dict((i, self.fields(game_state, i)) for i in self.get_opponents(game_state))
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
            moved = self.elapse(prior, i, game_state)
            hidden[i] = {c: p for c, p in moved.items()
                         if consistent(c, readings[i]) and self.side_ok(fields_now[i], c)}

        if prev is not None and hidden:
            food_eaten = (set(self.get_food_you_are_defending(prev).as_list())
                          - set(self.get_food_you_are_defending(game_state).as_list()))
            eaten = food_eaten | (set(self.get_capsules_you_are_defending(prev))
                                  - set(self.get_capsules_you_are_defending(game_state)))
            seen = set(game_state.get_agent_position(i) for i in self.get_opponents(game_state))
            owners = set(hidden)
            for f in sorted(eaten - seen):
                if not owners:
                    break
                candidates = owners
                if self.cfg.flags and f in food_eaten:
                    # H-S14: each enemy moved once and ate at most one dot; the eater's carrying rose
                    eaters = set(i for i in owners if fields_now[i] is not None and self.fields(prev, i)
                                 is not None and fields_now[i][1] > self.fields(prev, i)[1])
                    if eaters:
                        candidates = eaters
                owner = max(sorted(candidates), key=lambda i: (hidden[i].get(f, 0.0),
                                                               -self.expected_dist(hidden[i], f)))
                hidden[owner] = {f: 1.0}
                owners.discard(owner)

        for i, cells in hidden.items():
            total = sum(cells.values())
            if total <= 0:  # contradiction (e.g. a respawn we missed): restart from the sonar alone
                cells = {c: 1.0 for c in self.map.cells
                         if consistent(c, readings[i]) and self.side_ok(fields_now[i], c)}
                if not cells:
                    cells = {game_state.get_initial_agent_position(i): 1.0}
                total = float(len(cells))
            self.belief[i] = {c: p / total for c, p in cells.items() if p > 0}

    def elapse(self, prior, i, game_state):
        """One move of enemy i: it stays with weight STAY_WEIGHT or steps to each neighbour with
        weight 1. With `directed` (H-S17, Ziebart et al. 2009), a step towards the enemy's current
        goal weighs 1 + DIRECT_BONUS; every neighbour keeps a positive weight, so no cell the enemy
        can reach is ever dropped (T-54)."""
        field = self.goal_field(i, game_state) if self.cfg.directed else None
        nbrs = self.map.nbrs
        moved = {}
        for c, p in prior.items():
            if field is None:
                share = p / (len(nbrs[c]) + STAY_WEIGHT)
                moved[c] = moved.get(c, 0.0) + share * STAY_WEIGHT
                for n in nbrs[c]:
                    moved[n] = moved.get(n, 0.0) + share
                continue
            here = field.get(c, INF)
            weights = [(n, 1.0 + DIRECT_BONUS if field.get(n, INF) < here else 1.0) for n in nbrs[c]]
            share = p / (sum(w for _, w in weights) + STAY_WEIGHT)
            moved[c] = moved.get(c, 0.0) + share * STAY_WEIGHT
            for n, w in weights:
                moved[n] = moved.get(n, 0.0) + share * w
        return moved

    def goal_field(self, i, game_state):
        """directed (H-S17): distance field towards enemy i's goal, or None for a random walk.
        A Pacman forages (our nearest food) until it carries what it banked before, then heads for
        its own side; ghosts keep the random walk (their goals are not observable enough)."""
        f = self.fields(game_state, i)
        if f is None or not f[0]:
            return None
        if f[1] >= self.enemy_return_at(i):
            return self.map.dist_enemy_side
        dist, _ = self.food_goals(game_state)
        return dist or None

    def food_goals(self, game_state):
        """Distance from every cell to our nearest food and which food that is (multi-source BFS),
        computed once per turn (H-S16, H-S17)."""
        now = game_state.data.timeleft
        if self._food_goals[0] != now:
            dist, label = {}, {}
            queue = deque()
            for f in sorted(self.get_food_you_are_defending(game_state).as_list()):
                dist[f], label[f] = 0, f
                queue.append(f)
            while queue:
                c = queue.popleft()
                for n in self.map.nbrs[c]:
                    if n not in dist:
                        dist[n], label[n] = dist[c] + 1, label[c]
                        queue.append(n)
            self._food_goals = (now, dist, label)
        return self._food_goals[1], self._food_goals[2]

    def update_bank_sizes(self, game_state):
        """flags: remember how much each enemy banked at a time (its num_returned jumps)."""
        prev = self.get_previous_observation()
        if prev is None:
            return
        for i in self.get_opponents(game_state):
            old, new = self.fields(prev, i), self.fields(game_state, i)
            if old is not None and new is not None and new[3] > old[3]:
                self.bank_sizes.setdefault(i, []).append(new[3] - old[3])

    def enemy_return_at(self, i):
        """Food enemy i probably carries before heading home: the median of what it banked so far."""
        sizes = sorted(self.bank_sizes.get(i, ()))
        return sizes[len(sizes) // 2] if sizes else ENEMY_RETURN_DEFAULT

    def belief_quantile(self, belief, cell, q):
        """Distance from an enemy with this belief to `cell` that it beats with probability q."""
        mass = 0.0
        for d, p in sorted((self.map.d(c, cell), p) for c, p in belief.items()):
            mass += p
            if mass >= q:
                return d
        return INF

    def update_raider(self, game_state):
        """P-23: the enemy most recently evident on our side (seen there, or with belief mass of at
        least HUNT_MASS there). Their defender is never it, unless it has come over. With flags
        (H-S14): the enemy that is a Pacman now; of two, the current raider or the one carrying more."""
        if self.cfg.flags:
            pacmen = [i for i in sorted(self.get_opponents(game_state)) if self.fields(game_state, i)[0]]
            if pacmen and self.raider not in pacmen:
                self.raider = max(pacmen, key=lambda i: (self.fields(game_state, i)[1], i))
            return
        for i, _, invader in self.visible_enemies(game_state):
            if invader:
                self.raider = i
        for i in sorted(self.belief):
            if game_state.get_agent_position(i) is None and \
                    sum(p for c, p in self.belief[i].items() if self.map.is_ours(c)) >= HUNT_MASS:
                self.raider = i

    def goal_open(self, game_state, pos):
        """open_goal (H-S24, marginal value rule): True when no enemy can reach `pos` before we could
        get home from it plus OPEN_MARGIN moves. Each enemy's arrival is its exact distance when seen,
        else the pessimistic OPEN_QUANTILE of its belief distance; scared enemies cannot eat us before
        their timer runs out."""
        eta = INF
        for i in self.get_opponents(game_state):
            f = self.fields(game_state, i)
            seen = game_state.get_agent_position(i)
            if f is None:
                return False
            if seen is not None:
                d = self.map.d(seen, pos)
            else:
                belief = self.belief.get(i)
                if not belief:
                    return False
                d = self.belief_quantile(belief, pos, OPEN_QUANTILE)
            if f[2] > 0:
                d = max(d, f[2] - SCARED_MARGIN)
            eta = min(eta, d)
        return eta > self.map.dist_home[pos] + self.cfg.open_margin

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
        f = self.fields(game_state, i)
        if f is not None:  # H-S14: the exact timer, in the enemy's own moves
            return f[2] > SCARED_MARGIN
        if self.scared_since is None or i in self.unscared:
            return False
        enemy_moves = (self.scared_since - game_state.data.timeleft) // 4 + 1
        return SCARED_TIME - enemy_moves > SCARED_MARGIN

    def defenders(self, game_state):
        """Our agents defending this turn (RoleAgent overrides; fixed roles never split invaders)."""
        return []

    def assigned_invader(self, game_state, known):
        """recall / endgame (H-S26, SCRAM): with two invaders known (enemy index -> cell) and both of
        us defending, the invader this agent takes: of the two pairings, the one whose longer trip is
        shorter (then the shorter total). Computed in a fixed order, so both agents agree."""
        if len(known) != 2:
            return None
        team = self.defenders(game_state)
        if len(team) != 2 or self.index not in team:
            return None
        low, high = sorted(team)
        pos = dict((t, game_state.get_agent_position(t)) for t in team)
        a, b = sorted(known)

        def cost(x, y):  # low takes x, high takes y
            d1, d2 = self.map.d(pos[low], known[x]), self.map.d(pos[high], known[y])
            return max(d1, d2), d1 + d2
        low_takes = a if cost(a, b) <= cost(b, a) else b
        if self.index == low:
            return low_takes
        return b if low_takes == a else a

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
        # lab6
        self.planner = None
        self.plan_info = None
        self.plan_uses = 0
        if self.cfg.plan is not None:
            self.planner = WidthPlanner(WidthModel(self.map), self.cfg)
        self.features = self.map_features(game_state)
        self.focus_mode = self.cfg.focus
        if self.focus_mode == 'auto':
            self.focus_mode = select_focus(self.features)
        self._focus_static = {}

    def choose_action(self, game_state):
        self.perceive(game_state)
        return self.attack(game_state)

    # --- lab6: map features (our own frame: blue's y is flipped, x measured from our border) ---

    def frame_y(self, y):
        h = self.map.height - 1
        return (y if self.red else h - y) / float(max(1, h))

    def map_features(self, game_state):
        food = self.get_food(game_state).as_list()
        caps = self.get_capsules(game_state)
        h = self.map.height - 1
        n = max(1, len(food))
        ys = [self.frame_y(f[1]) for f in food]
        depth_home = [min(self.map.dist_home[f], 40) for f in food]
        deadend = [1.0 if self.map.depth.get(f, 0) > 0 else 0.0 for f in food]
        near = []
        for f in food:
            row = self.map.dist[f]
            near.append(sum(1 for g in food if g != f and row.get(g, INF) <= 3))
        my_food = self.get_food_you_are_defending(game_state).as_list()
        feats = {
            'food_y': sum(ys) / n,
            'food_top': sum(1 for y in ys if y > 0.5) / float(n),
            'food_ystd': (sum((y - sum(ys) / n) ** 2 for y in ys) / n) ** 0.5,
            'food_depth': sum(depth_home) / float(n) / 20.0,
            'food_deadend': sum(deadend) / n,
            'food_cluster': sum(near) / float(n) / 5.0,
            'border_n': len(self.map.home_border) / float(max(1, h + 1)),
            'cap_n': len(caps) / 2.0,
            'cap_y': (sum(self.frame_y(c[1]) for c in caps) / len(caps)) if caps else 0.5,
            'cap_depth': (sum(min(self.map.dist_home[c], 40) for c in caps) / len(caps) / 20.0) if caps else 1.0,
            'cells': len(self.map.cells) / 400.0,
            'my_food_depth': (sum(min(self.map.dist_enemy_side.get(f, 40), 40) for f in my_food)
                              / float(max(1, len(my_food))) / 20.0),
        }
        return feats

    # --- lab6: focus modes for the food-target choice ---

    def focus_penalty(self, game_state, f, food):
        mode = self.focus_mode
        if mode in ('top', 'bottom', 'deep', 'shallow'):
            v = self._focus_static.get(f)
            if v is None:
                if mode == 'top':
                    v = 1.0 - self.frame_y(f[1])
                elif mode == 'bottom':
                    v = self.frame_y(f[1])
                elif mode == 'deep':
                    v = 1.0 - min(self.map.dist_home[f], 20) / 20.0
                else:
                    v = min(self.map.dist_home[f], 20) / 20.0
                self._focus_static[f] = v
            return v
        if mode == 'majority':
            top = self._majority_top
            return 0.0 if ((self.frame_y(f[1]) > 0.5) == top) else 1.0
        if mode == 'cluster':
            row = self.map.dist[f]
            k = sum(1 for g in food if g != f and row.get(g, INF) <= 3)
            return 1.0 - min(k, 5) / 5.0
        if mode == 'far':
            cells = self._enemy_ghost_cells
            if not cells:
                return 0.0
            row = self.map.dist[f]
            dmin = min(row.get(c, INF) for c in cells)
            return 1.0 - min(dmin, 10) / 10.0
        if mode == 'linear':
            return self.linear_penalty(game_state, f, food)
        return 0.0

    def linear_penalty(self, game_state, f, food):
        """focus='linear' (focus_w is ignored): sum_k fw_k * phi_k(f), phi_k in [0, 1], weights in maze
        steps (negative = attraction). The weights are a learned / tuned food-choice policy."""
        cfg = self.cfg
        row = self.map.dist[f]
        v = 0.0
        if cfg.fw_top:
            v += cfg.fw_top * (1.0 - self.frame_y(f[1]))
        if cfg.fw_depth:
            v += cfg.fw_depth * (min(self.map.dist_home[f], 20) / 20.0)
        if cfg.fw_cluster:
            k = sum(1 for g in food if g != f and row.get(g, INF) <= 3)
            v += cfg.fw_cluster * (1.0 - min(k, 5) / 5.0)
        if cfg.fw_ghost and self._enemy_ghost_cells:
            dmin = min(row.get(c, INF) for c in self._enemy_ghost_cells)
            v += cfg.fw_ghost * (1.0 - min(dmin, 10) / 10.0)
        if cfg.fw_deadend:
            v += cfg.fw_deadend * (1.0 if self.map.depth.get(f, 0) > 0 else 0.0)
        if cfg.fw_capsule and self._enemy_caps:
            dc = min(row.get(c, INF) for c in self._enemy_caps)
            v += cfg.fw_capsule * (min(dc, 20) / 20.0)
        if cfg.fw_mate and self._mate_pos is not None:
            v += cfg.fw_mate * (1.0 - min(row.get(self._mate_pos, INF), 10) / 10.0)
        return v

    def focus_action(self, game_state, pos, targets, safe, food):
        """lab6 focus: among race-safe food, minimise steps + focus_w * penalty (penalty in [0, 1])."""
        mode = self.focus_mode
        if mode == 'majority':
            top_n = sum(1 for f in food if self.frame_y(f[1]) > 0.5)
            self._majority_top = top_n * 2 >= len(food)
        if mode in ('far', 'linear'):
            self._enemy_ghost_cells = [c for c, s in self.plan_ghosts(game_state) if s == 0]
        if mode == 'linear':
            self._enemy_caps = list(self.get_capsules(game_state))
            mate = [t for t in self.get_team(game_state) if t != self.index]
            self._mate_pos = game_state.get_agent_position(mate[0]) if mate else None
        tset = set(targets)
        first = {}
        steps = {pos: 0}
        queue = deque()
        for action in game_state.get_legal_actions(self.index):
            if action == Directions.STOP:
                continue
            dx, dy = Actions.direction_to_vector(action)
            nxt = (int(pos[0] + dx), int(pos[1] + dy))
            if nxt not in first and safe(nxt, 1):
                first[nxt] = action
                steps[nxt] = 1
                queue.append(nxt)
        found = []
        while queue:
            cell = queue.popleft()
            s = steps[cell]
            if cell in tset:
                found.append((s + self.cfg.focus_w * self.focus_penalty(game_state, cell, food), s, cell))
            for n in self.map.nbrs[cell]:
                if n not in first and n != pos and safe(n, s + 1):
                    first[n] = first[cell]
                    steps[n] = s + 1
                    queue.append(n)
        if not found:
            return None
        found.sort()
        return first[found[0][2]]

    # --- lab6: planner glue ---

    def plan_ghosts(self, game_state, placement=None):
        """[(cell, scared moves left)] for enemy ghosts (agents on their own side): visible ones at
        their position, hidden ones (with flags + plan_hidden) at their belief's most likely cell, or
        (placement 'near', v7) at the belief cell with mass >= 0.05 nearest to us."""
        if placement is None:
            placement = 'near' if self.cfg.plan_hidden == 'near' else 'argmax'
        me = game_state.get_agent_position(self.index)
        out = []
        for i in self.get_opponents(game_state):
            p = game_state.get_agent_position(i)
            if p is not None:
                if self.map.is_ours(p):
                    continue
                s = game_state.get_agent_state(i).scared_timer
                out.append((p, s - SCARED_MARGIN if s > SCARED_MARGIN else 0))
                continue
            if not self.cfg.plan_hidden:
                continue
            f = self.fields(game_state, i)
            if f is None or f[0]:
                continue
            b = self.belief.get(i)
            if not b:
                continue
            c = max(b, key=b.get)
            if placement == 'near':
                cand = [x for x, pr in b.items() if pr >= 0.05 and not self.map.is_ours(x)]
                if cand:
                    c = min(cand, key=lambda x: (self.map.d(me, x), x))
            if self.map.is_ours(c):
                continue
            out.append((c, f[2] - SCARED_MARGIN if f[2] > SCARED_MARGIN else 0))
        return out

    def plan_alt_ghosts(self, game_state):
        """v7 plan_hidden='both': the 'near' placement as a second scenario."""
        if self.cfg.plan_hidden == 'both':
            return self.plan_ghosts(game_state, 'near')
        return None

    def hunt_scared_action(self, game_state, pos, safe):
        """v7 hunt_scared: a visible scared enemy ghost on its side within hunt_d steps whose scared
        time (minus the margin) exceeds our distance + 1."""
        targets = []
        for i, p, invader in self.visible_enemies(game_state):
            if invader:
                continue
            st = game_state.get_agent_state(i).scared_timer - SCARED_MARGIN
            d = self.map.d(pos, p)
            if d <= self.cfg.hunt_d and st > d + 1:
                targets.append(p)
        if not targets:
            return None
        action, _ = self.bfs_action(game_state, targets, safe)
        return action

    def plan_move(self, game_state, pos, carrying, food, moves_left):
        ghosts = self.plan_ghosts(game_state)
        if self.cfg.plan == 'danger':
            if not any(s == 0 and self.map.d(g, pos) <= self.cfg.plan_trigger for g, s in ghosts):
                return None
        caps = list(self.get_capsules(game_state))
        action, info = self.planner.plan_multi(pos, carrying, food, caps, ghosts, moves_left, self.cfg.plan_budget, self.plan_alt_ghosts(game_state))
        self.plan_info = info
        if action is None or info['best_value'] < self.cfg.plan_min:
            return None
        if action not in game_state.get_legal_actions(self.index):
            return None
        self.plan_uses += 1
        return action

    def uses_belief(self):
        return self.cfg.shared or self.cfg.open_goal

    def late(self, game_state):
        """endgame (H-S27): within the last ENDGAME_MOVES own moves."""
        return self.cfg.endgame and game_state.data.timeleft // 4 <= ENDGAME_MOVES

    def attack(self, game_state):
        if self.cfg.plan in ('override', 'shield') and self.planner is not None:
            return self.attack_override(game_state)
        return self.attack_core(game_state, True)

    def attack_override(self, game_state):
        """lab6 plan='override': greedy decides; the planner overrides greedy's move only when its
        best root action beats greedy's action in the same search tree by more than plan_margin, and
        only while a non-scared modelled ghost is within plan_trigger maze steps."""
        g = self.attack_core(game_state, False)
        pos = game_state.get_agent_position(self.index)
        me = game_state.get_agent_state(self.index)
        carrying = me.num_carrying
        food = self.get_food(game_state).as_list()
        returned = sum(game_state.get_agent_state(i).num_returned for i in self.get_team(game_state))
        moves_left = game_state.data.timeleft // 4
        score = self.get_score(game_state)
        if (len(food) <= 2 or returned + carrying >= self.food_to_win
                or (self.late(game_state) and score < 0 and carrying > -score)
                or moves_left <= self.map.dist_home[pos] + TIME_MARGIN):
            return g
        ghosts = self.plan_ghosts(game_state)
        if not any(s == 0 and self.map.d(c, pos) <= self.cfg.plan_trigger for c, s in ghosts):
            return g
        caps = list(self.get_capsules(game_state))
        action, info = self.planner.plan_multi(pos, carrying, food, caps, ghosts, moves_left, self.cfg.plan_budget, self.plan_alt_ghosts(game_state))
        self.plan_info = info
        if action is None or action == g:
            return g
        rv = info['root_values']
        if self.cfg.plan == 'shield' and rv.get(g, -1e9) >= -0.5 * self.cfg.plan_death:
            return g  # shield: greedy's move is not predicted to be deadly
        if rv.get(action, -1e9) - rv.get(g, -1e9) > self.cfg.plan_margin and                 action in game_state.get_legal_actions(self.index):
            self.plan_uses += 1
            return action
        return g

    def attack_core(self, game_state, use_plan):
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
        threatened = any(self.map.d(g, pos) <= self.cfg.threat_dist for g in ghosts)

        enough = carrying >= self.return_threshold(game_state, pos)
        if enough and self.cfg.open_goal and self.goal_open(game_state, pos):
            enough = False  # H-S24: nobody can catch us before we get home, so keep eating
        score = self.get_score(game_state)
        if self.late(game_state) and score < 0 and carrying > -score:
            enough = True   # H-S27: behind late, bank as soon as this trip takes the lead
        go_home = carrying > 0 and (
            enough
            or len(food) <= 2
            or returned + carrying >= self.food_to_win
            or my_moves_left <= self.map.dist_home[pos] + TIME_MARGIN
            or threatened)

        safe = self.safe_fn(ghosts)
        plan = self.cfg.plan
        if use_plan and plan in ('full', 'danger', 'food') and self.planner is not None:
            special = (len(food) <= 2 or returned + carrying >= self.food_to_win
                       or (self.late(game_state) and score < 0 and carrying > -score)
                       or my_moves_left <= self.map.dist_home[pos] + TIME_MARGIN)
            if not special and (plan != 'food' or not go_home) and not (
                    plan == 'food' and self.cfg.breaker and self.entry is not None):
                action = self.plan_move(game_state, pos, carrying, food, my_moves_left)
                if action is not None:
                    if self.cfg.breaker:
                        self.blocked.append(False)
                    return action
        if not go_home:
            if self.cfg.breaker and self.entry is not None:
                action = self.follow_entry(game_state, pos, me)
                if action is not None:
                    return action
            if self.cfg.hunt_scared:
                action = self.hunt_scared_action(game_state, pos, safe)
                if action is not None:
                    return action
            targets = [f for f in food if self.food_is_safe(f, pos, ghosts)]
            if targets:
                if self.focus_mode not in ('none', '', '0'):
                    action = self.focus_action(game_state, pos, targets, safe, food)
                else:
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
        if sum(self.blocked) < self.cfg.standoff_moves:
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
        self.perceive(game_state)
        return self.defend(game_state)

    def uses_belief(self):
        return self.cfg.hunt or self.cfg.shadow or self.cfg.shared or self.cfg.guard

    def defend(self, game_state):
        pos = game_state.get_agent_position(self.index)
        scared = game_state.get_agent_state(self.index).scared_timer > 0  # our own state
        invaders = [p for _, p, invader in self.visible_enemies(game_state) if invader]
        mine = self.assigned_invader(game_state, dict((i, p) for i, p, invader
                                                      in self.visible_enemies(game_state) if invader))
        if mine is not None:  # recall / endgame: two of us, two invaders in sight: take ours
            invaders = [game_state.get_agent_position(mine)]

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

        if self.cfg.guard and not scared:
            target = self.guard_target(game_state, pos)
            if target is not None:
                self.target = None  # the belief already holds the food events (as P-22)
                if target == pos:
                    return Directions.STOP
                action, _ = self.bfs_action(game_state, [target], lambda cell, steps: self.map.is_ours(cell))
                if action is not None:
                    return action

        if self.cfg.hunt and not invaders:
            # P-22: the belief already holds the food events, so it replaces the eaten-food target
            self.target = None
            suspect = self.suspected_invader(pos, game_state)
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

    def guard_target(self, game_state, pos):
        """guard (H-S16, H-S14): where to go for an invader, seen or hidden (its is_pacman), or None.
        Prefer the invader carrying most (it is worth the most and goes home first). In sight: the
        greedy_v3 intercept. Hidden and carrying what it banked before (or more): the border entry it
        most likely leaves by, if we get there first. Hidden and foraging: the food it most likely
        eats next, if we get there first; this is a simplified goal recognition that takes each
        belief cell's nearest food as the goal (a greedy forager), not the full cost-difference
        formula of Masters & Sardina. Otherwise its most likely cell, intercepted."""
        known = {}
        for i in self.get_opponents(game_state):
            f = self.fields(game_state, i)
            if f is None or not f[0]:
                continue
            seen = game_state.get_agent_position(i)
            if seen is not None:
                known[i] = seen
            elif self.belief.get(i):
                known[i] = self.likely_cell(i, pos)
        known = dict((i, c) for i, c in known.items() if c is not None)
        if not known:
            return None
        choice = self.assigned_invader(game_state, known)
        if choice is None:
            choice = max(sorted(known), key=lambda i: (self.fields(game_state, i)[1],
                                                       -self.map.d(pos, known[i])))
        cell = known[choice]
        if game_state.get_agent_position(choice) is None:
            belief = self.belief[choice]
            carrying = self.fields(game_state, choice)[1]
            if carrying > 0 and carrying >= self.enemy_return_at(choice) and self.map.home_border:
                exit_cell = min(self.map.home_border, key=lambda b: (self.expected_dist(belief, b), b))
                if self.map.d(pos, exit_cell) <= self.expected_dist(belief, exit_cell):
                    return exit_cell
            elif carrying < self.enemy_return_at(choice):
                _, label = self.food_goals(game_state)
                votes = {}
                for c, p in belief.items():
                    if c in label:
                        votes[label[c]] = votes.get(label[c], 0.0) + p
                if votes:
                    nxt = max(sorted(votes), key=lambda f: votes[f])
                    if self.map.d(pos, nxt) <= self.expected_dist(belief, nxt):
                        return nxt
        return self.intercept_cell(pos, cell) if self.cfg.intercept else cell

    def likely_cell(self, i, pos):
        """The most likely cell of enemy i on our side (ties: nearest to us), or None."""
        ours = dict((c, p) for c, p in self.belief.get(i, {}).items() if self.map.is_ours(c))
        if not ours:
            return None
        return max(ours, key=lambda c: (ours[c], -self.map.d(pos, c), c))

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

    def suspected_invader(self, pos, game_state=None):
        """P-22: the most likely home cell of the hidden enemy with the most belief mass on our side,
        if that mass is at least HUNT_MASS (visible enemies have all their mass on their cell).
        With flags (H-S14): a hidden enemy that is a Pacman, preferring the one carrying more."""
        best = None
        for i in sorted(self.belief):
            ours = dict((c, p) for c, p in self.belief[i].items() if self.map.is_ours(c))
            mass = sum(ours.values())
            f = self.fields(game_state, i)
            if f is not None:
                if not f[0] or not ours or game_state.get_agent_position(i) is not None:
                    continue
                key = (f[1], mass)
            elif mass >= HUNT_MASS:
                key = mass
            else:
                continue
            if best is None or key > best[0]:
                cell = max(ours, key=lambda c: (ours[c], -self.map.d(pos, c), c))
                best = (key, cell)
        return best[1] if best is not None else None

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
            threatened = any(self.map.d(g, pos) <= self.cfg.threat_dist for g in ghosts)
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


#####################################
# endgame / recall: per-turn roles  #
#####################################

class RoleAgent(GreedyAttacker, PatrolDefender):
    """endgame (H-S27, P-17c) and recall (H-S26): attacks or defends each turn. In the last
    ENDGAME_MOVES own moves both defend when we lead and both attack when we trail. With recall, the
    home attacker defends while both enemies are Pacmen and it is on our side (or carries nothing
    within RECALL_HOME of home). Each agent works out both roles from facts both see the same way
    (score, time, the enemies' is_pacman, our own agents' states), so they agree without talking."""

    def __init__(self, index, cfg, home_roles, memory=None):
        super().__init__(index, cfg, memory)
        self.home_roles = home_roles
        self.role = home_roles[index]

    def register_initial_state(self, game_state):
        super().register_initial_state(game_state)
        self.role = self.home_roles[self.index]

    def uses_belief(self):
        return True  # it may have to defend (shadow, guard) at any time

    def choose_action(self, game_state):
        self.perceive(game_state)
        role = self.role_of(game_state, self.index)
        if role != self.role:
            self.role = role
            self.target, self.entry = None, None
            self.blocked.clear()
        if role == 'attack':
            return self.attack(game_state)
        if game_state.get_agent_state(self.index).is_pacman:  # called back: get home first
            pos = game_state.get_agent_position(self.index)
            ghosts = self.dangerous_ghosts(game_state)
            threatened = any(self.map.d(g, pos) <= self.cfg.threat_dist for g in ghosts)
            return self.retreat(game_state, ghosts, threatened, self.safe_fn(ghosts))
        g = self.defend(game_state)
        if self.cfg.dplan:
            return self.dplan_move(game_state, g)
        return g

    def dplan_move(self, game_state, g):
        """v7 dplan: the defender planner overrides the rule defender's move g by dplan_margin, against
        the nearest visible invader within 8 steps, while we are not scared."""
        me = game_state.get_agent_state(self.index)
        if me.scared_timer > 0:
            return g
        pos = game_state.get_agent_position(self.index)
        inv = [(self.map.d(pos, p), p, i) for i, p, invader in self.visible_enemies(game_state) if invader]
        if not inv:
            return g
        dd, p, i = min(inv)
        if dd > 8:
            return g
        if getattr(self, 'dplanner', None) is None:
            self.dplanner = DefPlanner(WidthModel(self.map), self.cfg)
        carried = game_state.get_agent_state(i).num_carrying
        food = self.get_food_you_are_defending(game_state).as_list()
        rv, info = self.dplanner.plan(pos, p, carried, food, 0.15)
        if not rv:
            return g
        best = max(sorted(rv), key=lambda a: rv[a])
        if best != g and rv[best] - rv.get(g, -1e9) > self.cfg.dplan_margin and \
                best in game_state.get_legal_actions(self.index):
            return best
        return g

    def role_of(self, game_state, t):
        home = self.home_roles[t]
        if self.late(game_state):
            score = self.get_score(game_state)
            if score > 0:
                return 'defend'
            if score < 0:
                return 'attack'
        if self.cfg.recall and home == 'attack' and self.recalled(game_state, t):
            return 'defend'
        if self.cfg.formation == 'power' and home == 'defend' and self.power_on(game_state, t):
            return 'attack'  # v7 SM-3 power play
        if self.cfg.formation == 'lead' and home == 'defend' and self.get_score(game_state) <= self.cfg.form_lead:
            return 'attack'  # lab6 formation: double attack until we lead by more than form_lead
        return home

    def power_on(self, game_state, t):
        """v7 formation='power' (SM-3): no enemy is a Pacman, and either the enemies' smallest scared
        timer covers a trip from agent t to the nearest enemy food and home + 6, or an enemy respawned
        within the last 10 own moves (it is walking back from its start)."""
        now = game_state.data.timeleft
        seen = getattr(self, 'respawn_seen', None)
        if seen is None:
            seen = self.respawn_seen = {}
        for i in self.just_respawned:
            seen[i] = now
        timers = []
        for i in self.get_opponents(game_state):
            f = self.fields(game_state, i)
            if f is None or f[0]:
                return False
            timers.append(f[2])
        if any(now - tt <= 40 for tt in seen.values()):
            return True
        pos = game_state.get_agent_position(t)
        food = self.get_food(game_state).as_list()
        if not food or pos is None:
            return False
        row = self.map.dist[pos]
        trip = min(row.get(fd, INF) + self.map.dist_home[fd] for fd in food)
        return min(timers) >= trip + 6

    def recalled(self, game_state, t):
        """recall (H-S26): both enemies are Pacmen, and our agent t is on our side or carries nothing
        within RECALL_HOME of home."""
        for i in self.get_opponents(game_state):
            f = self.fields(game_state, i)
            if f is None or not f[0]:
                return False
        state = game_state.get_agent_state(t)
        pos = game_state.get_agent_position(t)
        return not state.is_pacman or (state.num_carrying == 0 and self.map.dist_home[pos] <= RECALL_HOME)

    def defenders(self, game_state):
        return [t for t in self.get_team(game_state) if self.role_of(game_state, t) == 'defend']
