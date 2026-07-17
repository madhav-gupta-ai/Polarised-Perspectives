"""Run a single simulation from the command line.

Examples:
    python -m src.simulate
    python -m src.simulate --pr 9.6 --seed 7
    python -m src.simulate --plot network.png
"""

import argparse

from . import config
from .model import simulate


def main():
    parser = argparse.ArgumentParser(
        description='Simulate two competing political WhatsApp campaigns '
                    'spreading through a network of neutral citizens.')
    parser.add_argument('--n', type=int, default=config.N,
                        help='number of civilians (default %(default)s)')
    parser.add_argument('--d', type=int, default=config.D,
                        help='degree of connections of each civilian (default %(default)s)')
    parser.add_argument('--il', type=int, default=config.IL,
                        help='number of influencers on the left (default %(default)s)')
    parser.add_argument('--ir', type=int, default=config.IR,
                        help='number of influencers on the right (default %(default)s)')
    parser.add_argument('--dl', type=int, default=config.DL,
                        help='connections of each left influencer (default %(default)s)')
    parser.add_argument('--dr', type=int, default=config.DR,
                        help='connections of each right influencer (default %(default)s)')
    parser.add_argument('--pl', type=float, default=config.PL,
                        help='persuasiveness of the left campaign, negative (default %(default)s)')
    parser.add_argument('--pr', type=float, default=config.PR,
                        help='persuasiveness of the right campaign, positive (default %(default)s)')
    parser.add_argument('--sm', type=float, default=config.SM,
                        help='mean susceptibility of civilians (default %(default)s)')
    parser.add_argument('--sd', type=float, default=config.SD,
                        help='standard deviation in susceptibility (default %(default)s)')
    parser.add_argument('--steps', type=int, default=config.MAX_STEPS,
                        help='maximum time steps (default %(default)s)')
    parser.add_argument('--seed', type=int, default=config.SEED,
                        help='random seed; change it to explore run-to-run variation '
                             '(default %(default)s)')
    parser.add_argument('--plot', metavar='PATH',
                        help='save the final network as an image, citizens clustered by allegiance')
    args = parser.parse_args()

    if args.n < 1 or args.steps < 1:
        parser.error('--n and --steps must be positive')
    if args.d >= args.n:
        parser.error('--d must be smaller than --n')
    if (args.n * args.d) % 2:
        parser.error('--n times --d must be even (random regular graph requirement)')
    if args.dl > args.n or args.dr > args.n:
        parser.error('--dl and --dr cannot exceed --n')
    if args.il < 0 or args.ir < 0:
        parser.error('--il and --ir cannot be negative')
    if args.pl > 0:
        parser.error('--pl is the left campaign and must be <= 0 (persuasion is a '
                     'linear scale: negative = left, positive = right)')
    if args.pr < 0:
        parser.error('--pr is the right campaign and must be >= 0')

    result = simulate(N=args.n, D=args.d, IL=args.il, IR=args.ir,
                      DL=args.dl, DR=args.dr, PL=args.pl, PR=args.pr,
                      SM=args.sm, SD=args.sd, max_steps=args.steps,
                      seed=args.seed, verbose=True)

    left, right, neutral = result.final_counts
    if result.converged_at:
        print(f'Convergence reached at iteration {result.converged_at}')
    else:
        print(f'No convergence within {args.steps} steps')
    print(f'Final allegiances: left={left} right={right} neutral={neutral} '
          f'(mood changes: {result.mood_changes})')

    if args.plot:
        import matplotlib
        matplotlib.use('Agg')
        from .plot import draw_network
        ax = draw_network(result.graph, args.n, clustered=True, seed=args.seed,
                          title='Final allegiances')
        ax.figure.savefig(args.plot, dpi=150, bbox_inches='tight')
        print(f'Network plot saved to {args.plot}')


if __name__ == '__main__':
    main()
