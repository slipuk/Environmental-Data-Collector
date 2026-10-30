import pathlib
import json
import csv

from datetime import datetime
from dataclasses import asdict

from ..models.environmental import EnvironmentalModel
from ..service.logger import log

class Writer:
    def __init__(self):
        self.path_to_directory = pathlib.Path("./data/")
        self.path_to_directory.mkdir(parents=True, exist_ok=True)

    def datetime_default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat(timespec="seconds")
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def check_type_support(self, content: list[EnvironmentalModel] | EnvironmentalModel | None):
        if content is None:
            log.message("WARNING", "skipping write: no records provided")
            return
        
        items = content if isinstance(content, list) else [content]
        valid_items = []
        
        for item in items:
            if item is None:
                log.message("WARNING", "skipping write: record is None")
                continue
            if not isinstance(item, EnvironmentalModel):
                log.message(
                    "WARNING",
                    f"skipping write: unsupported type {type(item).__name__}"
                )
                continue
            valid_items.append(item)
        
            if not valid_items:
               log.message("WARNING", "skipping write: no valid records")
               return
        return valid_items

class jsonWriter(Writer):
    def __init__(self):
        super().__init__()
        self.path_to_file = self.path_to_directory / "environmental_data.jsonl"
        self.path_to_file.parent.mkdir(exist_ok=True)
        self.path_to_file.touch(exist_ok=True)

    def write_to_json(self, content: list[EnvironmentalModel] | EnvironmentalModel | None = None):
        valid_items = self.check_type_support(content=content)
        
        with open(self.path_to_file, "a", encoding="utf-8") as json_file:
            for item in valid_items:
                line = json.dumps(asdict(item), default=self.datetime_default, ensure_ascii=False)
                json_file.write(line + "\n")

        log.message("INFO", f"wrote {len(valid_items)} records to {self.path_to_file}")

class csvWriter(Writer):
    def __init__(self):
        super().__init__()
        self.path_to_file = self.path_to_directory / "environmental_data.csv"
        self.path_to_file.parent.mkdir(exist_ok=True)
        self.path_to_file.touch(exist_ok=True)
        self.initialise_csv_table()

    def initialise_csv_table(self):
        with open(self.path_to_file, "a+", encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file)
            csv_file.seek(0)
            headers = list(EnvironmentalModel.__dataclass_fields__)

            if next(reader, None) == headers:
                return

            writer = csv.writer(csv_file)
            writer.writerow(headers)
            
    def parse_model_to_csv_columns(self, model_list: list[EnvironmentalModel]):
        return [self.datetime_default(value) if isinstance(value, datetime) else value for value in [asdict(model).values() for model in model_list]]

    def write_to_csv(self, content: list[EnvironmentalModel] | EnvironmentalModel | None = None):
        valid_items = self.check_type_support(content=content)

        with open(self.path_to_file, "a", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerows(self.parse_model_to_csv_columns(valid_items))

json_writer = jsonWriter()
csv_writer = csvWriter()