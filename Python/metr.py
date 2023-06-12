import csv
import sys
import glob
from dataclasses import dataclass

keycodes_aliases_file_path = "./KeyCodes.csv"


class Counter(dict[int, int]):
    def __missing__(self, key):
        return 0

    def merge(self, other: "Counter"):
        for key, value in other.items():
            self[key] += value

    def sort_desc(self) -> "Counter":
        return Counter(dict(sorted(self.items(), key=lambda item: item[1], reverse=True)))


@dataclass
class KeyEntry:
    code: int
    name: str
    count: int
    percentage: float


# TODO filter by processes list
def read_logs_in_dir(dir_name: str) -> Counter:
    result = Counter()
    for file_name in glob.iglob(f'{dir_name}/*.log', recursive=False):
        print(f'Processing: {file_name}')

        records = get_records_from_file(file_name)
        for _, keys_counters in records.items():
            result.merge(keys_counters)

    return result


# TODO count all files and show percentage progress
def get_records_from_file(file_name: str) -> dict[str, Counter]:
    with open(file_name, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        result = {}
        for row in reader:
            try:
                flag = int(row['Flags'])
            except TypeError:
                continue

            if flag != 0:
                continue

            process = row['Process']
            key_code = int(row['VKey'])
            if process not in result:
                result[process] = Counter()

            result[process][key_code] += 1

    return result


# TODO map key names
def map_keys(counter: Counter, aliases: dict[int, str]) -> list[KeyEntry]:
    total_keys_count = sum(counter.values()) / 100

    def build(key_code: int, count: int) -> KeyEntry:
        alias = "Unknown Key"
        if key_code in aliases:
            alias = aliases[key_code]

        return KeyEntry(code=key_code, name=alias, count=count,
                        percentage=count / total_keys_count)

    return list(map(lambda kv: build(kv[0], kv[1]), counter.items()))


def read_aliases() -> dict[int, str]:
    with open(keycodes_aliases_file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        result = {}
        for row in reader:
            try:
                key_code = int(row['Value'], base=16)
            except ValueError:
                continue

            alias = row['Description']
            result[key_code] = alias

    return result


def run():
    logs_path = sys.argv[1]
    # processes_to_track = sys.argv[2]
    keys = read_logs_in_dir(logs_path)
    keys_aliases = read_aliases()
    mapped_keys = map_keys(keys.sort_desc(), keys_aliases)
    for k in mapped_keys:
        print(k)


if __name__ == '__main__':
    run()
