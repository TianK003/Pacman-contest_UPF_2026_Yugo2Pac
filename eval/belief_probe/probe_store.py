# Shared in-process log for the belief accuracy check (E-019; local analysis only).
beliefs = []   # (our index, timeleft, {enemy: {cell: p}}, last_seen {enemy: (pos, timeleft)}, move secs)
truth = []     # (enemy index, timeleft at its own observation, its own position)
