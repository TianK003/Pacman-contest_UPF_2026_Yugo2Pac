# Belief accuracy check (E-019; LOCAL ANALYSIS ONLY, never submitted). Plays games in-process with
# probe_team.py on both sides: ours = teams/greedy_lab_v3.py with the given options, logging the
# defender's belief after each move; theirs = a league entry whose agents log their own position
# at their own turn. Compares the two and writes rows_<opts>.json next to this file (gitignored);
# belief_summary.py turns that into the E-019 table. Touches no engine object.
# usage (from the repo root):
#   venv/Scripts/python.exe eval/belief_probe/belief_check.py . "hunt=1,shadow=1" 5 430 greedy_v2 feature
#   venv/Scripts/python.exe eval/belief_probe/belief_summary.py eval/belief_probe/rows_hunt1_shadow1.json
# Another lab file (E-025): set BELIEF_LAB=teams/greedy_lab_v5.py; outputs then get its name as a prefix.
# Seeds: tuning seeds <seed_offset>+1 .. <seed_offset>+<n_seeds>; options K_<CONST>=v override a
# constant of the loaded lab module (e.g. K_STAY_WEIGHT=1.0).
import io
import json
import os
import sys
from collections import deque
from contextlib import redirect_stdout

REPO = os.path.abspath(sys.argv[1])
OURS_OPTS = sys.argv[2]
N_SEEDS = int(sys.argv[3])
OFFSET = int(sys.argv[4])
OPPONENTS = sys.argv[5:]
HERE = os.path.dirname(os.path.abspath(__file__))
CONTEST = os.path.join(REPO, 'pacman-contest', 'src', 'contest')
sys.path.insert(0, os.path.join(REPO, 'pacman-contest', 'src'))
sys.path.insert(0, HERE)
os.chdir(CONTEST)

import contest.capture as capture  # noqa: E402
import probe_store  # noqa: E402

league = json.load(open(os.path.join(REPO, 'eval', 'league.json')))
seeds = [l.strip() for l in open(os.path.join(REPO, 'eval', 'seeds', 'tuning.txt'))
         if l.strip() and not l.startswith('#')][OFFSET:OFFSET + N_SEEDS]
probe = os.path.join(HERE, 'probe_team.py')
lab = os.path.join(REPO, os.environ.get('BELIEF_LAB', os.path.join('teams', 'greedy_lab_v3.py')))
TAG = '' if 'BELIEF_LAB' not in os.environ else os.path.splitext(os.path.basename(lab))[0] + '_'


def opts_str(d):
    return ','.join('%s=%s' % kv for kv in d.items())


def maze(walls):
    cells = [(x, y) for x in range(walls.width) for y in range(walls.height) if not walls[x][y]]
    cs = set(cells)
    nb = {c: [n for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)) if n in cs]
          for c in cells}
    dist = {}
    for s in cells:
        d = {s: 0}
        q = deque([s])
        while q:
            c = q.popleft()
            for n in nb[c]:
                if n not in d:
                    d[n] = d[c] + 1
                    q.append(n)
        dist[s] = d
    return dist


rows = []
for opp in OPPONENTS:
    entry = league[opp]
    theirs = dict(entry.get('opts', {}))
    theirs.update(role='theirs', team=os.path.join(REPO, entry['path']))
    for seed in seeds:
        for we_red in (True, False):
            ours = 'role=ours,team=%s%s' % (lab, (',' + OURS_OPTS) if OURS_OPTS else '')
            red, blue = (ours, opts_str(theirs)) if we_red else (opts_str(theirs), ours)
            argv = ['-r', probe, '--redOpts', red, '-b', probe, '--blueOpts', blue,
                    '-q', '-l', 'RANDOM%s' % seed, '--delay-step', '0', '-u', 'belief_probe_' + TAG + (OURS_OPTS or 'off')]
            probe_store.beliefs[:] = []
            probe_store.truth[:] = []
            with redirect_stdout(io.StringIO()):
                options = capture.read_command(argv)
                games = capture.run_games(**options)
            layout = games[0].state.data.layout
            dist = maze(layout.walls)
            mid = layout.width // 2
            truth = {}
            for i, t, p in probe_store.truth:
                truth.setdefault(i, []).append((t, p))
            for idx, T, beliefs, last_seen, secs, visible, team, me, readings, resp in probe_store.beliefs:
                for i, b in beliefs.items():
                    if i in visible:
                        continue
                    later = [p for t, p in truth.get(i, []) if t < T]
                    if not later:
                        continue
                    true = later[0]
                    ours_side = (true[0] < mid) == we_red
                    if b:
                        mapc = max(b, key=b.get)
                        exp_err = sum(p * dist[c][true] for c, p in b.items())
                        mass_ours = sum(p for c, p in b.items() if (c[0] < mid) == we_red)
                    else:
                        mapc, exp_err, mass_ours = None, None, 0.0
                    ls = last_seen.get(i)
                    ls_pos = ls[0] if ls else layout.agent_positions[i][1]
                    in_sight = any(abs(true[0] - t[0]) + abs(true[1] - t[1]) <= 5 for t in team if t)
                    sonar_ok = abs(abs(true[0] - me[0]) + abs(true[1] - me[1]) - readings[i]) <= 6
                    prev_true = [p for t, p in truth.get(i, []) if t >= T]
                    prev_true = prev_true[-1] if prev_true else None
                    jump = dist[prev_true][true] if prev_true else None
                    rows.append(dict(in_sight=in_sight, sonar_ok=sonar_ok, jump=jump, resp=i in resp,
                                     at_start=true == layout.agent_positions[i][1],
                                     opp=opp, seed=seed, red=we_red, T=T, i=i, p_true=b.get(true, 0.0),
                                     exp_err=exp_err, map_err=dist[mapc][true] if mapc else None,
                                     support=len(b), mass_ours=mass_ours, true_ours=ours_side,
                                     ls_err=dist[ls_pos][true], secs=secs))
            print(opp, seed, 'red' if we_red else 'blue', 'score', games[0].state.data.score,
                  'rows', len(rows), file=sys.stderr)

out = os.path.join(HERE, 'rows_%s%s.json' % (TAG, OURS_OPTS.replace(',', '_').replace('=', '') or 'off'))
json.dump(rows, open(out, 'w'))
print('wrote', out, len(rows))
