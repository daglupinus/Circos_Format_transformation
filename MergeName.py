# zachowujemy BP i nazwe

from itertools import groupby



def by_name(record):
    return record.name

# chr    start    end     name
# a2    16800    16900    ATREP4
# a2    16900    17000    ATREP4
# a2    17000    17100    ATREP3
# a2    17100    17200    ATREP3
# a2    17200    17300    ATREP3
# a2    17300    17400    ATREP3
# a2    17400    17500    ATREP3
# a2    17500    17600    ATREP3
# a2    17600    17700    ATREP3
# a2    17700    17800    ATREP3
# a2    17800    17900    ATREP3
# a2    17900    18000    ATREP3
# a2    18000    18100    ATREP3
# a2    18100    18200    ATREP3
# a2    18200    18300    ATREP3

# a2    18300    18400    ATHATN7|ATREP3
# a2    18400    18500    ATHATN7|ATREP3
# a2    18500    18600    ATHATN7|ATREP3
# a2    18600    18700    ATHATN7|ATREP3

# a2    18700    18800    ATREP3
# a2    18800    18900    ATREP3
# a2    18900    19000    ATREP3


# NOTATKI:
# str.strip -> usuń białe znaki na około


# groupby:
# Argumenty wywołwania:
# 1) zbiór/lista elementów, które mają zostać pogrupowane
# 2) (opcjonalny) funkcja mówiąca względem czego grupujemy
# Wynikiem jest kilka par po który iterujemy,
# a każda para to element grupy oraz sama grupa.
# Dla przykładu:
# [1, 1, 1, 1, 2, 2, 2, 7, 7, 1, 1, 1]
# to wówcz będzie 4 pary, oto one:
# (1, [1, 1, 1])
# (2, [2, 2, 2])
# (7, [7, 7])
# (1, [1, 1, 1])


# MAGIC METHODS!!
# to wszystkie metody, które zaczynają i kończą się dwoma podkreśleniami
# Jawnie się tych metod nie wywołuje.
# Np.
# Jeśli tworzę obiekt wtedy przed jego użyciem uruchomi się pierw metoda __init__.
# Natomiast jeśli będziemy chcieli zmienic obiekt w tekst wtedy wywoła się __str__,
# który ma zwrócić tekstową reprezentacją tego obiektu.

# print(record)
# text = str(record)
# result = "{0} = {1}".format('cos', record)
class Record:

    def __init__(self, chro, bp,  end, name):
        self.chro = chro
        self.bp = bp
        self.end = end
        self.name = name

    def __str__(self):
        """
        Metoda format ona działa na tekście, który jest szablonem.
        To znaczy w miejsce np. {0} lub {1} lub {2} itd
        można osadzić jakieś wartości.

        Używamy metody format głównie po to, żeby unikać mało czytelnych i mało wydajnych zapisów z plusami.
        """
        return '({0}, {1}, {2}, {3})'.format(self.chro, self.bp, self.end, self.name)


# https://docs.python.org/2/library/itertools.html#itertools.groupby
# (2 2 2) (3 3) (2 2 2 2)


def convert_file(input_filename, output_filename):
    with open(input_filename) as document:
        content = document.read()
    lines = content.split('\n')
    records = create_records(lines[1:])
    merged_records = merge_records(records)
    with open(output_filename, 'w') as document:
        output_content = build_output_content(merged_records)
        document.write(output_content)

def create_records(lines):
    """Funkcja zwraca listę stworzonych rekordów na podstawie wszystkich linii.
    """
    records = []
    for line in lines:
        # Ten if chroni przed pustymi liniami.
        if line.strip():
            record = create_record(line)
            records.append(record)
    return records


# a2    11900    12000    ATCO    PIA24
def create_record(line):
    chro, bp, end, name = line.split()
    return Record(chro, bp, end, name)


def merge_records(records):
    new_records = []

    for name, gen_group in groupby(records, by_name):
        group = list(gen_group)  # wyjmujemy wszystkie wartości z generatora do listy
        top_record = group[0]
        bottom_record = group[-1]
        new_record = merge_record(top_record, bottom_record)
        new_records.append(new_record)
    return new_records

def merge_record(top_record, bottom_record):
    return Record(top_record.chro, top_record.bp, bottom_record.end, top_record.name)


def build_output_content(records):
    lines = make_lines(records)
    return '\n'.join(lines)


def make_lines(records):
    lines = []
    for record in records:
        line = make_line(record)
        lines.append(line)
    return lines


def make_line(r):
    return '{0}\t{1}\t{2}\t{3}'.format(r.chro, r.bp, r.end, r.name)



# values = ['aaa', 'aaa', 'aaa', 'bbb', 'b', 'a', 'a', 'ccccc', 'ccccc']
# for letter, group in groupby(values, len):
#     print(letter, list(group))

# r = Record('a', 'b', 'c')
# print('r:', r)

def main():
    convert_file('Arabido_SR1_names.txt', 'SmallArabido_SR1names.txt')
    print('Udało się :)')


main()