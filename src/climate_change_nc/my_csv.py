from pathlib import Path
import csv

DATA_DIR = f"{Path.home()}/.climate_change_nc/data"

class NotReady(Exception):
    pass


class MyCsv:

    def __init__(self, name, logger):
        self.logger = logger
        self.path = f"{DATA_DIR}/{name}.csv"
        self.is_setup = False

        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    def setup(self, columns):
        self.logger.log("Setting up the csv file with the following columns")
        self.logger.log(f'{" | ".join(columns)}')

        if Path(self.path).is_file():
            self.logger.error("The csv file has already been set up")
        else:
            with open(self.path, "w", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()

        self.is_setup = True

    def write_row(self, single_object):
        self.write_rows([single_object])

    def write_rows(self, object_list):
        if not self.is_setup:
            raise NotReady(f"{self.path} csv file is not set up yet. Please run the setup method first.")

        rows = [o.to_list() for o in object_list]

        with open(self.path, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
