load("@pip//:requirements.bzl", "requirement")

py_binary(
    name = "scrabble_main",
    srcs = ["scrabble_main.py"],
    data = ["//scrabble/resources"],
    deps = [
        "//scrabble/context:scrabble_board",
        "//scrabble/context:scrabble_context",
        "//scrabble/context:scrabble_dictionary",
        "//scrabble/solver",
        "//scrabble/util:constants",
        "//scrabble/util:scrabble_move",
        requirement("absl-py"),
    ],
)
