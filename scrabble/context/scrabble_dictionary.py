from __future__ import annotations
from typing import Dict, Sequence


class ScrabbleDictionary(object):
  END_TOKEN = "ø"
  Trie: Dict[str, Dict] = {}
  """
    A valid `Trie` is a dictionary (mapping `str -> Trie`) with the following properties:
    - Each key is either a lowercase alphanumeric character or the `END_TOKEN` (`ø`).
    - Leaf nodes (end of word) are represented as a mapping from `ø` to an empty `dict`. No other key may map to an empty `dict`.
    - A Trie cannot be recursively constructed.
    """

  def __init__(self, word_list: Sequence[str]):
    self._word_set = set(word.lower() for word in word_list)
    self.suffix_tree = ScrabbleDictionary._build_suffix_tree(self._word_set)
    self.prefix_tree = ScrabbleDictionary._build_prefix_tree(self._word_set)

  def __contains__(self, word: str) -> bool:
    return word.lower() in self._word_set

  @staticmethod
  def _insert_into_prefix_trie(
      trie: ScrabbleDictionary.Trie, word: str
  ) -> None:
    for c in word:
      if c not in trie:
        trie[c] = {}
      trie = trie[c]
    trie[ScrabbleDictionary.END_TOKEN] = {}

  @staticmethod
  def _build_suffix_tree(words: Sequence[str]) -> ScrabbleDictionary.Trie:
    trie = {}
    for word in words:
      ScrabbleDictionary._insert_into_prefix_trie(trie, word[::-1])
    return trie

  @staticmethod
  def _build_prefix_tree(words: Sequence[str]) -> ScrabbleDictionary.Trie:
    trie = {}
    for word in words:
      ScrabbleDictionary._insert_into_prefix_trie(trie, word)
    return trie

  @staticmethod
  def open(fname: str):
    with open(fname) as file:
      words = [ScrabbleDictionary._sanitize_line(line) for line in file]
      return ScrabbleDictionary(words)

  @staticmethod
  def _sanitize_line(line: str) -> str:
    return "".join(c.lower() for c in line if c.isalpha())
