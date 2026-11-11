"""Local analysis only (never submitted; E-042): re-records chosen greedy_v4 vs flagrats games and measures
what our agents do in double invasions, scared windows and standoffs, from the TRUE state."""
import contextlib, io, json, os, sys, collections
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'eval'))
sys.path.insert(0, os.path.join(REPO, 'teams'))
sys.path.insert(0, os.path.join(REPO, 'pacman-contest', 'src'))
import replay_probe as rp  # noqa
import evaluate as ev  # noqa


def metrics(replay, focus_red):
    from contest.capture import CaptureRules
    from contest import text_display
    from greedy_v2 import MapInfo
    rules = CaptureRules(quiet=True)
    with contextlib.redirect_stdout(io.StringIO()):
        game = rules.new_game(replay['layout'], replay['agents'], text_display.NullGraphics(),
                              replay['length'], False, False)
    st = game.state
    ours = st.get_red_team_indices() if focus_red else st.get_blue_team_indices()
    theirs = st.get_blue_team_indices() if focus_red else st.get_red_team_indices()
    att, dfn = min(ours), max(ours)  # greedy_v4: first index = attacker, second = defender
    m = MapInfo(st.get_walls(), focus_red)
    starts = {k: st.get_initial_agent_position(k) for k in ours + theirs}
    def our_food(s):
        return (s.get_red_food() if focus_red else s.get_blue_food()).count()
    c = collections.Counter()
    in_double = False
    for ply, (mover, action) in enumerate(replay['actions']):
        prev = st
        st = st.generate_successor(mover, action)
        inv = [j for j in theirs if st.get_agent_state(j).is_pacman]
        lost_food = our_food(prev) - our_food(st)
        scared = st.get_agent_state(dfn).scared_timer > 0
        # deaths of our defender
        for k in ours:
            b, a = prev.get_agent_position(k), st.get_agent_position(k)
            if a == starts[k] and b != starts[k] and m.d(b, starts[k]) > 1:
                c['death_%s%s' % ('att' if k == att else 'def', '_scared' if prev.get_agent_state(k).scared_timer > 0 else '')] += 1
                c['death_%s_in_double' % ('att' if k == att else 'def')] += len([j for j in theirs if prev.get_agent_state(j).is_pacman]) == 2
        for j in theirs:
            b, a = prev.get_agent_position(j), st.get_agent_position(j)
            if a == starts[j] and b != starts[j] and m.d(b, starts[j]) > 1:
                c['kills'] += 1
                c['kills_in_double'] += len([q for q in theirs if prev.get_agent_state(q).is_pacman]) == 2
                c['kills_carried'] += prev.get_agent_state(j).num_carrying
        ret = sum(st.get_agent_state(j).num_returned - prev.get_agent_state(j).num_returned for j in theirs)
        oret = sum(st.get_agent_state(k).num_returned - prev.get_agent_state(k).num_returned for k in ours)
        key = 'double' if len(inv) == 2 else ('single' if inv else 'none')
        c['plies_' + key] += 1
        c['eaten_' + key] += lost_food
        c['theyret_' + key] += ret
        c['weret_' + key] += oret
        if scared:
            c['plies_scared'] += 1
            c['eaten_scared'] += lost_food
        if len(inv) == 2:
            if not in_double:
                c['double_episodes'] += 1
                a_st = st.get_agent_state(att)
                c['att_pacman_at_double_start'] += a_st.is_pacman
                c['att_carry_at_double_start'] += a_st.num_carrying
            a_st = st.get_agent_state(att)
            d_st = st.get_agent_state(dfn)
            c['double_att_is_pacman'] += a_st.is_pacman
            c['double_att_home_ghost'] += (not a_st.is_pacman)
            c['double_def_scared'] += d_st.scared_timer > 0
            ghosts = [st.get_agent_position(k) for k in ours if not st.get_agent_state(k).is_pacman]
            if ghosts:
                c['double_gap_sum'] += min(m.d(g, st.get_agent_position(j)) for g in ghosts for j in inv)
                c['double_gap_n'] += 1
            in_double = True
        else:
            in_double = False
        # standoff: our agent is a ghost within 1 of our border while no invader and not attacking
        if mover == att:
            a_st = st.get_agent_state(att)
            if a_st.is_pacman:
                c['att_pac_moves'] += 1
            else:
                c['att_home_moves'] += 1
                pos = st.get_agent_position(att)
                if min(m.d(pos, bb) for bb in m.home_border) <= 2:
                    c['att_at_border_moves'] += 1
        rules.process(st, game)
        if game.game_over:
            break
    c['score'] = st.data.score if focus_red else -st.data.score
    c['plies'] = ply + 1
    return dict(c)


def one(job):
    seed, colour = job
    league = ev.load_league() if hasattr(ev, 'load_league') else json.load(open(os.path.join(REPO, 'eval', 'league.json')))
    red, blue = ('greedy_v4', 'lyw_flagrats') if colour == 'red' else ('lyw_flagrats', 'greedy_v4')
    replay, _ = rp.record_game(red, blue, seed, league, 'pf_%d_%s' % (seed, colour))
    return seed, colour, metrics(replay, colour == 'red')


if __name__ == '__main__':
    # usage: python eval/pitfall_probe.py jobs.json out.json   (jobs = [[seed, "red"/"blue"], ...])
    jobs = [(int(s), c) for s, c in json.load(open(sys.argv[1]))]
    out = []
    with ProcessPoolExecutor(8) as ex:
        for r in ex.map(one, jobs):
            out.append(r)
    json.dump(out, open(sys.argv[2], 'w'))
    print('done', len(out))
