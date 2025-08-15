import json, random, argparse

CONDITIONS = ["hypertension", "type 2 diabetes", "asthma", "depression", "hyperlipidemia"]
DRUGS = [
    ("metformin", 500, "mg", "BID"),
    ("lisinopril", 10, "mg", "QD"),
    ("albuterol", 90, "mcg", "PRN"),
    ("sertraline", 50, "mg", "QD"),
    ("atorvastatin", 20, "mg", "QD")
]

def make_note(i:int):
    age = random.randint(18, 90)
    sex = random.choice(["M", "F"])
    num_conditions = random.randint(1, 3)
    conditions = random.sample(CONDITIONS, num_conditions)
    num_drugs = random.randint(1, 3)
    drugs = random.sample(DRUGS, num_drugs) 
    text = f"{age} yo {sex} with {', '.join(conditions)}. Rx: " + \
           ", ".join([f"{d[0]} {d[1]} {d[2]} {d[3]}" for d in drugs]) + "."
    label = {
        "patient": {"age": age, "sex": sex[0].upper()},
        "conditions": [{"name": c} for c in conditions],
        "medications": [
            {"name": d[0], "dose": d[1], "unit": d[2], "frequency": d[3]} for d in drugs
        ],
    }
    
    return text, label


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=200, help="Number of synthetic notes to generate")
    args = parser.parse_args()

    with open("data/synthetic/notes.json", "w") as fnotes, open("data/synthetic/labels.json", "w") as flabels:
        for i in range(args.num):
            note, lab = make_note(i)
            fnotes.write(json.dumps({"id":i, "note":note}) + "\n")
            flabels.write(json.dumps({"id":i, "label":lab}) + "\n")
    print(f"Wrote {args.num} synthetic notes and labels")