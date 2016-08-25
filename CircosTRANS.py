from datetime import datetime
from os.path import basename, splitext

class CSVDocumentLoader:
    def __init__(self, field_sep=',', line_sep='\n'):
        self.field_sep = field_sep
        self.line_sep = line_sep

    def load(self, filename):
        with open(filename) as doc:
            content = doc.read().replace('\t', ' ').replace('"', '')
        csv_doc = self.parse_csv_document(content)
        csv_doc.name = splitext(basename(filename))[0]
        return csv_doc

    def parse_csv_document(self, content):
        """Przekształcanie postaci tekstowej na postać wygodną (w naszym przypadku to obiekty klasy CSVDocument)"""
        lines = content.split(self.line_sep)
        rows = []
        for line in lines:
            if line.strip():  # linia musi być niepusta
                row = line.split(self.field_sep)
                if row:
                    rows.append(row)
        # rows to lista lista zawierająca teksty
        if len(rows) == 0:
            return CSVDocument([], [])
        elif len(rows) == 1:
            return CSVDocument(rows[0], [])
        else:
            return CSVDocument(rows[0], rows[1:])


class CSVDocument:
    def __init__(self, headers, rows, name='result'):
        """
        Atrybuty:
            headers: to lista (str) nagłówków
            rows: to jest lista list (każda wewnątrz lista to jeden wiersz)
        """
        self.headers = headers
        self.rows = rows
        self.name = name

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

    def make_subdocument(self, indexes):
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
        for row in self.rows:  # obsługa wielu linii
            new_row = []
            for i in indexes:  # obsługa pojedynczej lini
                new_row.append(row[i])
            rows.append(new_row)

        return CSVDocument(headers, rows, self.name)

    def render(self, field_sep=',', line_sep='\n'):
        """Powoduje utworzenie tekstu opisującego dokument.
        Udostępnia możliwość przestawienia separatorów na dowolne znaki.
        """
        lines = [
            field_sep.join(self.headers)  # powstaje nam linia z nagłówkami
        ]
        for row in self.rows:
            lines.append(field_sep.join(row))
        return line_sep.join(lines)

    def sort(self, index):
        self.rows.sort(key=lambda r: r[index])

    def __str__(self):
        return self.render()

    def save(self, filename=None, ext='.csv'):
        with open(self.get_fullname(ext), 'w') as doc:
            doc.write(self.render(' '))

    def get_fullname(self, ext='.csv'):
        return self.name + ext


class CSVNormalizer:

    def normalize(self, csv1, csv2):
        shared_headers = self.get_shared_headers(csv1.headers, csv2.headers)
        header_indexes1 = self.get_header_indexes(csv1.headers, shared_headers)
        header_indexes2 = self.get_header_indexes(csv2.headers, shared_headers)
        print('SHARED_HEADERS', shared_headers)
        print('HEADERS', csv1.headers, csv2.headers)
        subdoc1 = csv1.make_subdocument(header_indexes1)
        subdoc2 = csv2.make_subdocument(header_indexes2)
        return subdoc1, subdoc2

    def get_shared_headers(self, headers1, headers2):
        """Zwraca nam listę z wspólnymi nagłówkami."""
        shared_headers = []
        for header in headers1:
            if header in headers2:
                shared_headers.append(header)
        return shared_headers

    def get_header_indexes(self, headers, selected_headers):
        """Oblicza indeksy bieżących nagłówków.

        Argumenty:
            headers:  Wszystkie nagłówki
            selected_headers: Nagłówki, którymi chcemy teraz operować

        Wynik:
           Zwraca nową listę z indeksami bieżących nagłówków względem wszystkich nagłówków.
        """
        indeksy = []
        for selected_header in selected_headers:
            # tutaj będziemy dodawać elementy do nowej listy
            # za każdym razem jeden indeks
            indeks = headers.index(selected_header)
            indeksy.append(indeks)
        return indeksy


class CircosCSVBuilder:
    BASE_COL_COUNT = 3

    def buildMany(self, csv):
        csv.add_column(2, 'end', self.calculate_plus_100)
        circos_csv_docs = []
        for index in range(self.calculate_file_count(csv)):
            # extra_index to indeks kolumny jaką chcemy przepisać do pliku
            extra_index = self.BASE_COL_COUNT + index  # (3 + 0, 3 + 1)
            sub_doc = csv.make_subdocument(
                [0, 1, 2, extra_index])  # [0, 1, 2, 3], [0, 1, 2, 4]
            sub_doc.name = csv.name + '_' + csv.headers[extra_index]
            circos_csv_docs.append(sub_doc)
        return circos_csv_docs

    def calculate_plus_100(self, row):
        return str(int(row[1]) + 100)

    def calculate_file_count(self, csv):
        return len(csv.headers) - self.BASE_COL_COUNT


def main():
    csv_file_name1 = 'TRANSFcoverage_Oryza_Dagmara_20160415_TEonly.txt'
    csv_file_name2 = 'TRANSFcoverage_Oryza_SR_Dagmara_20160415_TEonly.txt'

    csv_loader = CSVDocumentLoader(field_sep=' ')
    csv1 = csv_loader.load(csv_file_name1)
    csv2 = csv_loader.load(csv_file_name2)
    print('Odczytano pliki')

    csv_normalizer = CSVNormalizer()
    normalized_csv_docs = csv_normalizer.normalize(csv1, csv2)
    print('Przeprowadzono normalizację')

    circos_csv_builder = CircosCSVBuilder()
    for normalized_csv_doc in normalized_csv_docs:
        circos_csv_docs = circos_csv_builder.buildMany(normalized_csv_doc)
        for circos_csv_doc in circos_csv_docs:
            circos_csv_doc.save(ext='.txt')
            print('Zapisano plik: ', circos_csv_doc.get_fullname(ext='.txt'))


main()





