"""
Napisz program, w którym budowana będzie lista wylosowanych liczb.
Lista ma zawierać jedynie unikalne liczby.
Zakres oraz długość listy ma być wprowadzona przez użytkownika.
Po etapie losowań należy wyśiwetlić sumę liczb na pozycjach parzystych oraz iloczyn na pozycjach nieparzystych.
"""

import random

a = int(input("Podaj początek zakresu: "))
b = int(input("Podaj koniec zakresu: "))
c = int(input("Podaj długość listy: "))

assert c <= b-a, "Zakres jest za mały"

random_list = random.sample(range(a, b), c)
print("lista: ", random_list)
print("Suma: ", sum(random_list[::2]))
n = 1
print("Iloczyn: ", [n := n * tmp for tmp in random_list[1::2]][-1])