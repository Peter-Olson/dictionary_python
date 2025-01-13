"""
    dictionary.py

    A Dictionary that uses a trie data structure to find
    words and definitions.

    By default, the Collins 2015 dictionary is used. Any
    text file dictionary can be substituted with relative
    easy


"""

import itertools
from collections import defaultdict

DICTIONARY_FILE_NAME = "NWL2023.txt"
# Determines whether the end of a word has been reached
RETRACE_WORD = False
# Globals for Scrabble games (and Scrabble variants)
BLANK_TILE_CHAR = "?"
LETTER_DISTRIBUTION = \
    ["A9", "B2", "C2", "D4", "E12", "F2", "G3", "H2", "I9",
     "J1", "K1", "L4", "M2", "N6", "O8", "P2", "Q1", "R6",
     "S4", "T6", "U4", "V2", "W2", "X1", "Y2", "Z1",
     BLANK_TILE_CHAR + "2"]
LETTER_SCORING = \
    [1, 3, 3, 2, 1, 4, 2, 4, 1,
     8, 5, 1, 3, 1, 1, 3, 10, 1,
     1, 1, 1, 4, 4, 8, 4, 10,
     0]
LETTER_DICTIONARY = \
    {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6,
     "H": 7, "I": 8, "J": 9, "K": 10, "L": 11, "M": 12,
     "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17, "S": 18,
     "T": 19, "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24,
     "Z": 25, BLANK_TILE_CHAR: 26}
LETTER_LIST = []
WORD_MULTIPLIER = "W"
LETTER_MULTIPLIER = "L"
SCRABBLE_BOARD_MULTIPLIERS = \
    [["3W", "1L", "1L", "2L", "1L", "1L", "1L", "3W", "1L", "1L", "1L", "2L", "1L", "1L", "3W"],
     ["1L", "2W", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "2W", "1L"],
     ["1L", "1L", "2W", "1L", "1L", "1L", "2L", "1L", "2L", "1L", "1L", "1L", "2W", "1L", "1L"],
     ["2L", "1L", "1L", "2W", "1L", "1L", "1L", "2L", "1L", "1L", "1L", "2W", "1L", "1L", "2L"],
     ["1L", "1L", "1L", "1L", "2W", "1L", "1L", "1L", "1L", "1L", "2W", "1L", "1L", "1L", "1L"],
     ["1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L"],
     ["1L", "1L", "2L", "1L", "1L", "1L", "2L", "1L", "2L", "1L", "1L", "1L", "2L", "1L", "1L"],
     ["3W", "1L", "1L", "2L", "1L", "1L", "1L", "2W", "1L", "1L", "1L", "2L", "1L", "1L", "3W"],
     ["1L", "1L", "2L", "1L", "1L", "1L", "2L", "1L", "2L", "1L", "1L", "1L", "2L", "1L", "1L"],
     ["1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L"],
     ["1L", "1L", "1L", "1L", "2W", "1L", "1L", "1L", "1L", "1L", "2W", "1L", "1L", "1L", "1L"],
     ["2L", "1L", "1L", "2W", "1L", "1L", "1L", "2L", "1L", "1L", "1L", "2W", "1L", "1L", "2L"],
     ["1L", "1L", "2W", "1L", "1L", "1L", "2L", "1L", "2L", "1L", "1L", "1L", "2W", "1L", "1L"],
     ["1L", "2W", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "3L", "1L", "1L", "1L", "2W", "1L"],
     ["3W", "1L", "1L", "2L", "1L", "1L", "1L", "3W", "1L", "1L", "1L", "2L", "1L", "1L", "3W"]]
# Globals for the Board class
INVALID_PLAY = -1
DOWN = "DOWN"
RIGHT = "RIGHT"


class TrieNode:
    """
    The node objects of a trie, which in essence are
    dictionary data structures. Nodes can hold definitions
    and a boolean that tells whether the end of the word
    has been reached or not
    """

    def __init__(self):
        # Dict: Key = letter, Item = TrieNode
        self.children = {}
        self.defn = ""  # Definition stored here
        self.end = False


class Trie:
    """
    A trie data structure. Some of its functions include:
        - Constructing a trie based on a list of words
            --> build_trie()
        - Constructing a trie based on a list of words
          and their string values (which can be definitions)
            --> build_trie_defs()
        - Adding a new word
            --> insert()
        - Searching for a word
            --> search()
        - Getting the value of a word (a definition)
            --> get_defn()
        - Finding all words based on a root prefix
            --> auto_complete()
        - Finding all words that contain a token
            --> contains_partial()
    """

    def __init__(self):
        self.root = TrieNode()

    def build_trie(self, words, limit=None):
        """
        Add a list of words to the trie
        :param words: The list of words
        :param limit: The limit length of the word, if any
        """
        if limit is None:
            for word in words:
                self.insert(word)
        else:
            for word in words:
                self.insert(word[:limit])

    def build_trie_defs(self, words, defs):
        """
        Add a list of words and their definitions to the trie
        :param words: The list of words
        :param defs: The list of definitions, a parallel list
        """
        for index in range(0, len(words)):
            self.insert(words[index], defs[index])

    def insert(self, word, defn=""):
        """
        Adds a word to the trie. Each key is only one
        character long
        :param word: The word to add
        :param defn: The definition to add
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.defn = defn
        node.end = True

    def has_prefix(self, prefix):
        """
        Determines whether there are any words in the
        dictionary that begin with the given prefix
        :param prefix: The start of a word, eg "BL", which
            would return True for a regular dictionary, since
            there are words that begin with "BL", like "BLAME".
            However, "QZ" would return False, since no words
            begin with the letters "QZ"
        :return: Boolean True if one or more words in the
            dictionary begin with the given prefix, False
            if no words begin with the prefix
        """
        node = self.root
        temp_word = ""
        for char in prefix:
            temp_word += char
            if temp_word == prefix:
                return True
            if char in node.children:
                node = node.children[char]
            else:
                return False
        return False

    def search(self, word):
        """
        Searches for the word in the trie and returns whether
        it is in the trie or not
        :param word: The word to find
        :return: Boolean True if the word is in the true,
                         False otherwise
        """
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False

        return node.end

    def get_defn(self, word):
        """
        Gets the definition of the word in the trie
        :param word: The word whose definition is to be found
        :return: The definition of the word, or False if the
                 word does not exist
        """
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False

        return node.defn

    def walk_trie(self, node, word, word_list):
        """
        Finds all possible strings starting with a given
        node (recursive)
        :param node: The node to search from
        :param word: The word being compiled
        :param word_list: The list of words to add each
            string to
        """
        if node.children:
            for char in node.children:
                word_new = word + char
                if node.children[char].end:
                    word_list.append(word_new)
                self.walk_trie(node.children[char], word_new, word_list)

    def walk_trie_fixed_length(self, node, word,
                               word_list, length):
        """
        Finds all possible words starting with a given
        node (recursive) of a given length
        :param node: The node to search from
        :param word: The word being compiled
        :param word_list: The list of words to add each
            string to
        :param length: The length of the words to find
        """
        if node.children:
            for char in node.children:
                word_new = word + char
                if node.children[char].end and \
                        len(word_new) == length:
                    word_list.append(word_new)
                if len(word_new) <= length:
                    self.walk_trie_fixed_length(
                        node.children[char], word_new,
                        word_list, length)

    def walk_trie_defs(self, node, word, word_list, def_list):
        """
        Finds all possible words starting with a given
        node (recursive) and their definitions
        :param node: The node to search from
        :param word: The word being compiled
        :param word_list: The list of words to add each
            string to
        :param def_list: The list of definitions to add each
            value to
        """
        if node.children:
            for char in node.children:
                word_new = word + char
                if node.children[char].end:
                    word_list.append(word_new)
                    def_list.append(node.children[char].defn)
                self.walk_trie_defs(node.children[char], word_new, word_list, def_list)

    def auto_complete(self, partial_word, node_start=None):
        """
        Finds all words that begin with a partial word
        (recursive)
        :param partial_word: The prefix of the words to find
        :param node_start: The starting node. By default,
            this will be the root node
        :return: List The list of words found
        """
        if node_start is None:
            node = self.root
        else:
            node = node_start

        word_list = []
        # Find the node for last char of word
        for char in partial_word:
            if char in node.children:
                node = node.children[char]
            else:
                # Partial word not found, so return
                return word_list

        # If the last node is the end of a real word, add
        # it to the list
        if node.end:
            word_list.append(partial_word)

        #  Word list will be created in this method for
        #  suggestions that start with partial_word
        self.walk_trie(node, partial_word, word_list)
        return word_list

    def contains_partial(self, token):
        """
        Finds all words that contain a given token
        (helper functions are recursive)
        :param token: The token to search for
        :return: List The list of words found
        """
        global RETRACE_WORD
        node = self.root
        word_list = []
        prefix = ""

        def _contains_partial(_token, _node,
                              _prefix, _word_list):
            """
            Finds all of the words containing the given
            token (recursive). Uses auto_complete() and
            walk_trie()
            :param _token: The token to search for
            :param _node: The node currently searching at
            :param _prefix: The current prefix leading up to
                the token
            :param _word_list: The list of words found that
                contain the token
            :return: List The list of words containing the
                token
            """
            global RETRACE_WORD
            # Find the prefix up to the partial word
            if _node.children:
                for char in _node.children:
                    # Walk back the prefix by one character
                    # when backtracking
                    if RETRACE_WORD:
                        _prefix = _prefix[:-1]
                        RETRACE_WORD = False
                    _prefix += char
                    # If the prefix ends in the token, use
                    # the auto_complete method to find the
                    # rest of the words that contain the
                    # token
                    if _prefix[-len(_token):] == _token:
                        _word_list += self.auto_complete(_prefix, node)
                        break
                    # The token has not been found yet, so
                    # move on to the next character
                    else:
                        # Save the last node for backtracking
                        _last_node = _node
                        _node = _node.children[char]
                        # Only search deeper if the node has
                        # children
                        if len(_node.children) != 0:
                            _contains_partial(
                                _token, _node, _prefix,
                                _word_list)
                            # Backtracking
                            _node = _last_node
                            if len(_prefix) == 1:
                                RETRACE_WORD = True
                        # End of word found, start
                        # backtracking
                        else:
                            RETRACE_WORD = True
                            _node = _last_node

        _contains_partial(token, node,
                          prefix, word_list)
        return word_list


def _read_in_file(dct, text_file_name, use_defs, limit=None):
    """
    Read in the words (and definitions, if applicable) from
    a text file and store them in the trie
    :param dct: The dictionary object to use
    :param text_file_name: The name of the dictionary text
        file
    :param use_defs: True if the dictionary has definitions,
        False if the dictionary only has words
    :param limit: The limit to the length of the words, if any
    """
    file = open(text_file_name, "r")
    list_of_words, list_of_defs = [], []
    lines = file.readlines()
    for line in lines:
        # Remove tabs and multi-whitespace
        line = ' '.join(line.split())
        if use_defs:
            word_index = line.index(" ")
        else:
            word_index = len(line)
        word = line[0:word_index]
        defn = ""
        if use_defs:
            defn = line[word_index:].strip()
        list_of_words.append(word)
        if use_defs:
            list_of_defs.append(defn)

    if use_defs:
        dct.build_trie_defs(list_of_words, list_of_defs)
    else:
        dct.build_trie(list_of_words, limit)


def _find_permutations(word):
    """
    Finds all permutations of the letters of a word and
    stores them in a list
    :param word: The word to permute
    :return: List The list of all possible permutations of
        the letters of the words
    """
    word_list = list(itertools.permutations(word))
    return word_list


def _fill_bag(letter_distribution=None):
    """
    Set the letter_list, which is known as the 'bag' in
    Scrabble-like games. By default, the Scrabble letter
    distribution is used, although a different distribution
    can be specified instead
    :param letter_distribution: A precise list of strings
        describing the distribution of letter tiles. See
        the global variable LETTER_DISTRIBUTION for how
        this list of strings should be formatted
    :return: List The list of letters based on the distribution
    """
    global LETTER_LIST
    # Default Scrabble distribution
    use_global_letter_list = False
    if letter_distribution is None:
        letter_distribution = LETTER_DISTRIBUTION
        use_global_letter_list = True
    # Set letter list based on distribution
    letter_list = []
    for letter_dist in letter_distribution:
        letter = letter_dist[0:1]
        dist = int(letter_dist[1:])
        letters_to_add = list(letter * dist)
        if use_global_letter_list:
            LETTER_LIST.extend(letters_to_add)
        else:
            letter_list.extend(letters_to_add)
    if not use_global_letter_list:
        return letter_list


def _sort_by_value(dct):
    """
    Sort a dictionary by its values
    :param dct: The dictionary to sort
    :return: Dictionary The sorted dictionary
    """
    return dict(sorted(dct.items(), key=lambda item: item[1]))


def _find_words_of_min_value_at_letter_loc(
        word_dct, letter_index, second_index, min_value):
    """
    Finds words within a dictionary that have a minimum value
    at two specified locations. This function was quickly put
    together as a tool to address a particular Scrabble-based
    challenge, and was not designed for general use
    :param word_dct: The dictionary with words
    :param letter_index: The first-index to check the
        scoring value
    :param second_index: The second-index to check the scoring
        value
    :param min_value: The minimum scoring value the letter
        must have in order to not be removed from the
        dictionary
    :return: The dictionary, now only with words that have
        the minimum scoring value at the first and second
        index
    """
    word_index = 0
    word_list = list(word_dct.keys())
    while word_index < len(word_list):
        word = word_list[word_index]
        if LETTER_SCORING[LETTER_DICTIONARY[word[letter_index: letter_index + 1]]] < min_value and \
                LETTER_SCORING[LETTER_DICTIONARY[word[second_index: second_index + 1]]] < min_value:
            word_dct.pop(word)
            word_list.pop(word_index)
        else:
            word_index += 1
    return word_dct


def _remove_words_requiring_blank(word_dct, available_letters):
    """
    Given a dictionary of words and a list of available
    letters to use, remove all words from the dictionary
    that could not be played which would require more letters
    than the available_letters set has to offer
    :param word_dct: The dictionary with words to check
    :param available_letters: The list of available letters,
        where each letter can only be used once
    :return: Dictionary The same dictionary, but with all
        words removed that could not be made using the
        given set of available letters
    """
    word_list = list(word_dct.keys())
    word_index = 0
    while word_index < len(word_dct):
        word = word_list[word_index]
        removed_word = False
        copy_available_letters = available_letters.copy()
        for letter in word:
            if letter in copy_available_letters:
                copy_available_letters.remove(letter)
            else:
                word_dct.pop(word)
                word_list.pop(word_index)
                removed_word = True
                break
        if not removed_word:
            word_index += 1
    return word_dct


def _can_make_word_from_letters(word, available_letters):
    """
    Determines whether it is possible to make the given word
    from the available letters, or not. This function is
    differentiated from the function
    _remove_words_requiring_blank, since this function can
    help maintain the same bag of available letters if a word
    cannot be made (since letters are removed as the word is
    being checked)
    :param word: The word to check
    :param available_letters: The list of available letters,
        which can be used one time each only
    :return: Boolean True if the word can be made from the
        given letters, false otherwise
    """
    letter_index = 0
    while letter_index < len(word):
        letter = word[letter_index: letter_index+1]
        if letter in available_letters:
            available_letters.remove(letter)
            letter_index += 1
        else:
            return False
    return True


def _remove_word_from_letters(word, available_letters):
    """
    Removes all of the letters of a word from a set of
    available letters, which can only be used once each
    :param word: The word to check
    :param available_letters: The list of available letters,
        which can only be used once each
    """
    letters = list(word)
    for letter in letters:
        available_letters.remove(letter)


def _find_highest_scoring_compatible_words(word_dct, total_words):
    """
    Finds the highest scoring words within the dictionary
    that can all be made given a finite set of letters
    available to choose from
    :param word_dct: The dictionary of available words
    :param total_words: The total words to pick. Eg. If this
        variable is three, then the three words that have the
        highest scoring values are chosen, supposing that all
        three can be made using the available letters
    :return: List The list of the compatible words
    """
    word_list = list(word_dct.keys())
    available_letters = LETTER_LIST.copy()
    compatible_word_list = []
    word_index = len(word_list) - 1
    while len(compatible_word_list) < total_words:
        word = word_list[word_index]
        # Add requirement that the first two words must have
        # 'Q' or 'Z' in position four or five, then 'J' must
        # be in position four or five for third
        if len(compatible_word_list) < 3:
            if (LETTER_SCORING[LETTER_DICTIONARY[word[3:4]]] < 8 and
                    LETTER_SCORING[LETTER_DICTIONARY[word[4:5]]] < 8) or \
                    ('Q' in word and 'Z' in word):
                word_index -= 1
                continue
        # ---------------------------------------------------
        if _can_make_word_from_letters(word, available_letters.copy()):
            _remove_word_from_letters(word, available_letters)
            compatible_word_list.append(word)
            word_list.pop(word_index)
            word_index = len(word_list)-1
        else:
            word_index -= 1
    return compatible_word_list


def _remove_words_not_containing_x_letter_word(word_dct, word_list):
    """
    Removes words from a dictionary that do not contain a
    single X letter word contiguously within them. For example,
    if the word length 7 is chosen, if we examine the word
    'SONLIEST', the seven letter word 'ONLIEST' can be found
    within it (yes that is a word), so it would be kept. But
    if we examine the word 'CHARACTER', no seven letter words
    can be found within that nine letter word.
    :param word_dct: The dictionary of words
    :param word_list: The list of X-letter words, which are
        presumably all of the words in the dictionary of a
        given length
    :return: Dictionary The dictionary, now with words removed
        that do not have one or more X-letter word found
        continuously within them
    """
    dct_list = list(word_dct.keys())
    list_index = 0
    word_index = 0
    while word_index < len(dct_list):
        word = dct_list[word_index]
        found_word = False
        for x_letter_word in word_list:
            if x_letter_word in word:
                found_word = True
                break
        if not found_word:
            word_dct.pop(word)
            dct_list.pop(list_index)
        else:
            list_index += 1
            word_index += 1
    return word_dct


def _save_file(file_name, iterable):
    """
    Save an iterable (supposed to be some kind of 2D iterable)
    to a file, using the file name given
    :param file_name: The name of the new text file to make or
        rewrite
    :param iterable: A 2D iterable containing words, presumably
    """
    file = open(file_name, "w")
    all_text = ""
    for word_list in iterable:
        for word_index in range(len(word_list)):
            if word_index != len(word_list)-1:
                all_text += word_list[word_index] + ", "
            else:
                all_text += word_list[word_index] + "\n"
    all_text = all_text[:-1]
    file.write(all_text)
    file.close()


def _save_words_to_file(file_name, dct, use_defs=False):
    """
    Save the keys of a dictionary to a new file of the given name
    :param file_name: The name of the new text file to make
    :param dct: The name of the dictionary
    :param use_defs: Include definitions if true
    """
    file = open(file_name, "w")
    all_text = ""
    for word in dct:
        all_text += word
        if use_defs:
            all_text += " " + dct[word]
        all_text += "\n"
    all_text = all_text[:-1]
    file.write(all_text)
    file.close()


def _save_adjacency_words_to_file(file_name, dct, use_defs=False):
    """
    Save the keys of a dictionary to a new file of the given name
    :param file_name: The name of the new text file to make
    :param dct: The name of the dictionary
    :param use_defs: Include definitions if true
    """
    file = open(file_name, "w")
    all_text = ""
    for word in dct:
        all_text += word + ": "
        if use_defs:
            all_text += " ".join(dct[word])
        all_text += "\n"
    all_text = all_text[:-2]
    file.write(all_text)
    file.close()


def _find_prefixes_of_length(length):
    """
    Creates a dictionary from the default dictionary text file
    that is limited to prefixes of a given length. However,
    non-words are not removed from this dictionary, only copies
    of any duplicate keys (since it is a dictionary)
    :param length: The maximum length of the words for this
        prefix dictionary
    :return: Dictionary The prefix dictionary, whose words
        all have a maximum length. Many will not be 'real'
        words found in a regular dictionary, as many words
        were cut off at the limit to make this dictionary
    """
    prefix_dct = Dictionary(use_defs=False, limit=length)
    return prefix_dct


def _find_overlaps(word_list, total_overlaps=2):
    """
    Given a list of X-letter words (words that all have
    the same length X, not words that start with the
    letter X), find all permutations of words that
    overlap each other making valid words. For example:

        Valid overlaps:
            THE
            AIR

            AORTA
            BREAD

            QUESADILLA
            IMMOLATION

            BAN
            ONE
            ATE

        Invalid overlaps:
            BANE
            ARCH        -> 'NC' is not a word

            MOST
            OKEH
            DARE
            EYES        -> 'THES' is not a word

    Warning:
        This function uses recursion, and is a highly
        computationally intensive process. Finding
        overlaps of longer words can take multiple
        minutes, and finding overlaps that are multiple
        words (three or more) can take minutes, if not
        hours to compute.

        This is a brute force implementation, and there
        are certainly faster, more advanced methods for
        testing word overlapping. As of 12/11/23, these
        have not been implemented as of yet
    :param word_list: The list of X-letter words to test
         for overlapping. The longer the length of the
         list of words, the longer processing will take.
    :param total_overlaps: The total number of words to
        test for overlapping. The more overlaps entered,
        the longer processing will take.
    :return: List The list of valid overlappable words
    """
    overlappable_words = []
    # selected_index = 0
    indices = [0] * total_overlaps
    # This list is used to hold the words being tested
    # for overlapping... they do not necessarily make
    # successful overlaps, this is just for storage
    overlapping_word_list = []
    # The variable below keeps track of what index is
    # currently being changed
    word_selection_index = 0
    # Create a prefix dictionary, which is used for faster
    # searching (short-circuiting word checks whose prefixes
    # cannot result in a valid word)
    prefix_dct = _find_prefixes_of_length(total_overlaps)
    # Minimum number of overlaps before prefixing is worth it
    min_overlaps_for_prefixing = 3

    def _determine_if_overlaps(
            _overlapping_word_list, dct, use_prefixes=False):
        """
        Determines if two words overlap based on the dictionary
        given. Successful overlap is determined by whether
        each vertical word made from the overlap is within the
        dictionary given
        :param _overlapping_word_list: The list of words that
            are overlapping. The first word in the list is the
            word on top, the second beneath it, and so on
        :param dct: The dictionary used to check if the words
            overlap
        :return: Boolean True if the words overlap
            successfully, False otherwise
        """
        for letter_index in range(0, len(_overlapping_word_list[0])):
            vertical_word = ""
            for word in _overlapping_word_list:
                vertical_word += word[letter_index: letter_index + 1]
            if not use_prefixes and not dct.is_word(vertical_word):
                return False
            elif not dct.has_words_starting_with(vertical_word):
                return False
        return True

    def _find_overlaps_recursion(
            _word_list, _overlappable_words, _indices,
            _overlapping_word_list, _word_selection_index
    ):
        """
        Uses recursion to find the list of all sets of words
        that overlap successfully, creating vertical words
        that are all in the dictionary. This method also uses
        a short-circuiting 'prefix' dictionary, which allows
        checks to move on to the next word if a prefix is found
        to not allow for any possible words that are in the
        dictionary. This prefix dictionary is compiled at the
        start of the function, and saves momentous amounts of
        time.
        :param _word_list: The list of words of length X. This
            list makes up all the possible words that will
            be attempted to be overlapped
        :param _overlappable_words: The list of lists of words
            that successfully overlap
        :param _indices: Keeps track of the current
            indices for each layer of words, so that all
            permutations of words are considered (unless
            one or more are short-circuited using the prefix
            dictionary)
        :param _overlapping_word_list: The current list of
            words that is being compiled to check for
            overlapping. At any given point in this algorithm,
            this list may have words that will end up
            successfully overlapping or not. Unless the list
            is short-circuited, it is not possible to tell if
            the list will be overlappable until the last word
            is considered and checked vertically for all spots
        :param _word_selection_index:
            The index that keeps track of which layer is being
            permuted by cycling through words within the
            word_list
        :return: List The list of lists of overlappable words
            is returned. However, this function asks the user
            for the option of whether they would like to save
            the word list in a text file, in which case, the
            return data is likely not needed
        """
        while indices[_word_selection_index] < len(word_list):
            current_word = word_list[indices[_word_selection_index]]
            # Check for bad letter combos. Continue past the
            # current word if the first two or three letters
            # do not allow for any possible words. [Only run
            # prefix checks based on the total number of
            # overlaps being run. For example, if running a
            # 3x4 search (3 words on top of each other of
            # length 4), only check two hooks and three hooks]
            _overlapping_word_list.append(current_word)
            prefixes_work = True
            if 2 <= len(_overlapping_word_list) and \
                    total_overlaps >= min_overlaps_for_prefixing:
                prefixes_work = _determine_if_overlaps(
                    _overlapping_word_list, prefix_dct, True)

            # Last letter of word
            if _word_selection_index == len(indices) - 1 and \
                    prefixes_work:
                overlaps = _determine_if_overlaps(
                    _overlapping_word_list, my_dictionary)
                if overlaps:
                    overlapping_words = []
                    for word in _overlapping_word_list:
                        overlapping_words.append(word)
                    _overlappable_words.append(overlapping_words)
                    print(overlapping_words)
            elif prefixes_work:
                _word_selection_index += 1
                _find_overlaps_recursion(
                    _word_list, _overlappable_words,
                    _indices, _overlapping_word_list,
                    _word_selection_index)
                _indices[_word_selection_index] = 0
                _word_selection_index -= 1
            # Clear last word entry
            _overlapping_word_list.pop()
            # This either increases the index of the last word
            # repeatedly, or increases the index of one of the
            # previous overlapping word by 1 after the word
            # list in the next level has finished testing all
            # words
            _indices[_word_selection_index] += 1

    _find_overlaps_recursion(word_list, overlappable_words, indices, overlapping_word_list, word_selection_index)

    length_word = len(word_list[0])
    print("Total overlappable ", length_word, "-letter words: ", len(overlappable_words), sep='')
    response = input("Would you like to save these in a text file?")
    response = response.upper()
    if response == "YES":
        text_file_name = "overlap_" + str(total_overlaps) + "x" + str(length_word) + "_words.txt"
        _save_file(text_file_name, overlappable_words)
    return overlappable_words


def _create_2d_list(total_rows, total_cols, value=None):
    """
    Create a 2D list, filled with 'value', the default
    being None.

    :param total_rows: The number of rows for the 2D list
    :param total_cols: The number of columns for the 2D list
    :param value: The value to put in each cell
    :return: List A 2D list filled with value
    """
    return [[value for _ in range(total_cols)] for _ in range(total_rows)]


def _get_all_adjectives(word_dct):
    """
    Create a text file containing all of the adjectives in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    adj_dct = word_dct.get_words_with_x_in_def("[adj")
    _save_words_to_file("ADJECTIVE_LIST.txt", adj_dct, True)


def _get_all_adverbs(word_dct):
    """
    Create a text file containing all of the adverbs in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    adv_dct = word_dct.get_words_with_x_in_def("[adv")
    _save_words_to_file("ADVERB_LIST.txt", adv_dct, True)


def _get_all_articles(word_dct):
    """
    Create a text file containing all of the articles in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    art_dct = word_dct.get_words_with_x_in_def("[art")
    _save_words_to_file("ARTICLE_LIST.txt", art_dct, True)


def _get_all_conjunctions(word_dct):
    """
    Create a text file containing all of the conjunctions in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    conj_dct = word_dct.get_words_with_x_in_def("[conj")
    _save_words_to_file("CONJUNCTION_LIST.txt", conj_dct, True)


def _get_all_interjections(word_dct):
    """
    Create a text file containing all of the interjections in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    interj_dct = word_dct.get_words_with_x_in_def("[interj")
    _save_words_to_file("INTERJECTION_LIST.txt", interj_dct, True)


def _get_all_nouns(word_dct):
    """
    Create a text file containing all of the nouns in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    noun_dct = word_dct.get_words_with_x_in_def("[n")
    _save_words_to_file("NOUN_LIST.txt", noun_dct, True)


def _get_all_prepositions(word_dct):
    """
    Create a text file containing all of the prepositions in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    prep_dct = word_dct.get_words_with_x_in_def("[prep")
    _save_words_to_file("PREPOSITION_LIST.txt", prep_dct, True)


def _get_all_pronouns(word_dct):
    """
    Create a text file containing all of the pronouns in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    pronoun_dct = word_dct.get_words_with_x_in_def("[pron")
    _save_words_to_file("PRONOUN_LIST.txt", pronoun_dct, True)


def _get_all_verbs(word_dct):
    """
    Create a text file containing all of the verbs in the given dictionary

    :param word_dct: The Dictionary of the words and defs
    """
    verb_dct = word_dct.get_words_with_x_in_def("[v")
    _save_words_to_file("VERB_LIST.txt", verb_dct, True)


def _create_adjacency_dct(word_dct):
    """
    Create an adjacency dictionary, whose definitions consist of all the words that contain the
    given word in their definition.

    Eg. For the entry JELLYFISH:

        JELLYFISH: CNIDA, MEDUSA, ACALEPH, AEQUORIN, JELLYFISHES

    :param word_dct: The Dictionary to use
    """
    new_dct = dict()
    actual_dct = word_dct.get_dct()  # Convert the Dictionary object to a dict
    for word in actual_dct:
        words_found_dct = word_dct.get_words_with_x_in_def(word, False)
        new_dct.update(words_found_dct)
        print(words_found_dct)
    _save_adjacency_words_to_file("ADJACENCY_NWL_2023.txt", new_dct, True)


def _clean_up_adjacency_file(file_name):
    """
    A helper function for reformatting adjacency files created
    from the _create_adjacency_dct(...) function

    Removes ", " at the ends of entries

    :param file_name: The name of the file to clean up
    """
    with open(file_name, 'r+') as f:
        text = f.read()
        words_list = text.split("\n")
        edited_text = ""
        for line in words_list:
            line = line[:-2]
            edited_text += line + "\n"
        edited_text = edited_text[:-1]
        f.seek(0)
        f.write(edited_text)
        f.truncate()


def _alphabetize_file(file_name):
    """
    Alphabetize a file

    :param file_name: The name of the file to reorder
    """
    with open(file_name, 'r+') as f:
        text = f.readlines()
        text.sort()
        f.seek(0)
        f.write("".join(text))


def _alphabetize_adjacency_words(file_name):
    """
    Alphabetize the adjacency words for all entries within the
    file. Generally speaking, many c and v words appear out of
    order, at the end of the lists. This is related to c and v
    words not having any valid 2-letter words and reading from
    files that are sorted by length first and then alphabetically

    :param file_name: The name of the file to sort
    """
    with open(file_name, 'r+') as f:
        text = f.readlines()
        new_text = ""
        for line in text:
            colon_index = line.index(":")
            root_word = line[:colon_index].upper()
            adj_words_str = line[colon_index + 1:]
            adj_words_str = adj_words_str.strip()
            if len(adj_words_str) <= 1:
                new_text += root_word + ": \n"
                continue
            adj_words_list = adj_words_str.split(" ")
            adj_words_list.sort()
            adj_words_str = " ".join(adj_words_list)

            new_text += root_word + ": " + adj_words_str + "\n"
        new_text = new_text[:-1]
        f.seek(0)
        f.write(new_text)
        f.truncate()


def _remove_adjacency_subwords(adjacency_file_name):
    """
    Create a new adjacency dictionary file by removing all
    subwords and zero adjacency words.

    Eg. aals: -> [remove completely]
        ...
        aardvark: AARDVARKS ANTBEAR -> aardvark: ANTBEAR
        ...
        briefly: DIP NAP NOD REMARK VIGNETTE -> [no change]

    :param adjacency_file_name: The name of the adjacency
        dictionary file
    """
    # Get text
    with open(adjacency_file_name, 'r') as f:
        line_list = f.readlines()

    # Edit lines
    all_text = ""
    for line in line_list:
        colon_index = line.index(":")
        root_word = line[:colon_index].upper()
        adj_words_str = line[colon_index+1:]

        # Remove any entries with no adjacency words
        if len(adj_words_str) <= 2:
            continue

        # Remove adjacency words containing root word
        adj_words_str = adj_words_str.strip()
        adj_words_list = adj_words_str.split(" ")
        new_adj_line = ""
        for adj_word in adj_words_list:
            if root_word not in adj_word:
                new_adj_line += adj_word + " "

        # Remove entries whose adjacency words all contain the
        # root word
        if new_adj_line == "":
            continue

        new_adj_line = new_adj_line[:-1] + "\n"
        all_text += root_word + ": " + new_adj_line

    # Write text to new file
    new_file_name = ""
    all_text = all_text[:-1]
    if ".txt" in adjacency_file_name:
        new_file_name += adjacency_file_name[:adjacency_file_name.index(".txt")]
    else:
        new_file_name += adjacency_file_name
    new_file_name += "_NO_ROOT.txt"
    file = open(new_file_name, "w")
    file.write(all_text)
    file.close()


class Dictionary:
    """
    Dictionary objects are built on Trie data structures.
    However, tries are clunky and less intuitive, so the
    trie structure is abstracted
    """

    def __init__(self, dct_file_name=DICTIONARY_FILE_NAME,
                 use_defs=True, limit=None):
        """
        Create a dictionary using words only or one with
        words and definitions
        :param dct_file_name: The name of the dictionary
            text file
        :param use_defs: True if the dictionary will use
            definitions, False if it will only use words
        :param limit: The word length limit, if any
        """
        self.__dct = Trie()
        self.use_defs = use_defs
        print("Loading dictionary...")
        _read_in_file(self.__dct, dct_file_name, self.use_defs, limit)
        _fill_bag()

    def is_word(self, word):
        """
        Determine whether the given word is in the dictionary
        or not
        :param word: The word to search for
        :return: Boolean True if the word is in the
            dictionary, False otherwise
        """
        return self.__dct.search(word.upper())

    def is_defn(self, defn):
        """
        Determines whether the definition appears in the
        dictionary or not
        :param defn: The definition to search for
        :return: Boolean True if the definition appears in
            the dictionary, False otherwise
        """
        word_list = []
        def_list = []
        self.__dct.walk_trie_defs(self.__dct.root, "", word_list, def_list)

        return defn in def_list

    def get_word_from_def(self, defn):
        """
        Get a word based on a definition
        :param defn: The definition used to find its
            corresponding word
        :return: String The word that corresponds with the
            definition
        """
        word_list = []
        def_list = []
        self.__dct.walk_trie_defs(self.__dct.root, "", word_list, def_list)

        return word_list[def_list.index(defn)]

    def get_def(self, word):
        """
        Gets the definition of a word. Returns False if the
        word is not found
        :param word: The word whose definition is to be found
        :return: String The definition of the word, or False
            if the word is not found
        """
        return self.__dct.get_defn(word.upper())

    def get_words_with_x_in_def(self, string, include_def=True):
        """
        Finds the list of words whose definitions contain
        a given string. Returns a dictionary of the words
        and their definitions
        :param string: The string to search the definitions
            for
        :param include_def: True if the definition is included, false otherwise. If definitions are
            included, each entry is the word-definition pair that the string was found in. If not
            included, each key is the string and each value are the words that contain the string
            in their definitions
        :return: dict A dictionary containing the words and
            their definitions if definitions are included, whose definitions contain the
            string, or if definitions are not included, a dictionary whose keys are the string, and
            values are the words whose definitions contain that string
        """
        all_words = []
        def_list = []
        self.__dct.walk_trie_defs(self.__dct.root, "", all_words, def_list)

        dct = dict()
        dct_lst = defaultdict(list)
        string = string.lower()
        for index in range(0, len(def_list)):
            if string in def_list[index]:
                if include_def:
                    dct[all_words[index]] = def_list[index]
                else:
                    dct_lst[string].append(all_words[index])
        if include_def:
            return dct
        else:
            if len(dct_lst) == 0:
                dct_lst[string].append("")
            return dct_lst

    def get_x_letter_words(self, length):
        """
        Find all words of a given length
        :param length: The length of the words to find
        :return: List The list of words of the given length
        """
        word_list = []

        self.__dct.walk_trie_fixed_length(
            self.__dct.root, "", word_list, length)

        return word_list

    def has_words_starting_with(self, root):
        return self.__dct.has_prefix(root)

    def get_words_starting_with(self, root):
        """
        Finds the list of words starting with the given root
        :param root: A String of letters representing the
            prefix of a word
        :return: List The list of words that begin with the
            given root
        """
        return self.__dct.auto_complete(root)

    def get_words_containing(self, token):
        """
        Finds the list of words containing the given token
        :param token: The token being searched for
        :return: List The list of words containing the given
            token
        """
        return self.__dct.contains_partial(token)

    def find_anagrams(self, word):
        """
        Find all anagrams of the word, using all letters
        within the word.

        For example, the word 'DISASTER' has three other
        anagrams: 'ASTERIDS', 'DIASTERS', and 'DISRATES'

        :param word: The word to anagram
        :return: List A list of the anagrams of the word.
            Duplicates are removed
        """
        permute_list = _find_permutations(word)
        word_list = []

        for token in permute_list:
            token = ''.join(token)
            if self.__dct.search(token):
                word_list.append(token)

        return list(set(word_list))

    def find_subanagrams(self, word, sort_by_length=False):
        """
        Finds all possible words that can be made using the
        letters that make up 'word'. Letters can only be
        used once

        For example, the word 'CAT' has four total
        subanagrams: 'CAT', 'ACT', 'TA', and 'AT'

        :param word: The letters used to find all possible
            words that can be made
        :param sort_by_length: Determines whether the list of
            subanagrams is sorted by length and alphabetized,
            or whether it is just alphabetized. True sorts
            alphabetically and by length. False sorts just
            alphabetically
        :return: List The list of words that can be made from
            the list of letters that comprise 'word'
        """

        word_list = []

        def _find_subanagrams(_word, _word_list):
            """
            Finds all possible subanagrams of the word,
            using recursion
            :param _word: The letters to permute and find
                words from
            :param _word_list: The list of valid words found
                thusfar
            """
            _word_list += self.find_anagrams(_word)
            if len(_word) > 1:
                for index in range(0, len(_word)):
                    sub_word_letters = _word[0:index] + _word[index + 1:]
                    _find_subanagrams(sub_word_letters, _word_list)

        _find_subanagrams(word, word_list)

        word_list = list(set(word_list))

        def _custom_key(_str):
            return -len(_str), _str.lower()

        if sort_by_length:
            word_list = sorted(word_list, key=_custom_key)
        else:
            word_list.sort()

        return word_list

    @staticmethod
    def get_word_score(word, letter_scoring=None):
        """
        Get the total score of a word when its letter score
        values are added up.
        :param word: The word to score
        :param letter_scoring: The score values for each letter
            for scoring in Scrabble-like games. If this is
            None, use the default global LETTER_SCORING
        :return: Integer The total value of the score
        """
        total_score = 0
        for letter in word:
            # LETTER_DICTIONARY used to get index of letter
            if letter_scoring is None:
                letter_scoring = LETTER_SCORING
            total_score += letter_scoring[LETTER_DICTIONARY[letter]]
        return total_score

    def get_highest_scoring_words(self, word_list):
        """
        Creates a dictionary of the highest scoring words
        from a given list, sorted from lowest to highest values
        :param word_list: The list of words to search
        :return: Dictionary A dictionary of the highest scoring
            words found within the list, sorted from lowest
            to highest values
        """
        # To get all the words in the dictionary, an empty
        # list can be used or None
        if word_list is None or len(word_list) == 0:
            word_list = []
            self.__dct.walk_trie(self.__dct.root, "", word_list)

        # Find highest scoring word based on LETTER_SCORING
        word_score_dct = dict()
        for word in word_list:
            word_score_dct[word] = Dictionary.get_word_score(word)
        return _sort_by_value(word_score_dct)

    def get_dct(self):
        """
        Return a dict equivalent of this Dictionary object
        """
        word_list = []
        def_list = []
        if self.use_defs:
            self.__dct.walk_trie_defs(self.__dct.root, "", word_list, def_list)
        else:
            self.__dct.walk_trie(self.__dct.root, "", word_list)

        dct = dict()
        for index in range(0, len(word_list)):
            word = word_list[index]
            if self.use_defs:
                dct[word] = def_list[index]
            else:
                dct[word] = ""
        return dct

    def print_dct(self):
        """
        Print the dictionary's set of words and their
        definitions (if applicable)
        """
        word_list = []
        def_list = []
        if self.use_defs:
            self.__dct.walk_trie_defs(self.__dct.root, "", word_list, def_list)
        else:
            self.__dct.walk_trie(self.__dct.root, "", word_list)

        for index in range(0, len(word_list)):
            print(word_list[index], end='')
            if not self.use_defs:
                print("")
            if self.use_defs:
                print(": ", def_list[index], sep='')


def _set_board(board, board_multipliers):
    """
    Sets the initial board values based on whether a default
    board has been given or not. The board and the board
    multipliers must have the same dimensions
    :param board: The board
    :param board_multipliers: The board multipliers
    :return: [[]] The board for a starting game of Scrabble
        or a Scrabble-like game
    """
    # Empty board and default multipliers
    if board is None and board_multipliers is None:
        return _create_2d_list(len(SCRABBLE_BOARD_MULTIPLIERS), len(SCRABBLE_BOARD_MULTIPLIERS[0]))
    # Non-standard multipliers, and empty board
    elif board is None and board_multipliers is not None:
        return _create_2d_list(len(board_multipliers), len(board_multipliers[0]))
    # Non-empty board... multipliers are set in _set_board_multipliers
    else:
        return board


def _set_board_multipliers(board_multipliers):
    """
    Sets the board multipliers based on whether a default
    board multiplier is given or not. The board and the board
    multipliers must have the same dimensions
    :param board_multipliers: The board multipliers
    :return: [[]] The board multipliers for a starting
        Scrabble game, or Scrabble-like game
    """
    # Default multipliers
    if board_multipliers is None:
        return SCRABBLE_BOARD_MULTIPLIERS
    # Non-default multipliers
    else:
        return board_multipliers


def _set_letter_scoring(letter_scoring):
    """
    Sets the letter scoring values based on whether a default
    list of scoring values was given or not
    :param letter_scoring: The letter scoring values
    :return: List The letter scoring values
    """
    if letter_scoring is None:
        return LETTER_SCORING
    else:
        return letter_scoring


class Board:
    """
        Create a Scrabble-type board object, used for playing
        Scrabble games or Scrabble-like games (eg. Words With
        Friends, or custom boards). The Board class contains
        functions useful for maintaining board states, scores,
        finding plays, calculating scores, and other functions
        related to the Scrabble board. Some useful functions
        can instead be found as private functions to this
        script, or within the Dictionary class.

        Additionally, several quick-access global variables
        are used for typical instantiation of Scrabble
        settings and objects, such as the Scrabble letter
        distribution, the Scrabble multiplier board, and other
        values
    """
    def __init__(self, game_dct, board=None, board_multipliers=None, letter_dist=None, letter_scoring=None):
        self.dct = game_dct
        self.board = _set_board(board, board_multipliers)
        self.multipliers = _set_board_multipliers(board_multipliers)
        self.letter_dist = _fill_bag(letter_dist)
        self.letter_scoring = _set_letter_scoring(letter_scoring)
        self.last_play = []

    def _is_valid_coord(self, row, col):
        """
        Determines whether the coordinate is valid within the
        board or not
        :param row: The row of the tile
        :param col: The column of the tile
        :return: Boolean True if the coordinate exists within
            the board, False otherwise
        """
        if 0 <= row < len(self.board) and \
                0 <= col < len(self.board[0]):
            return True
        return False

    def undo_play(self):
        """
        Change all coordinates stored in the self.last_play
        list of tuples to now have blank spaces (None) values.
        Then reset the list to have no coordinate pairs
        representing the last letters played
        """
        for tuple_coord in self.last_play:
            self.board[tuple_coord[0]][tuple_coord[1]] = None
        self.last_play.clear()

    def get_multiplier(self, row, col):
        """
        Returns the decimal multiplier for the tile at the
        coordinate given. If the tile is a word multiplier,
        a negative decimal value is returned
        :param row: The row of the multiplier
        :param col: The column of the multiplier
        :return: Double If positive, the multiplier of the
            letter tile. If negative, the multiplier of the
            word going through this tile
        """
        tile_multiplier = self.multipliers[row][col]
        multiplier = 1.0
        multiplier_identifier_index = \
            tile_multiplier.find(next(
                filter(str.isalpha, tile_multiplier)))
        multiplier *= float(
            tile_multiplier[0:multiplier_identifier_index])
        if WORD_MULTIPLIER in tile_multiplier:
            multiplier *= -1
        return multiplier

    def _get_cross_word_score(
            self, letter, row, col, direction, multiplier):
        """
        Gets the word score for the word going perpendicularly
        to the direction given. This function does not account
        for same direction hooks, eg. FOOT -> FOOTBALL. This
        function does account for perpendicular hooks, including
        Eg.
            LAKE    ->    LAKES   and   FOX ROT    ->    FOXTROT
                              E                             I
                              T                             E

        :param letter: The letter of the word that connects
            between the two intersecting words
        :param row: The row of the letter
        :param col: The column of the letter
        :param direction: The direction the original word is
            going, which is opposite to the direction the
            word that has been hooked is going
        :param multiplier: The multiplier of the letter. If
            the multiplier is negative, then it is a word
            multiplier instead of a letter multiplier
        :return: Integer The score of the crossword, including
            any multipliers picked up from the letter that has
            been placed from the word it intersects. Note that
            any multipliers that may be under the cross-word
            are not included in the score... the multipliers
            are one-use only
        """
        # Set direction to opposite direction of original word
        new_direction = DOWN
        if direction == DOWN:
            new_direction = RIGHT
        # Variables
        score = 0

        def _get_cross_word_score_piece(cross_dir, is_neg_dir):
            """
            Find the score of the piece of the word that is on
            one side of the intersecting letter. More often than
            not, there will only be one piece in the first place.

            This occurs in the odd example when a word is played
            like the following:

                FOX ROT     ->      FOXTROT
                                       I
                                       E

            :param cross_dir: The direction that the cross-word
                is being placed
            :param is_neg_dir: True if this piece is being
                calculated in the negative direction, False
                otherwise. The negative directions include going
                up or left, and positive include right or down
            :return: The score of the crossword, including the
                letter shared between the two words intersecting.
                If the letter shared has a word score, this is
                applied as well
            """
            cross_score = 0
            new_row = row
            new_col = col
            new_row_delta, new_col_delta = 0, 0
            # Set incrementers
            if cross_dir == DOWN:
                if is_neg_dir:
                    new_row_delta = -1
                else:
                    new_row_delta = 1
            else:
                if is_neg_dir:
                    new_col_delta = -1
                else:
                    new_col_delta = 1
            new_row += new_row_delta
            new_col += new_col_delta
            # Find score of all letters of piece
            while self.board[new_row][new_col] is not None:
                cross_score += \
                    self.get_score(self.board[new_row][new_col])
                new_row += new_row_delta
                new_col += new_col_delta
            return cross_score

        # Add letters above or left of letter
        score += _get_cross_word_score_piece(new_direction, True)
        # Add letters below or right of letter
        score += _get_cross_word_score_piece(new_direction, False)
        # Get score of letter
        word_multiplier = 1
        if multiplier >= 0:
            score += self.get_score(letter) * multiplier
        # Word multiplier, applied later
        else:
            word_multiplier *= abs(multiplier)
            score += self.get_score(letter)
        # Get total score
        score *= word_multiplier
        return score

    def _is_touching_word(self, row, col, direction):
        """
        Determines whether the tile is next to a letter
        (perpendicular to the current direction) or if the
        current tile already has a letter (word is
        intersecting another word, and thus touching)
        :param row: The row of the current tile
        :param col: The column of the current tile
        :param direction: The current direction of the word
            being played
        :return: Boolean True if the tile is touching another
            word, False otherwise
        """
        # Check current tile
        if self.board[row][col] is not None:
            return True
        # Check tiles left and right
        if direction == DOWN:
            if (self._is_valid_coord(row, col-1) and
                    self.board[row][col-1] is not None) or \
                    (self._is_valid_coord(row, col+1) and
                     self.board[row][col+1] is not None):
                return True
        # Check tiles above and below
        elif (self._is_valid_coord(row-1, col) and
                self.board[row-1][col] is not None) or \
                (self._is_valid_coord(row+1, col) and
                 self.board[row+1][col] is not None):
            return True
        # Check tile before the word
        if direction == DOWN:
            if self._is_valid_coord(row-1, col) and \
                    self.board[row-1][col] is not None:
                # Check that this isn't the tile that was just
                # played
                if len(self.last_play) == 0:
                    return True
        elif self._is_valid_coord(row, col-1) and \
                self.board[row][col-1] is not None:
            # Check that this isn't the tile that was just
            # played
            if len(self.last_play) == 0:
                return True
        # Check tile after the word
        if direction == DOWN:
            if self._is_valid_coord(row + 1, col) and \
                    self.board[row + 1][col] is not None:
                return True
        elif self._is_valid_coord(row, col + 1) and \
                self.board[row][col + 1] is not None:
            return True

        return False

    def set_word(self, word, row, col, direction):
        """
        Sets a word on the board starting at the given
        coordinate, regardless of whether the play will be
        valid or not. If the word would not correctly
        intersect existing words on the board, the word will
        instead be played over the letters existing, but not
        replacing them. Similarly, if the play would go off
        the edge of the board, only place tiles up to the edge.
        This function also saves the locations of the
        played letters in the field self.last_play, so that
        the word can be removed if needed (if only valid plays
        are being accepted)
        :param word: The word being played on the board
        :param row: The row of the first letter in the word
            being played
        :param col: The column of the first letter in the word
            being played
        :param direction: The direction that the word is being
            played
        :return: Integer The score of the play
        :return: Boolean True if the play was valid, False
            otherwise
        """
        word = word.upper()
        valid_play = True
        is_first_play = False
        play_through_center = False
        touching_word = False
        score = 0  # Used before word multipliers are applied
        cross_scores = 0  # For finding scores of words hooked
        total_multiplier = 1
        self.last_play.clear()  # Remove last move played
        # Check if this is the first play of the game
        if self.is_empty():
            is_first_play = True
        # Play each letter, if possible. Save each letter loc
        # in self.last_play. If the play is invalid, update
        # valid_play
        # Assumes a board with an odd number of rows and cols
        board_center_row = len(self.board)//2
        board_center_col = len(self.board[0])//2
        for letter in word:
            word_multiplier = 1
            if self._is_valid_coord(row, col):
                # Check if first play goes through center
                if is_first_play and row == board_center_row and \
                        col == board_center_col:
                    play_through_center = True
                # Check if touching word
                if not touching_word and not is_first_play and \
                        self._is_touching_word(row, col, direction):
                    touching_word = True
                # Check if a tile exists at the coordinate given
                if self.board[row][col] is None:
                    # Place tile and update score
                    self.board[row][col] = letter
                    # Add last letter coordinates to last_play
                    # to keep track of where last letters have
                    # been played
                    self.last_play.append((row, col))
                    multiplier = self.get_multiplier(row, col)
                    # Single letter multiplier
                    if multiplier >= 0:
                        score += self.get_score(letter) * multiplier
                    # Word multiplier, applied later
                    else:
                        word_multiplier *= abs(multiplier)
                        score += self.get_score(letter)
                    # Check if a word is being made perpendicularly
                    if direction == DOWN and \
                            (self.board[row][col-1] is not None or
                             self.board[row][col+1] is not None):
                        cross_scores += self._get_cross_word_score(letter, row, col, direction, multiplier)
                    elif direction == RIGHT and \
                            (self.board[row-1][col] is not None or
                             self.board[row+1][col] is not None):
                        cross_scores += self._get_cross_word_score(letter, row, col, direction, multiplier)
                elif self.board[row][col] == letter:
                    # Update score, but do not place letter
                    score += self.get_score(letter)
                else:
                    valid_play = False
                # Update row or col
                if direction == DOWN:
                    row += 1
                else:
                    col += 1
            else:
                valid_play = False
                if direction == DOWN:
                    row += 1
                else:
                    col += 1
            total_multiplier *= word_multiplier
        # Apply word multiplier (if there are none, then mult
        # by 1). Then get total_score combining cross scores
        # and score
        score *= total_multiplier
        total_score = score + cross_scores
        # Find whether the play was valid
        all_valid = valid_play
        if is_first_play and not play_through_center:
            all_valid = False
        if not is_first_play and not touching_word:
            all_valid = False

        return total_score, all_valid

    def play_word(self, word, row, col, direction):
        """
        Plays a word on the board starting at the given
        coordinate on the board. If the play is invalid,
        returns INVALID_PLAY and nothing is played on the
        board. If the play is valid, returns the score gained
        from the played word, taking into account tile
        multipliers. If there are no tiles on the board, the
        play must go through the center tile, otherwise, the
        play is invalid. A play is considered valid if it fits
        on the board, if it correctly intersects words already
        on the board, but this function does not consider
        whether the words played or made through the play are
        actually words or not
        :param word: The word to play on the board
        :param row: The row of the first tile of the word
        :param col: The column of the first tile of the word
        :param direction: Determines the direction which the
            word is played. Direction must be equal to DOWN
            or RIGHT
        :return: Integer Returns the score of the word played
            on the board, including tile multipliers, or
            INVALID_PLAY if the play was not valid
        """
        score, was_valid_play = self.set_word(word, row, col, direction)
        if was_valid_play:
            return score
        else:
            self.undo_play()
        return INVALID_PLAY

    def get_score(self, word):
        """
        Get the total score of a word based on the values of
        its letters
        :param word: The word to get the score of
        :return: Integer The score of the word
        """
        return Dictionary.get_word_score(word, self.letter_scoring)

    def is_empty(self):
        """
        Determines if the board is empty or not. A board is
        empty if all its tiles have no letters on them (None
        is used for empty tiles)
        :return: Boolean True if the board is empty, False
            otherwise
        """
        for row in self.board:
            for tile in row:
                if tile is not None:
                    return False
        return True

    def print_board(self):
        """
        Print the Scrabble board, including the multiplier
        spaces
        """
        for row_index in range(len(self.board)):
            row = self.board[row_index]
            for col_index in range(len(row)):
                tile = row[col_index]
                multiplier = self.multipliers[row_index][col_index]
                if tile is not None:
                    print(tile, sep=' ', end='')
                elif multiplier[0] != "1":
                    alpha_index = multiplier.find(
                        next(filter(str.isalpha, multiplier)))
                    if WORD_MULTIPLIER in multiplier:
                        print(multiplier[0:alpha_index], sep=' ', end='')
                    elif "2" in multiplier[0]:
                        print("@", sep=' ', end='')
                    else:
                        print("#", sep=' ', end='')
                else:
                    print(" ", sep=' ', end='')
            print("", sep='')


my_dictionary = Dictionary()
# my_dictionary.print_dct()
# print("'muzjik' is a word:", my_dictionary.is_word("muzjik"))
#  Use "test_dct.txt" for these tests
# print("'eat' is a word:", my_dictionary.is_word("eat"))
# print("'asdfg' is a word:", my_dictionary.is_word("asdfg"))
# print("The definition of 'eat' is:", my_dictionary.get_def("eat"))
# print("'consume with mouth' is a definition:", my_dictionary.is_defn("consume with mouth"))
# print("'thing that does a thing' is a definition:", my_dictionary.is_defn("thing that does a thing"))
# print("The word corresponding to the definition 'consume with mouth' is:",
#       my_dictionary.get_word_from_def("consume with mouth"))
# print("Words starting with 'OVI':", my_dictionary.get_words_starting_with("OVI"))
# print("Words containing 'AA':", my_dictionary.get_words_containing("AA"))
# print("Words containing 'DJ':", my_dictionary.get_words_containing("DJ"))
# print("Words whose definitions have 'PURPLE' in them:", my_dictionary.get_words_with_x_in_def("purple"))
# print("Words of length 2:", my_dictionary.get_x_letter_words(2))
# print("Anagrams of 'DISASTER':", my_dictionary.find_anagrams("DISASTER"))
# print("Subanagrams of 'CAT':", my_dictionary.find_subanagrams("CAT"))
# print("Subanagrams of 'DISASTER':", my_dictionary.find_subanagrams("DISASTER"))
# print("Subanagrams of 'DISASTER', sorted by length:", my_dictionary.find_subanagrams("DISASTER", True))
# print("Highest scoring 8-letter words, according to Scrabble",
#       "letter distributions:", my_dictionary.get_highest_scoring_words(my_dictionary.get_x_letter_words(8)))
# high_scoring_eight_letter_words = my_dictionary.get_highest_scoring_words(my_dictionary.get_x_letter_words(8))
# high_scoring_right_place_dct = _find_words_of_min_value_at_letter_loc(high_scoring_eight_letter_words, 3, 4, 4)
# high_scoring_no_blanks_right_place = _remove_words_requiring_blank(high_scoring_right_place_dct, LETTER_LIST.copy())
# print("Top four high-scoring eight letter words that have a",
#       "high-scoring tile\n (4 or more points) in the fourth or",
#       "fifth position, that do not require blanks\n and have all",
#       "the tiles needed for all four words:\n",
#       _find_highest_scoring_compatible_words(high_scoring_no_blanks_right_place, 4))
# print("All 15-letter words:", my_dictionary.get_x_letter_words(15))
# h_s_15_l_w_dct = my_dictionary.get_highest_scoring_words(my_dictionary.get_x_letter_words(15))
# eight_letter_words_list = my_dictionary.get_x_letter_words(8)
# h_s_15_min_score_dct = _find_words_of_min_value_at_letter_loc(h_s_15_l_w_dct, 3, 11, 8)
# h_s_15_min_score_has_8s = _remove_words_not_containing_x_letter_word(h_s_15_min_score_dct, eight_letter_words_list)
# print("Highest scoring 15-letter word pairs that have\n",
#       "8s and are alphabetically compatible:",
#       _find_highest_scoring_compatible_words(h_s_15_min_score_has_8s, 2))
# two_letter_words_list = my_dictionary.get_x_letter_words(2)
# three_letter_words_list = my_dictionary.get_x_letter_words(3)
# four_letter_words_list = my_dictionary.get_x_letter_words(4)
# five_letter_words_list = my_dictionary.get_x_letter_words(5)
# six_letter_words_list = my_dictionary.get_x_letter_words(6)
# seven_letter_words_list = my_dictionary.get_x_letter_words(7)
# nine_letter_words_list = my_dictionary.get_x_letter_words(9)
# ten_letter_words_list = my_dictionary.get_x_letter_words(10)
# eight_letter_word_list_overlaps = _find_overlaps(eight_letter_words_list)
# print("Eight letter word overlaps:", eight_letter_word_list_overlaps)
# _find_overlaps(ten_letter_words_list)
# _find_overlaps(two_letter_words_list, 4)
# _get_all_verbs(my_dictionary)
# _create_adjacency_dct(my_dictionary)
# _clean_up_adjacency_file("ADJACENCY_NWL_2023.txt")
# _alphabetize_file("ADJACENCY_NWL_2023.txt")
# _remove_adjacency_subwords("ADJACENCY_NWL_2023.txt")
# _alphabetize_adjacency_words("ADJACENCY_NWL_2023.txt")

scrabble_board = Board(my_dictionary)
# if scrabble_board.is_empty():
#     print("Default board is empty")
# print("Score of the word 'ZIGZAG':", scrabble_board.get_score("ZIGZAG"))
# Test playing word
'''
word_score = scrabble_board.play_word("BROOK", 7, 3, RIGHT)
print("The score of playing 'BROOK' through the double letter",
      "and double word score is:", word_score, "points.")
scrabble_board.print_board()
print("--------------------------------")
# Test intersection
second_word_score = scrabble_board.play_word("JAR", 5, 4, DOWN)
print("The score of playing 'JAR' through the 'R' in",
      "'BROOK' is:", second_word_score, "points.")
scrabble_board.print_board()
print("--------------------------------")
# Test hook, one cross word
word_score = scrabble_board.play_word("ZAS", 5, 8, DOWN)
print("The score of playing 'ZAS', hooking the word 'BROOK'\n",
      "to make 'BROOKS' is:", word_score, "points.")
scrabble_board.print_board()
print("--------------------------------")
# Test invalid intersection
word_score = scrabble_board.play_word("VUG", 5, 2, RIGHT)
if word_score >= 0:
    print("The score of 'VUG' is:", word_score, "points.")
else:
    print("'VUG' cannot be played at this position.")
scrabble_board.print_board()
print("--------------------------------")
# Test playing word hooking in the middle, going downwards
word_score = scrabble_board.play_word("FAR", 4, 3, RIGHT)
print("The score of playing 'FAR' hooking the word 'JAR'\n",
      "to make the word 'AJAR' is:", word_score, "points.")
scrabble_board.print_board()
print("--------------------------------")
# Test multiple cross words
word_score = scrabble_board.play_word("BRO", 8, 5, RIGHT)
print("The score of the word 'BRO' making overlaps 'OB'\n,",
      "'OR', and 'KO' is:", word_score, "points.")
scrabble_board.print_board()
print("--------------------------------")
# Test playing floating word
word_score = scrabble_board.play_word("CAR", 2, 2, RIGHT)
if word_score >= 0:
    print("Car was played successfully. But it should have",
          "failed.")
else:
    print("'CAR' at position 2, 2 does not intersect any\n",
          "other words. It was removed.")
scrabble_board.print_board()
print("--------------------------------")
'''
