"""Embed an exported leaf net (eval/rl/leaf_net_<name>.py) into a team file as constants.

usage: python eval/rl/embed_net.py teams/greedy_lab_v6.py eval/rl/leaf_net_v1.py [CONST_NAME]
Replaces `CONST = None` or a previous `# CONST_BEGIN ... # CONST_END` block. Only plan_leaf='net'
configurations read the constant, so other entries keep playing identically.
"""
import re
import sys


def main(team, netfile, const='LEAF_NET'):
    src = open(netfile, encoding='utf-8').read()
    body = src.replace('LEAF_NET', const)
    block = '# %s_BEGIN\n%s# %s_END\n' % (const, body if body.endswith('\n') else body + '\n', const)
    s = open(team, encoding='utf-8').read()
    pat = re.compile(r'# %s_BEGIN\n.*?# %s_END\n' % (const, const), re.S)
    if pat.search(s):
        s = pat.sub(lambda m: block, s, count=1)
    else:
        line = '%s = None\n' % const
        assert s.count(line) == 1, 'placeholder not found'
        s = s.replace(line, block, 1)
    open(team, 'w', encoding='utf-8').write(s)
    print('embedded', netfile, 'into', team, 'as', const)


if __name__ == '__main__':
    main(*sys.argv[1:])
