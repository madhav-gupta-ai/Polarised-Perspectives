"""Model defaults: the tuned parameter set reported in the paper."""

N = 200    # Number of civilians
D = 9      # Degree of regular agents
IL = 16    # Number of influencers on the left
IR = 16    # Number of influencers on the right
DL = 23    # Degree of influence for left influencers
DR = 23    # Degree of influence for right influencers
PL = -8    # Persuasiveness score of the left campaign (negative)
PR = 8     # Persuasiveness score of the right campaign (positive)
SM = 9     # Mean susceptibility of civilians
SD = 3     # Standard deviation in susceptibility

MAX_STEPS = 100   # simulation cap; a run stops earlier once counts stabilise
TUNE_STEPS = 200  # fixed horizon used by the tuning objective
SEED = 11         # default random seed; gives a run close to the one in the report
