import argparse
import json

# This script extracts just notes as html. No notebooks, topics or tags.

parser = argparse.ArgumentParser(description="Extract html notes from a notesnook backup")
parser.add_argument("backupfile", action="store")
args = parser.parse_args()

with open(args.backupfile, mode="rt") as f:
    data = json.load(f)["data"]

    for note_id in data["notes"]:
        note = data[f"{note_id}_notes"]

        # skip deleted notes
        if "contentId" not in note:
            continue

        content_id = note["contentId"]
        content_data = data[f"{content_id}_content"]["data"]

        filename = "".join(x for x in note["title"] if x.isalnum())

        with open(filename + ".html", "wt") as f:
            f.write(content_data)

