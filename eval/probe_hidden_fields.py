"""Shows which fields of an out-of-sight opponent survive into our agent's observation (E-023).

Builds the true initial state of RANDOM13, sets blue agent 1's is_pacman / num_carrying /
scared_timer on the TRUE state only, then calls the engine's own make_observation(0), which is
what red agent 0 receives every turn (CaptureAgent.observation_function). Local analysis only,
never submitted.

Usage (from the repo root): venv\\Scripts\\python.exe eval\\probe_hidden_fields.py
The stray "0" printed first comes from the map generator.
"""
import contest.capture as capture
import contest.layout as layout
from contest.capture import GameState
from contest.util import manhattan_distance

ENEMY = 1
SIGHT_RANGE = 5

name, text = capture.random_layout(seed=13)
lay = layout.Layout(layout_name=name, layout_text=text.split('\n'))

true_state = GameState()
true_state.initialize(lay, 4)
true_state.red_team = [0, 2]
true_state.blue_team = [1, 3]
true_state.teams = [True, False, True, False]

hidden = true_state.data.agent_states[ENEMY]
hidden.is_pacman, hidden.num_carrying, hidden.scared_timer, hidden.num_returned = True, 7, 23, 4

obs = true_state.make_observation(0)
seen = obs.get_agent_state(ENEMY)
dist = min(manhattan_distance(true_state.get_agent_position(ENEMY), true_state.get_agent_position(t))
           for t in true_state.red_team)

print('Manhattan distance to nearest red agent: %d (%s)' % (dist, 'hidden' if dist > SIGHT_RANGE else 'visible'))
print('%-14s %-10s %s' % ('field', 'true', 'observed by agent 0'))
print('%-14s %-10s %s' % ('position', true_state.get_agent_position(ENEMY), obs.get_agent_position(ENEMY)))
for field in ('is_pacman', 'num_carrying', 'scared_timer', 'num_returned'):
    print('%-14s %-10s %s' % (field, getattr(hidden, field), getattr(seen, field)))
