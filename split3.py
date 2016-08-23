# # CHR    BP        TE_Quesneville    CG    CT    eG    nG    nT    CF    nF
# # 1    11900    12000    ATCOPIA24    0    0    0    0    0    0    0.673143654914252
# # 1    16800    16900    ATREP4    0    0    0    0    0    0    0.673143654914252
# # 1    17000    17100    ATREP3    0    0    0    0    0    0    0
# # 1    17100    17200    ATREP3    0    0    0    0    0    0    0
# # 1    17200    17300    ATREP3    0    0    0    0    0    0    0
# # 1    17300    17400    ATREP3    0    0    0    0    0    0    0
# # 1    17400    17500    ATREP3    0    0    0    0    0    0.704228823663215    0
# # 1    17600    17700    ATREP3    0    0    0    0    0    0    0
# # 1    17700    17800    ATREP3    0    0    0    0    0    0.704228823663215    0
# # 1    17800    17900    ATREP3    0    0    0    0    0    0.704228823663215    0
# # 1    17900    18000    ATREP3    0    0    0    0    0    0.704228823663215    0.336571827457126


# #                                      (szybko)                                      (troszke)                              (szybko)
# # dane -> python -> 4 + 1 -> sortowanie(wzgledem ostatniej kolumny) -> wykrywamy przeskok (2 razy wiekszy niz srednia) -> ucinamy -> zapisujemy
# def load_csv_document(file_name, field_sep, line_sep):
#     with open(file_name) as document:
#         content = document.read()
#     return parse_csv_document(content, field_sep, line_sep)


# # 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 100,  100, 100, 1000

#  number = float(number)
# UnboundLocalError: local variable 'number' referenced before assignment

import math

def calculate_level(x):
    number = float(x)
    if number:
        return math.log10(number)
    return 0


def parse_csv_document(content, field_sep, line_sep):
    """Przekształcanie postaci tekstowej na postać wygodną (w naszym przypadku to obiekty klasy CSVDocument)"""
    lines = content.split(line_sep)
    rows = []
    for line in lines:
        if line.strip(): # linia musi być niepusta
            row = line.split(field_sep)
            rows.append(row)
    # rows to lista lista zawierająca teksty
    if len(rows) == 0:
        return CSVDocument([], [])
    elif len(rows) == 1:
        return CSVDocument(rows[0], [])
    else:
        return CSVDocument(rows[0], rows[1:])


# 0, 3,5,8,10,50,99,100,120    ,500,900,4000,20000


class NumberDetector:

    def __init__(self, factor=1.25):
        self.total_sum = 0
        self.count = 0
        self.factor = factor

    def add(self, number):
        self.total_sum += float(number)
        self.count += 1

    def should_add(self, number):
        avg = self.calculate_avg()
        if avg is None or avg == 0:
            return True
        if avg > 0 and avg * self.factor > float(number):
            return True
        return False

    def calculate_avg(self):
        if self.count == 0:
            return None
        return self.total_sum / self.count


class CSVDocument:

    def __init__(self, headers, rows):
        """
        Atrybuty:
            headers: to lista (str) nagłówków
            rows: to jest lista list (każda wewnątrz lista to jeden wiersz)
        """
        self.headers = headers
        self.rows = rows

    def add_column(self, index, header, calculate):
        """Dodaje kolumnę.

        Argumenty:
            index: Wskazuje nam miejsce, gdzie ma zostać osadzona kolumna.
            header: Nagłówek dla nowej kolumny.
            calculate: Funkcja, która jako argument przyjmuje wiersz i na tej podstawie produkuje wynik dla nowej kolumny.
        """
        self.headers.insert(index, header)
        # Na podstawie każdego rzędu tworzymy jedną wartość, która stanowi podstawę do zbudowania kolumny.

        for row in self.rows:
            value = calculate(row)
            row.insert(index, value)


    def make_subdocument_by_indexes(self, indexes):
        """Tworzymy dokumnet z wybranymi kolumnami.

        Argumenty:
            indexes: Indeksy kolumn, które mają zostać dołączone do nowego dokumentu.
        """
        # selekcja nagłówków na podstawie indeksów
        headers = []
        for i in indexes:
            header = self.headers[i]
            headers.append(header)

        # selekcja wartości na podstawie indeksów
        # czyli każdy wiersz będzie przetworzony
        # i z każdego wiersza wybieramy to co nas interesuje (patrz na indeksy).
        rows = []
        for row in self.rows:   # obsługa wielu linii
            new_row = []
            for i in indexes:   # obsługa pojedynczej lini
                new_row.append(row[i])
            rows.append(new_row)

        return CSVDocument(headers, rows)


    def make_subdocument_by_avg(self, index):
        detector = NumberDetector()
        rows = []
        for row in self.rows:   # obsługa wielu linii
            value = row[index]
            # print(index, row)
            if detector.should_add(value):
                detector.add(value)
                rows.append(row)
            else:
                print('PRZYCINAMY', value)
                break
        return CSVDocument(self.headers, rows)

    def make_subdocument_by_last_value(self, index, delta_level):
        if not self.rows:
            return CSVDocument(self.headers, [])

        rows = []
        max_number_level = calculate_level(self.rows[-1][index])

        for row in self.rows[::-1]:
            if calculate_level(row[index]) + delta_level >= max_number_level:
                rows.append(row)
            else:
                break

        return CSVDocument(self.headers, rows[::-1])


    def render(self, field_sep=',', line_sep='\n'):
        """Powoduje utworzenie tekstu opisującego dokument.
        Udostępnia możliwość przestawienia separatorów na dowolne znaki.
        """
        lines = [
            field_sep.join(self.headers)    # powstaje nam linia z nagłówkami
        ]
        for row in self.rows:
            lines.append(field_sep.join(row))
        return line_sep.join(lines)

    def sort(self, index):

        def foo(r):
            try:
                return float(r[index])
            except ValueError:
                print(r, index)
                import sys
                sys.exit(1)

        self.rows.sort(key=foo)
        # self.rows.sort(key=lambda r: float(r[index]))


    def __str__(self):
        return self.render()


doc = CSVDocument(
    headers=['A', 'B', 'C'],
    rows=[
        ['10', '20', '30'],
        ['0', '1', '3'],
        ['7', '13', '2']
    ]
)


def calculate_plus_100(row):
    try:
        return str(int(row[1]) + 100)
    except ValueError:
        print(row)
        import sys
        sys.exit(1)

BASE_COL_COUNT = 3
BASE_COL_COUNT_AVG = 4

def build_filename(file_name, col_name):
    basename, extension = file_name.split('.')
    return '{0}_{1}.{2}'.format(basename, col_name, extension)


def save_document(file_name, csv_doc):
    with open(file_name, 'w') as doc:
        doc.write(csv_doc.render(' '))


def build_sub_files(file_name, doc):
    """Tworzy różne kombinacje plików"""
    # obliczamy ilosć kolumn, a zarazem plików jakie chcemy przetworzyć
    file_count = len(doc.headers) - BASE_COL_COUNT  # 2
    for index in range(file_count):  # [0, 1, ....]
        # extra_index to indeks kolumny jaką chcemy przepisać do pliku
        extra_index = BASE_COL_COUNT + index  # (3 + 0, 3 + 1)

        sub_doc = doc.make_subdocument_by_indexes([0, 1, 2, extra_index])   # [0, 1, 2, 3], [0, 1, 2, 4]
        col_name = doc.headers[extra_index]
        new_file_name = build_filename(file_name, col_name)
        save_document(new_file_name, sub_doc)


def build_sub_files_avg(file_name, doc):
    """Tworzy różne kombinacje plików"""
    # obliczamy ilosć kolumn, a zarazem plików jakie chcemy przetworzyć
    file_count = len(doc.headers) - BASE_COL_COUNT_AVG  # 2
    print('Przed1', doc.rows[-1])
    print('FILE_COUNT', file_count)
    for index in range(file_count):  # [0, 1, ....]
        # extra_index to indeks kolumny jaką chcemy przepisać do pliku
        extra_index = BASE_COL_COUNT_AVG + index  # (3 + 0, 3 + 1)
        print('EXTRA_INDEX', extra_index)
        print('POWINNO BYĆ OK', doc.rows[-1])  # OK
        sub_doc = doc.make_subdocument_by_indexes([0, 1, 2, 3, extra_index])   # [0, 1, 2, 3], [0, 1, 2, 4]
        print('POWINNO BYĆ ŹLE', sub_doc.rows[-1]) # ZLE!!
        new_extra_index = len(doc.headers) - 1
        print('PRZED sort')
        sub_doc.sort(new_extra_index)
        print('PO sort')
        # print(sub_doc.rows[1])
        # print(sub_doc.rows[2])
        # print(new_extra_index)
        valid_doc = sub_doc.make_subdocument_by_last_value(new_extra_index, delta_level=1)
        print('Zbudowano doc względem avg')
        final_doc = valid_doc
        # final_doc = valid_doc.make_subdocument_by_indexes([0, 1, 2, 3])
        print('Ucięto zbędną kolumnę')
        col_name = doc.headers[extra_index]
        new_file_name = build_filename(file_name, col_name)
        print('TERAZ ZAPISYWNAIE:', new_file_name)
        save_document(new_file_name, final_doc)


# def process_file(file_name):
#     """Przetwarzamy wybrany plik"""
#     with open(file_name) as document:
#         content = document.read().replace('\t', ' ').replace('"', '')
#     csv_doc = parse_csv_document(content, ' ', '\n')
#     csv_doc.add_column(2, 'end', calculate_plus_100)
#     build_sub_files(file_name, csv_doc)


def process_file_avg(file_name):
    """Przetwarzamy wybrany plik"""
    with open(file_name) as document:
        content = document.read().replace('\t', ' ').replace('"', '')
    csv_doc = parse_csv_document(content, ' ', '\n')
    print('PrzedPrzed1', csv_doc.rows[-1])
    csv_doc.add_column(2, 'end', calculate_plus_100)
    print('PrzedPrzed2', csv_doc.rows[-1])
    print('TERAZ BUDOWANIE')
    build_sub_files_avg('avg_' + file_name, csv_doc)


def main(file_names):
    """Wiele plików przetwarzamy."""
    for file_name in file_names:
        process_file_avg(file_name)

main(['NamesArabido_SR1CF.txt'])
# main(['coverage_Arabido_SR_20160329_247860_TEonly.txt'])

# values = ['A', 'b', 'c', 'd']

# values.insert(2, 'F')
# print(values)




