"""Append entries to eval/league.json without reformatting the hand-aligned file.

usage: python eval/league_add.py NAME PATH 'k=v,k=v' 'notes' [NAME PATH OPTS NOTES ...]
An empty opts string ('') means no opts. Refuses to overwrite an existing entry (freeze rule).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEAGUE = os.path.join(HERE, 'league.json')


def main(argv):
    if len(argv) % 4 != 0 or not argv:
        sys.exit(__doc__)
    with open(LEAGUE, encoding='utf-8') as fh:
        text = fh.read()
    league = json.loads(text)
    lines = []
    for k in range(0, len(argv), 4):
        name, path, opts, notes = argv[k:k + 4]
        if name in league:
            sys.exit('entry %s already exists (freeze rule: use a new name)' % name)
        entry = {'path': path, 'ours': True, 'frozen': True}
        if opts:
            entry['opts'] = dict(kv.split('=', 1) for kv in opts.split(','))
        entry['notes'] = notes
        body = json.dumps(entry, ensure_ascii=False)
        lines.append('  %s %s' % (json.dumps(name + '') + ':', body))
        league[name] = entry
    end = text.rstrip().rfind('}')
    head = text[:end].rstrip()
    new = head + ',\n' + ',\n'.join(lines) + '\n}\n'
    json.loads(new)  # must still parse
    with open(LEAGUE, 'w', encoding='utf-8') as fh:
        fh.write(new)
    print('added', len(lines), 'entries')


if __name__ == '__main__':
    main(sys.argv[1:])
