import json
import re
import os
from symspellpy import SymSpell, Verbosity

# алгоритм левенштейна
def my_levenshtein(first: str, second: str) -> int:
    n = len(first) + 1
    m = len(second) + 1
    a = [([0] * n) for _ in range(m)]
    
    # изначалаьное заполнение матрицы
    for i in range(m):
        for j in range(n):
            if i == 0 and j != 0:
                a[i][j] = a[i][j - 1] + 1
            elif j == 0 and i != 0:
                a[i][j] = a[i - 1][j] + 1
    
    # основной алгоритм
    for i in range(1, m):
        for j in range(1, n):
            if second[i - 1].lower() != first[j - 1].lower():
                a[i][j] = min(a[i][j-1], a[i-1][j], a[i-1][j-1]) + 1
            else:
                a[i][j] = min(a[i][j-1], a[i-1][j], a[i-1][j-1])
    
    # вывод матрицы
    # for i in range(1, m):
    #     print(a[i][1:])
    
    return a[i][j]
    
def levenshtein(first: str, second: str) -> int:
    if len(first) > len(second):
        first, second = second, first
    
    m, n = len(first), len(second)
    
    prev_row = list(range(m + 1))
    curr_row = [0] * (m + 1)
    
    for i in range(1, n + 1):
        curr_row[0] = i
        for j in range(1, m + 1):
            if first[j - 1].lower() == second[i - 1].lower():
                curr_row[j] = prev_row[j - 1]
            else:
                curr_row[j] = min(
                    curr_row[j - 1] + 1,  # Insertion
                    prev_row[j] + 1,      # Deletion
                    prev_row[j - 1] + 1   # Substitution
                )
        # Swap rows for next iteration
        prev_row, curr_row = curr_row, prev_row
    
    return prev_row[m]    

# поиск ближайшего слова
def finder(s: str, path: str):
    m = 10 ** 4
    ans = ''
    with open(path) as f:
        words = [word.rstrip() for word  in f.readlines()]
        if s.lower() in words:
            return s
        for elem in words:
            res = levenshtein(s, elem)
            if min(res, m) == res:
                ans = elem
                m = res
        return ans
    
def is_word(s: str) -> bool:
    # Проверяет, что строка содержит только буквы кириллицы или дефисы и имеет хотя бы одну букву
    return bool(re.match(r'^[а-яА-Я\-]*[а-яА-Я][а-яА-Я\-]*$', s))

def merge_words(words: list[str]) -> list[str]:
    # Возвращает новый список, объединяя слова, где первое заканчивается на дефис
    result = []
    i = 0
    while i < len(words):
        if not is_word(words[i]):
            result.append(words[i])
            i += 1
            continue
        if words[i].endswith('-') and i + 1 < len(words) and is_word(words[i + 1]):
            merged_word = words[i][:-1] + words[i + 1]
            if is_word(merged_word):
                result.append(merged_word)
                i += 2  # Пропускаем два слова
            else:
                result.append(words[i])
                i += 1
        else:
            result.append(words[i])
            i += 1
    return result

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        main_text = data["data"]["text"]
        ans1 = [elem.rstrip().strip('.') for elem in main_text.split()]
        ans2 = [elem for elem in ans1 if is_word(elem)]
        text = merge_words(ans2)
    return text

def finder_symspell(word: str, sym_spell: SymSpell, max_edit_distance: int = 3) -> str:
    word_lower = word.lower()
    suggestions = sym_spell.lookup(word_lower, Verbosity.TOP, max_edit_distance=0)
    if suggestions:
        return word
    suggestions = sym_spell.lookup(word_lower, Verbosity.TOP, max_edit_distance)
    if suggestions:
        return suggestions[0].term
    return word_lower

def init_symspell(path: str, max_edit_distance: int = 3) -> SymSpell:
    sym_spell = SymSpell(max_dictionary_edit_distance=max_edit_distance)
    with open(path, 'r', encoding='utf-8') as f:
        for word in f:
            word = word.rstrip()
            if is_word(word):
                sym_spell.create_dictionary_entry(word, 1)
    return sym_spell

def func(json_path, sym_spell):
    text = read_json(json_path)
    edit_dict = dict()
    for word in text:
        cor = finder_symspell(word, sym_spell)
        if word != cor:
            edit_dict[word] = cor

    with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            main_text = data["data"]["text"]
        
    for key, value in edit_dict.items():
        main_text = main_text.replace(key, value)

    with open(json_path + ".txt", 'w') as f:
        f.write(main_text)



folder_path = "./school"

sym_spell = init_symspell('russian.txt')
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        func(file_path, sym_spell)
