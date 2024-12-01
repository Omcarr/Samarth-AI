import difflib
from profanity_db import english_dict, hindi_dict

class TrieNode:
    def __init__(self):
        self.children = {}
        self.isTerminalNode = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def add_word(self, word):
        curr_node = self.root
        for char in word:
            if char not in curr_node.children:
                curr_node.children[char] = TrieNode()
            curr_node = curr_node.children[char]
        curr_node.isTerminalNode = True

    #Determine threshold based on the length of the word.
    def get_dynamic_threshold(self, word_length):
        if word_length<4:
            return 1
        elif 4<word_length<10:
            return 0.9
        return 0.8

    def is_foul(self, word):
        threshold = self.get_dynamic_threshold(len(word))
        candidates = self._collect_candidates()
        
        # Use difflib to find close matches
        matches = difflib.get_close_matches(word, candidates, n=1, cutoff=threshold)
        print(matches)
        return len(matches) > 0

    #Helper method to collect all terminal words into a list
    def _collect_candidates(self):
        candidates = []

        def dfs(node, prefix):
            if node.isTerminalNode:
                candidates.append(prefix)
            for char, child_node in node.children.items():
                dfs(child_node, prefix + char)

        dfs(self.root, "")
        return candidates

#build the trie from systemn maintained dict
def build_trie():
    foul_lang_detector = Trie()
    for word in english_dict:
        foul_lang_detector.add_word(word)
    
    for word in hindi_dict:
        foul_lang_detector.add_word(word)

    return foul_lang_detector

#censors the words
def censor_word(word):
    if len(word) <= 1:
        return "*"  # For a single-letter word
    return word[0] + '*' * (len(word) - 1)  # Keep the first letter and censor the rest

#Detects profanity in the given sentence and returns a censored version.
def profanity_detector(sentence: str, foul_lang_detector: Trie):
    words = sentence.lower().split()
    censored_sentence = [
        censor_word(word) if foul_lang_detector.is_foul(word) else word
        for word in words
    ]
    return ' '.join(censored_sentence)






# def main():
#     foul_lang_detector = build_trie()
    
#     while True:
#         user_input = input("Enter a sentence: ")
#         processed_sentence = profanity_detector(user_input, foul_lang_detector)
        
#         if processed_sentence != user_input:
#             print("Profanity detected! Censored output:", processed_sentence)
#         else:
#             print("Clean input!", processed_sentence)

# if __name__ == '__main__':
#     main()