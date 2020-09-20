import argparse
from collections import Counter
import re
import random
from typing import Dict, List
import pickle


class Model:
    def __init__(self):
        self.dict: Dict[str, Counter] = {}
        self.file_name = None
        self.results: List[List[str]] = []
        self.most_common_word = None

    def fit(self, file_name: str):
        self.file_name = file_name
        next_word = ''
        with open(file_name, encoding="utf8") as f:
            for line in f:
                words = self.__clear(line).split()
                if next_word and words:
                    if next_word not in self.dict:
                        self.dict[next_word] = Counter()
                    self.dict[next_word][words[0]] += 1
                for i in range(len(words) - 1):
                    word = words[i]
                    next_word = words[i + 1]
                    if word not in self.dict:
                        self.dict[word] = Counter()
                    self.dict[word][next_word] += 1
        self.most_common_word = max(self.dict,
                                    key=lambda x:
                                    sum(self.dict[x][w]
                                        for w in self.dict[x]))

    def generate(self, length: int, first_word) -> str:
        result = []
        if first_word not in self.dict:
            raise ValueError("First word is absent from the model")
        if not first_word:
            current_word = self.most_common_word
        else:
            current_word = first_word
        result.append(current_word)
        for i in range(length):
            words = list(self.dict[current_word].keys())
            weights = [self.dict[current_word][word] for word in words]
            next_word = random.choices(
                words,
                k=1,
                weights=weights)[0]
            result.append(next_word)
            current_word = next_word

        self.results.append(result)
        return " ".join(result)

    def __clear(self, string: str) -> str:
        return re.sub(r'[^\w\'-]', " ", string.lower())


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple text generator by 2-gram language model")
    parser.add_argument('--fit', nargs='+', default=None,
                        help='Path to text files for fit')
    parser.add_argument('--generate', default=None, nargs=2,
                        help="Length of generated file, path for save result")
    parser.add_argument('--first_word', '-fw', default=None,
                        help="First word in generated sequence")
    parser.add_argument('--save', default=None,
                        help="Path for save model by pickle")
    parser.add_argument('--load', default=None,
                        help='Path to saved model by pickle')
    return parser.parse_args()


if __name__ == "__main__":
    args = arg_parser()
    if args.load:
        with open(args.load, 'rb') as f:
            model = pickle.load(f)
    else:
        model = Model()
    if args.fit:
        for file in args.fit:
            model.fit(file)
    if args.generate:
        length, result_path = args.generate
        with open(result_path, 'w+', encoding='utf8') as f:
            f.write(model.generate(int(length), args.first_word))
    if args.save:
        with open(args.save, 'wb+') as f:
            pickle.dump(model, f)
