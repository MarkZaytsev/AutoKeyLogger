import csv
import sys
import glob


class Counter(dict[int, int]):
    def __missing__(self, key):
        return 0

    def merge(self, other: "Counter"):
        for key, value in other.items():
            self[key] += value


# TODO filter by processes list
def read_file(file_name: str) -> dict[str, Counter]:
    with open(file_name, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        result = {}
        for row in reader:
            flag = int(row['Flags'])
            if flag != 0:
                continue

            process = row['Process']
            key_code = int(row['VKey'])
            if process not in result:
                result[process] = Counter()

            result[process][key_code] += 1

    return result


def read_files_in_dir(dir_name: str):
    keys_metrics = Counter()
    for file_name in glob.iglob(f'{dir_name}/*.log', recursive=False):

        print(f'Processing: {file_name}')

        records = read_file(file_name)
        for process, keys_counters in records.items():
            keys_metrics.merge(keys_counters)

    print(f'metrics: {keys_metrics}')


if __name__ == '__main__':
    logs_path = sys.argv[1]
    # processes_to_track = sys.argv[2]
    read_files_in_dir(logs_path)
