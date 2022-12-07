package(default_visibility=["//visibility:public"])

py_library(
    name = "scrabble_util",
    srcs = ["scrabble_util.py"],
)

py_library(
    name = "scrabble_move",
    srcs = ["scrabble_move.py"],
    deps = [
        ":constants",
        ":scrabble_util",
    ],
)

py_library(
    name = "constants",
    srcs = ["constants.py"],
)
