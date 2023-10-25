"""
Napisz program, w którym budowana będzie lista wylosowanych liczb.
Zdefiniuj metody odpowiadające operatorom matematycznym, których wyniki będą zapisywane w nowej liście,
oraz metodę wypisującą zawartość tej listy. W krotce zapisane będą funkcje wykonujące działania matematyczne i wypisywanie wartości
Dla każdej kolejnej pary liczb z listy wylosowanych liczb wylosuj z krotki metodę i ją wykonaj. Po wylosowaniu wypisywania
należy się zatrzymać i nie przechodzić do kolejnej pary liczb, dopóki nie zostanie na nich wykonane odpowiednie działanie.
"""
import random
import datetime

now = datetime.datetime.now()
answers = []
n = int(input("Podaj długość listy liczb: "))
numbers = [random.randint(0,1000) for i in range(n)]


def dodaj(a, b):
    global answers
    answers.append(a + b)
    return a + b


def usun(a, b):
    global answers
    answers.append(a - b)
    return a - b


def pomnoz(a, b):
    global answers
    answers.append(a * b)
    return a * b


def podziel(a, b):
    global answers
    answers.append(a // b)
    return a // b


def pisz(*args):
    global i, answers, numbers
    print(f"Aktualnie przeliczone wyniki ({i}/{len(numbers)} liczb)", answers)


operations = (dodaj, usun, pomnoz, podziel, pisz)

done_operations = []
i = 0
while i < len(numbers):
    a, b = numbers[i:i+2]
    (operation := random.choice(operations))(a, b)
    done_operations.append({"Operation": operation,
                            "Numbers": (a, b),
                            "Result": answers[-1] if operation != pisz else "N/A"})
    if operation != pisz:
        i += 2

print(f"Done! (in {(datetime.datetime.now() - now).total_seconds()}s)")
pisz()