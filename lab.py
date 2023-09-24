"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!

import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    prefix tree class
    """

    def __init__(self):
        """ 
        initializes prefix tree
        """
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if not key:
            self.value = value
        else:
            next_letter = key[0]
            other_letters = key[1:]
            if next_letter not in self.children:
                self.children[next_letter] = PrefixTree()
            self.children[next_letter].__setitem__(other_letters, value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if not key:
            return self.value
        else:
            next_letter = key[0]
            if next_letter not in self.children:
                raise KeyError
            other_letters = key[1:]
            return self.children[next_letter].__getitem__(other_letters)

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if not key and self.value is None:
            raise KeyError
        if not key:
            if not self.value:
                raise KeyError
            self.value = None
        else:
            next_letter = key[0]
            if next_letter not in self.children:
                raise KeyError
            other_letters = key[1:]
            try:
                self.children[next_letter].__delitem__(other_letters)
            except KeyError:
                raise KeyError

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        if len(key) == 0:
            if self.value is None:
                return False
            else:
                return True

        else:
            letter = key[0]
            next_letters = key[1:]
            if letter not in self.children.keys():
                return False
            else:
                return self.children[letter].__contains__(next_letters)

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        if not self.children:
            return
        for child in self.children:
            value = self.children[child].value
            if value is not None:
                yield (child, value)
            for pair in self.children[child].__iter__():
                yield (child + pair[0], pair[1])

    def subtree(self, key):
        """
        creates a subtree of tree based off key
        """
        if not key:
            return self
        else:
            letter = key[0]
            next_letters = key[1:]
            if letter not in self.children:
                raise KeyError
            return self.children[letter].subtree(next_letters)


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    if not isinstance(text, str):
        raise TypeError
    tokenized_text = tokenize_sentences(text)
    tree = PrefixTree()
    for sentence in tokenized_text:
        word_list = sentence.split()
        for word in word_list:
            if tree.__contains__(word):
                value = tree.__getitem__(word)
                tree.__setitem__(word, value + 1)
            else:
                tree.__setitem__(word, 1)
    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError
    if max_count == 0:
        return []
    try:
        subtree = tree.subtree(prefix)
    except KeyError:
        return []

    prefix_pairs = [pair for pair in subtree.__iter__()]
    if tree.__getitem__(prefix):
        prefix_pairs.append((prefix, tree.__getitem__(prefix)))

    sorted_list = sorted(prefix_pairs, key=lambda x: x[1], reverse=True)
    result = []
    pairs_to_return = sorted_list
    if max_count:
        index = min(max_count, len(sorted_list))
        pairs_to_return = sorted_list[:index]
    for pair in pairs_to_return:
        if pair[0] != prefix:
            result.append(prefix + pair[0])
        else:
            result.append(pair[0])
    return result


def is_single_character_insertion(word1, word2):
    """ 
    checks for single character insertion 
    """
    if len(word1) + 1 != len(word2):
        return False

    i = 0
    j = 0
    diff = False

    while i < len(word1) and j < len(word2):
        if word1[i] != word2[j]:
            if diff:
                return False
            diff = True
            j += 1
        else:
            i += 1
            j += 1

    return diff


def is_single_character_deletion(word1, word2):
    """ 
    checks for single character deletion
    """
    if len(word1) != len(word2) + 1:
        return False

    for i in range(len(word2)):
        if word1[i] != word2[i]:
            return word1[i + 1 :] == word2[i:]

    return True


def is_single_character_replacement(word1, word2):
    """
    checks for single character replacement
    """
    if len(word1) != len(word2):
        return False
    num_diff = 0
    for i in range(len(word1)):
        if word1[i] != word2[i]:
            num_diff += 1
            if num_diff > 1:
                return False
    return num_diff == 1


def is_two_character_swap(word1, word2):
    """"
    checks for two character swap
    """
    if len(word1) != len(word2):
        return False

    diff_indices = []
    for i in range(len(word1)):
        if word1[i] != word2[i]:
            diff_indices.append(i)

    if len(diff_indices) != 2:
        return False

    i, j = diff_indices
    if word1[i] == word2[j] and word1[j] == word2[i]:
        return True

    return False


def find_valid_edits(tree, prefix, repeat_word_set, max_count=None):
    """
    checks for all valid edits (helper for autocorrect)
    """
    len_min = len(prefix) - 1
    len_max = len(prefix) + 1
    all_pairs = [pair for pair in tree.__iter__() if len_min <= len(pair[0]) <= len_max]
    valid_edits_pairs = []
    for pair in all_pairs:
        word = pair[0]
        if word in repeat_word_set:
            continue
        if should_add_word(prefix, word):
            valid_edits_pairs.append(pair)
    sorted_list = sorted(valid_edits_pairs, key=lambda x: x[1], reverse=True)
    if max_count:
        sorted_list = sorted_list[:max_count]
    result = [pair[0] for pair in sorted_list]
    return result


def should_add_word(prefix, word):
    """
    checks if word is a valid to prefix
    """
    should_add = False
    if len(word) == len(prefix):
        if is_single_character_replacement(prefix, word) or is_two_character_swap(
            prefix, word
        ):
            should_add = True
    elif len(word) == len(prefix) + 1 and is_single_character_insertion(prefix, word):
        should_add = True
    elif len(word) == len(prefix) - 1 and is_single_character_deletion(prefix, word):
        should_add = True
    return should_add


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    if not isinstance(prefix, str):
        raise TypeError
    if max_count == 0:
        return []
    autocomplete_word_list = autocomplete(tree, prefix, max_count)
    if max_count and len(autocomplete_word_list) >= max_count:
        return autocomplete_word_list
    needed_words = None
    if max_count:
        needed_words = max_count - len(autocomplete_word_list)
    autocomplete_word_set = set(autocomplete_word_list)
    valid_edits = find_valid_edits(tree, prefix, autocomplete_word_set, needed_words)
    result = set(autocomplete_word_list + valid_edits)
    return list(result)


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if not isinstance(pattern, str):
        raise TypeError
    if not pattern:
        if tree.value is not None:
            return [("", tree.value)]
        else:
            return []

    character, rest_of_word = pattern[0], pattern[1:]
    if character == "*":
        if rest_of_word and rest_of_word[0] == "*":
            return word_filter(tree, rest_of_word)
        result = set()
        for child in tree.children:
            subwords_list = word_filter(tree.children[child], pattern)
            for subword, value in subwords_list:
                result.add((child + subword, value))
        subwords_list = word_filter(tree, rest_of_word)
        for subword, value in subwords_list:
            result.add((subword, value))
        return list(result)

    elif character == "?":
        result = []
        for child in tree.children:
            subwords_list = word_filter(tree.children[child], rest_of_word)
            for subword, value in subwords_list:
                result.append((child + subword, value))
        return result
    else:
        if character in tree.children:
            subwords_list = word_filter(tree.children[character], rest_of_word)
            result = []
            for subword, value in subwords_list:
                result.append((character + subword, value))
            return result
        else:
            return []


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("alice.txt", encoding="utf-8") as f:
        text = f.read()
        a_tree = word_frequencies(text)
        print(autocorrect(a_tree, "hear", 12))
