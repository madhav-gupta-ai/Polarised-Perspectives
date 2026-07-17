"""Search for campaign parameters that maximise stable polarisation.

Optuna (Bayesian optimisation) minimises an objective that rewards an even
left/right split with few neutral citizens and few mood changes. Both sides
get the same parameter values, so the search looks for conditions under
which two equally-matched campaigns divide the whole population.

Example:
    python -m src.tune --trials 500
"""

import argparse

import optuna

from . import config
from .model import simulate


def objective_value(counts, N, mood_changes):
    """Distance from a stable 50/50 split: lower is more (and more stably) polarised."""
    left, right, neutral = counts
    return (left - N / 2) ** 2 + (right - N / 2) ** 2 + neutral ** 2 + mood_changes


def make_objective(N, base_seed):
    def objective(trial):
        # Hyperparameters to search (identical for the two sides)
        ILR = trial.suggest_int('ILR', 1, 20)
        DLR = trial.suggest_int('DLR', 10, 25)
        PLR = trial.suggest_float('PLR', 1, 8)
        SM = trial.suggest_float('SM', 8, 20)
        SD = trial.suggest_float('SD', 2, 8)
        D = trial.suggest_int('D', 1, 10)

        seed = None if base_seed is None else base_seed + trial.number
        result = simulate(N=N, D=D, IL=ILR, IR=ILR, DL=DLR, DR=DLR,
                          PL=-PLR, PR=PLR, SM=SM, SD=SD,
                          max_steps=config.TUNE_STEPS, early_stop=False, seed=seed)
        return objective_value(result.final_counts, N, result.mood_changes)

    return objective


def run_study(n_trials=500, N=config.N, seed=config.SEED, show_progress=False):
    sampler = optuna.samplers.TPESampler(seed=seed)
    study = optuna.create_study(direction='minimize', sampler=sampler)
    study.optimize(make_objective(N, seed), n_trials=n_trials,
                   show_progress_bar=show_progress)
    return study


def main():
    parser = argparse.ArgumentParser(
        description='Tune model parameters with Optuna to find maximally '
                    'polarising campaign conditions.')
    parser.add_argument('--trials', type=int, default=500,
                        help='number of Optuna trials (default %(default)s)')
    parser.add_argument('--n', type=int, default=config.N,
                        help='number of civilians, must be even (default %(default)s)')
    parser.add_argument('--seed', type=int, default=config.SEED,
                        help='seed for the sampler and the per-trial simulations '
                             '(default %(default)s)')
    args = parser.parse_args()

    if args.trials < 1:
        parser.error('--trials must be positive')
    if args.n < 26 or args.n % 2:
        parser.error('--n must be an even number >= 26 (search ranges allow '
                     'influencer connections up to 25)')

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = run_study(n_trials=args.trials, N=args.n, seed=args.seed,
                      show_progress=True)

    print('Best parameters:', study.best_params)
    print('Best objective value:', study.best_value)


if __name__ == '__main__':
    main()
