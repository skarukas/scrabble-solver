package(default_visibility = ["//visibility:public"])

py_library(
    name = "solver",
    srcs = ["scrabble_solver.py"],
    deps = [
        ":constraints",
        ":priority_calculators",
        ":pruning_strategies",
        ":ranking_strategies",
        ":state",
        "//scrabble/context:scrabble_context",
        "//scrabble/util:constants",
        "//scrabble/util:scrabble_util",
    ],
)

py_library(
    name = "constraints",
    srcs = ["constraints.py"],
    deps = [
        "//scrabble/context:scrabble_context",
        "//scrabble/context:scrabble_dictionary",
        "//scrabble/util:scrabble_util",
    ],
)

py_library(
    name = "pruning_strategies",
    srcs = ["pruning_strategies.py"],
    deps = [":state"],
)

py_library(
    name = "ranking_strategies",
    srcs = ["ranking_strategies.py"],
    deps = [
        ":state",
        "//scrabble/context:scrabble_context",
    ],
)

py_library(
    name = "priority_calculators",
    srcs = ["priority_calculators.py"],
    deps = [
        ":state",
        "//scrabble/context:scrabble_context",
    ],
)

py_library(
    name = "state",
    srcs = ["state.py"],
    deps = [
        ":constraints",
        "//scrabble/context:scrabble_context",
        "//scrabble/util:scrabble_move",
        "//scrabble/util:scrabble_util",
    ],
)
