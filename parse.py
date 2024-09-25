import csv

with open("intents_data.csv", "r") as file:
    reader = csv.reader(file)
    rows = [row for row in reader]

with open("training_data.txt", "w+") as out:
    for row in rows:
        out.write(f"__label__{row[1].lower()} {row[0]}\n")