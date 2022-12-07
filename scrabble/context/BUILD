package(default_visibility = ["//visibility:public"])

py_library(
    name = "scrabble_context",
    srcs = ["scrabble_context.py"],
    deps = [
        ":scrabble_board",
        ":scrabble_dictionary",
        "//scrabble/util:constants",
        "//scrabble/util:scrabble_move",
        "//scrabble/util:scrabble_util",
    ],
)

py_library(
    name = "scrabble_dictionary",
    srcs = ["scrabble_dictionary.py"],
)

py_library(
    name = "scrabble_board",
    srcs = ["scrabble_board.py"],
    deps = [
        "//scrabble/util:constants",
        "//scrabble/util:scrabble_move",
        "//scrabble/util:scrabble_util",
    ],
)
