NUM_PLANETS = 22
NUM_FEATURES = 14
NUM_ACTIONS_PER_LAYER = NUM_PLANETS * (NUM_PLANETS - 1)
NUM_LAYERS = 2  # TODO: should be 5 some day to account for percentages?
NUM_OUTPUTS = NUM_ACTIONS_PER_LAYER * NUM_LAYERS + 1