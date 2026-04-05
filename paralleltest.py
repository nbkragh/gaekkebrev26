from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from collections import defaultdict
from multiprocessing import freeze_support
from time import perf_counter



def generate_seeds(pruning, cryptoWords, indexAndPatternDKLexicon, split_depth = 2, min_pass_ratio=0.4):
    seeds = [({}, 0)]  # (mapping, index)
    wordsByLetter = build_words_by_letter(cryptoWords)

    for i in range(min(split_depth, len(pruning))):
        letter, candidates = pruning[i]
        next_seeds = []
        for mapping, _ in seeds:
            for c in candidates:
                mappingCopy = mapping.copy()
                mappingCopy[letter] = c
                affected_words = wordsByLetter.get(letter, [])
                if not affected_words:
                    next_seeds.append((mappingCopy, i + 1))
                    continue

                passed = 0
                for cryptoWord in affected_words:
                    if len(verifyDanishWords(cryptoWord, mappingCopy, indexAndPatternDKLexicon)) > 0:
                        passed += 1

                if (passed / len(affected_words)) >= min_pass_ratio:
                    next_seeds.append((mappingCopy, i + 1))
        seeds = next_seeds
        if not seeds:
            break
    print(f"{len(seeds)} seeds.")
    return seeds

def worker_search(args):
    cryptoWords, pruning, mapping, index, indexAndPatternDKLexicon, wordsByLetter = args
    # kald din eksisterende searchWords herfra
    return searchWords(cryptoWords, pruning, index, mapping, indexAndPatternDKLexicon, wordsByLetter)

def parallel_search(cryptoWords, pruning, indexAndPatternDKLexicon):
    seeds = generate_seeds(pruning, cryptoWords, indexAndPatternDKLexicon)
    if not seeds:
        return []
    wordsByLetter = build_words_by_letter(cryptoWords)
    all_results = []
    seen = set()

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        futures = [
            ex.submit(worker_search, (cryptoWords, pruning, mapping, index, indexAndPatternDKLexicon, wordsByLetter)) for mapping, index in seeds
        ]
        for future in as_completed(futures):
            res = future.result()
            if res is None:
                continue
            key = tuple(sorted(res.items()))
            if key in seen:
                continue
            seen.add(key)
            all_results.append(res)
    return all_results


def decrypt(mapping, cryptoWords,  indexAndPatternDKLexicon, singleOccurences,maxAlternatives=12):
    decodedWithAlter = []
    for cryptoWord in cryptoWords:
        base_decoded = "".join(mapping.get(c, c) for c in cryptoWord)
        alternatives = sorted(set(findAlternativesForAmbiguousWords(cryptoWord, mapping, indexAndPatternDKLexicon, singleOccurences)))
        if not alternatives:
            decodedWithAlter.append(base_decoded)
            continue

        if len(alternatives) > maxAlternatives:
            alternatives = alternatives[:maxAlternatives] + ["..."]

        if len(alternatives) == 1:
            decodedWithAlter.append(alternatives[0])
        else:
            decodedWithAlter.append("/".join(alternatives))

    return decodedWithAlter

def findAlternativesForAmbiguousWords(cryptoWord, mapping, indexAndPatternDKLexicon, singleOccurences):
    seen = {}
    counter = 0
    pattern = []
    for letter in cryptoWord:
        if letter not in seen:
            seen[letter] = counter
            counter += 1
        pattern.append(seen[letter])
    key = (len(cryptoWord), tuple(pattern))
    alternatives = []
    for DanishWord in indexAndPatternDKLexicon[key]:
        good = True
        for cryptoLetter, danishLetter in zip(cryptoWord, DanishWord):
            if (mapping[cryptoLetter] is not None and mapping[cryptoLetter] != danishLetter)and (cryptoLetter not in singleOccurences):
                    good = False
                    break
        if good:
            alternatives.append(DanishWord)
    return alternatives

def findDanishLettersForCryptoWord(cryptoWord, indexAndPatternDKLexicon, cipherFrequencySortedList, danishFrequency):
    mappedCryptoWord = dict((c, set()) for c in cryptoWord)
    for cipher in cipherFrequencySortedList:
        if cipher in cryptoWord:
            seen = {}
            enthropy = 0
            pattern = []
            for cryptoLetter in cryptoWord:
                fixedPositions = [(i, cipher) for i, cl in enumerate(cryptoWord) if cl == cipher]
                # The lexicon index uses structural patterns only, so lookup must do the same.
                if cryptoLetter not in seen:
                    seen[cryptoLetter] = enthropy
                    enthropy += 1
                pattern.append(seen[cryptoLetter])
            key = (len(cryptoWord), tuple(pattern))
            danishWords = indexAndPatternDKLexicon[key]
            for danishWord in danishWords:
                for i, (c, d) in enumerate(zip(cryptoWord, danishWord)):
                    if d in danishFrequency and any(i == j and c == cipher for j, cipher in fixedPositions):
                        if c not in mappedCryptoWord:
                            mappedCryptoWord[c] = set()
                        mappedCryptoWord[c].add(d)
    return mappedCryptoWord

def verifyDanishWords(cryptoWord, mapping, indexAndPatternDKLexicon):
    seen = {}
    counter = 0
    pattern = []
    # building a pattern for the word to search faster
    for letter in cryptoWord:
        if letter not in seen:
            seen[letter] = counter
            counter += 1
        pattern.append(seen[letter])
    key = (len(cryptoWord), tuple(pattern))
    verifiedDanishWords = []
    usedDanishLetters = set(mapping.values())
    for DanishWord in indexAndPatternDKLexicon[key]:
        good = True
        for cryptoLetter, danishLetter in zip(cryptoWord, DanishWord):
            mapped = mapping.get(cryptoLetter)
            if mapped is not None:
                # This crypto letter is already mapped. It must match.
                if mapped != danishLetter:
                    good = False
                    break
            else:
                # This crypto letter is unmapped.
                # Check if this would create a many-to-one mapping (two crypto → same Danish)
                if danishLetter in usedDanishLetters:
                    good = False
                    break
        if good:
            verifiedDanishWords.append(DanishWord)
    return verifiedDanishWords

# for faster search 
def build_words_by_letter(cryptoWords):
    wordsByLetter = defaultdict(list)
    for cryptoWord in cryptoWords:
        for letter in set(cryptoWord):
            wordsByLetter[letter].append(cryptoWord)
    return wordsByLetter


def searchWords(cryptoWords, pruning, index, mapping, indexAndPatternDKLexicon, wordsByLetter=None):
    if index >= len(pruning):
        return mapping
    
    mappingLetter, candidates = pruning[index]
    best_result = None
    best_score = 0

    for candidate in candidates:
        testMapping = mapping.copy()
        testMapping[mappingLetter] = candidate
        good = True
        for cryptoWord in wordsByLetter.get(mappingLetter, []):
            verifiedWords = verifyDanishWords(cryptoWord, testMapping, indexAndPatternDKLexicon)
            if len(verifiedWords) <= 0:
                good = False
                break
        if not good:
            continue
        result = searchWords(cryptoWords, pruning, index + 1, testMapping, indexAndPatternDKLexicon, wordsByLetter)
        
        if result is not None:
            score = 0
            for cryptoWord in cryptoWords:
                score += sum(1 for c in cryptoWord if c in mapping)
            if score > best_score:
                best_score = score
                best_result = result
    return best_result

def pruneCandidates(candidateWords, danishFrequency):
    candidateAlphabet = dict()
    for letter, candidates in candidateWords:
            candidateAlphabet[letter] = candidateAlphabet.get(letter, set(danishFrequency.copy())) & candidates
    return candidateAlphabet

def findCandidateList(cryptoWords, indexAndPatternDKLexicon, cipherFrequencySortedList, danishFrequency):
    mappedCryptoWords = list()
    letterFrequency = defaultdict(int)
    for cryptoWord in cryptoWords:
        for letter, candidates in findDanishLettersForCryptoWord(cryptoWord, indexAndPatternDKLexicon, cipherFrequencySortedList, danishFrequency).items():
            mappedCryptoWords.append((letter, candidates))
            letterFrequency[letter] += 1

    return mappedCryptoWords, letterFrequency


def main():
    allDanishWordsSet = list()

    with open("words.txt", encoding="utf-8") as f:
        for line in f:
            ord = line.strip("\n")
            if len(ord) > 2 or (len(ord) == 1 and ord in ["I","Ø","Å"," "]) or (len(ord) == 2 and any(c in "AEIOUYÆØÅ" for c in ord)):
                allDanishWordsSet.append(ord)
    indexAndPatternDKLexicon = defaultdict(list)
    for word in allDanishWordsSet:
        seen = {}
        counter = 0
        pattern = []
        # søge pattern til hurig søgning i lexikonet
        for letter in word:
            if letter not in seen:
                seen[letter] = counter
                counter += 1
            pattern.append(seen[letter])

        key = (len(word), tuple(pattern))
        indexAndPatternDKLexicon[key].append(word)

    with open("input.txt", encoding="utf-8") as f:
        textRaw = f.read()
        textPages = textRaw.split("\n\n")
        for page in range(len(textPages)):
            textPages[page] = "".join(textPages[page].splitlines())
    cipherFrequencyDict = dict()

    for cipher in "".join(textPages):
        if cipher not in cipherFrequencyDict:
            cipherFrequencyDict[cipher] = 0
        if cipher in "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ":
            cipherFrequencyDict[cipher] += 1

    
    cipherFrequencySortedDict = dict(sorted(cipherFrequencyDict.items(), key=lambda item: item[1], reverse=True))
    cipherFrequencySortedList = list(cipherFrequencySortedDict.keys())
    for cipher in cipherFrequencySortedList[:1]: # testing only  D = " "
        spacedCryptoText = []
        for page in textPages:
            # mapper alle tilfælde af ciffer der skal mappes til " " og deler op i ord
            spacedCryptoText.extend(page.replace(cipher, " ").split()) # 'ABC', 'EFGB', 'GAHIJB', 'KC', 'LEKJGB', 'GBL', 'MLNE', 'OBG', 'OPJBGB', 'HC', 'QRGBR', 'OQR', 'MSHTRB', 'TJBI', 'UVPRQG', 'PJPR', 'LWEQRC', 'GPWPJKCQBRM', 'XPGBE', 'BRUKGBG', 'Q', 'PMUQQ'
        spacedCryptoTextSorted = sorted(spacedCryptoText,key=len, reverse=True) 
    
    #danske bogstaver sorteret efter brug i skriftsproget
    danishFrequency = ['E','N','R','A','I','T','S','D','L','O','G','M','K','F','V','U','B','H','P','Å','Æ','J','Ø','Y','C','W','Z','X','Q']

    candidatList, letterFrequency = findCandidateList(spacedCryptoText, indexAndPatternDKLexicon, cipherFrequencySortedList, danishFrequency)

    singleOccurences = [letter for letter, freq in letterFrequency.items() if freq == 1]
    pruned = pruneCandidates(candidatList, danishFrequency)
    letterFrequencyInCrypto = defaultdict(int)
    for word in spacedCryptoText:
        for letter in word:
            letterFrequencyInCrypto[letter] += 1


    sortedPruning = sorted(pruned.items(), key=lambda item: len(item[1]))
    start = perf_counter()
    
    results = parallel_search(spacedCryptoTextSorted,sortedPruning,indexAndPatternDKLexicon)
    
    elapsed = perf_counter() - start

    if not results:
        print(f"Ingen løsning fundet. Tid: {elapsed:.2f}s")
    else:
        print(f"Antager at 'D' = ' ' ")
        print(f":Enkelt forekommende bogstaver:  {singleOccurences}")
        print(f"Mapping fundet:\n{results}")
        print(f"Dekryptering:\n{decrypt(results[0],spacedCryptoText,indexAndPatternDKLexicon,singleOccurences)}")
        

        print(f"Tid: {elapsed:.2f}s")

if __name__ == "__main__":
    if os.name == 'nt': # Windows
        freeze_support()   # vigtig på Windows
    main()