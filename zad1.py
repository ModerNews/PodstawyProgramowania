import random
import datetime

months = {}
values = list(range(1, 13))

for i in range(1, 13):
    possible_values = list(set(values.copy()) - set(months.keys()))  # Klucze nie powinny się pokrywać. Pythonowa lista nie definiuje różnicy zbiorów, dlatego trzeba użyć setów.
    tmp = random.randint(0, len(possible_values))
    months[tmp] = datetime.date(2020, i, 1).strftime('%B')  # %B - nazwa miesiąca, zgodna z systemowym locale


key = int(input('Podaj swoją liczbę: '))
print(f"Twój miesiąc: {months[key]}")
