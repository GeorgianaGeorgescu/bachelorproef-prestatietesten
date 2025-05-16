import subprocess
import time
import csv
from dotenv import load_dotenv
from pathlib import Path
from os import environ, getenv, chdir

load_dotenv(dotenv_path=Path(".env"))

projects = [
    {"name": "NestJS", "path": getenv("API_DIRECTORY_NEST")},
    {"name": "Koa", "path": getenv("API_DIRECTORY_KOA")},
    {"name": "Hono", "path": getenv("API_DIRECTORY_HONO")}
]

YARN_EXECUTABLE = getenv("YARN_EXECUTABLE", "yarn")

csv_file =Path(__file__).parent / "build_results.csv"

# Create/open the CSV and write the header
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Project", "Build Time (seconds)"])

    # Loop through each project and perform the build
    for project in projects:
        if not project["path"]:
            print(f"Skipping {project['name']}: no path defined in .env.")
            writer.writerow([project["name"], "No path defined"])
            continue

        print(f"\n🔧 Building {project['name']}...")

        try:
            chdir(project["path"])
        except FileNotFoundError:
            print(f"Directory not found: {project['path']}")
            writer.writerow([project["name"], "Directory not found"])
            continue

        start = time.time()
        try:
            result = subprocess.run([YARN_EXECUTABLE, "build"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            elapsed = round(time.time() - start, 2)
            print(f"{project['name']} build completed in {elapsed} seconds.")
            writer.writerow([project["name"], elapsed])
        except subprocess.CalledProcessError as e:
            print(f" Build failed for {project['name']}. Error: {e.stderr.decode()}")
            writer.writerow([project["name"], "Build failed"])
        finally:
            # Return to the original directory
            chdir("..")
