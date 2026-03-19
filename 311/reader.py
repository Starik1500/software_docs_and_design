import csv

class DataReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_data(self):
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                yield row