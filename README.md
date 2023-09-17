## Scrabble solver

This implementation is a custom algorithm that uses graph search to explore all viable next moves given the player's rack of letters. The possible next states are efficiently calculated by storing references to sub-tries along with the current state. A state will only be explored if it is guaranteed to be a prefix of a valid word.

Watch 2 Scrabble bots play each other by running `bazel run :scrabble_game_main`