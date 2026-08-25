import csv
from collections import Counter


def tally(path, column):
    """回傳指定欄位的值出現次數，由多到少排序。"""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if column not in (reader.fieldnames or []):
            raise KeyError(column)
        return Counter(row[column] for row in reader).most_common()
