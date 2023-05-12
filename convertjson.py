import argparse
import json
from datetime import datetime, timedelta


def get(filename):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            obj = json.loads(line)
            yield obj

def transform(objs):
    for obj in objs:
        for k, data in obj.items():
            startDate = datetime.fromisoformat(data["st"])
            endDate = startDate + timedelta(minutes=int(data["du"]))
            data["en"] = endDate.isoformat()
            del data["du"]
        yield obj


def convert(objs):
    for obj in objs:
        yield json.dumps(obj)


def write(filename, strings):
    with open(filename, mode='w') as f:
        for s in strings:
            f.write(s + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

write(args.output, convert(transform(get(args.input))))
