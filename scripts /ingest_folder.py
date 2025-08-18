import os, json, asyncio, argparse
from src.pipeline.harmonize import harmonize

async def process_folder(inp: str, out: str):
    os.makedirs(out, exist_ok=True)
    for fn in os.listdir(inp):
        if not fn.endswith(".txt"): continue
        note = open(os.path.join(inp, fn)).read()
        bundle = await harmonize(note)
        with open(os.path.join(out, fn.replace(".txt", ".bundle.json")), "w") as f:
            json.dump(bundle, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest folder of notes and output FHIR bundles.")
    parser.add_argument("--input", type=str, required=True, help="Input folder containing text files.")
    parser.add_argument("--output", type=str, required=True, help="Output folder for FHIR bundles.")
    args = parser.parse_args()

    asyncio.run(process_folder(args.input, args.output))