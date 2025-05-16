import subprocess
import sys
import time
import signal
import atexit
from datetime import date
from os import environ, getenv, listdir, makedirs
from os.path import isfile, join, splitext
from pathlib import Path
import psutil
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Constants
ping_url = "http://localhost:3000/api/health/ping"
scenarios_path = str(Path(__file__).resolve().parent / "scenarios")
results_base_directory = str(Path(__file__).resolve().parent / "scenarios" / "results")
current_date = date.today()
results_directory = f"{results_base_directory}/{current_date}"
artillery_run = "artillery run -e development"
config_path = Path(__file__).parent / "config.yaml"
number_of_runs = 1  

# Environment Variables
YARN_EXECUTABLE = getenv("YARN_EXECUTABLE")

# API directory mapping
API_DIRECTORIES = {
    "hono": getenv("API_DIRECTORY_HONO"),
    "koa": getenv("API_DIRECTORY_KOA"),
    "nest": getenv("API_DIRECTORY_NEST"),
}

scenarios = sorted([
    file for file in listdir(scenarios_path)
    if isfile(join(scenarios_path, file)) and file.endswith(".yaml")
])

result_folder = None
shutdown_api = None 
API_DIRECTORY = None

def drop_test_database():
    try:
        print("Resetting Prisma database...")
        subprocess.run(
            [YARN_EXECUTABLE, "prisma", "migrate", "reset", "--force"],
            cwd=API_DIRECTORY,
            check=True,
        )
        print("Database reset successfully.")
    except subprocess.CalledProcessError as error:
        print(f"Error resetting database: {error}")

def terminate_process_and_children(parent_pid):
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):
        child.terminate()
    parent.terminate()

def start_api():
    env = environ.copy()
    env["LOG_DISABLED"] = "true" 
    env["PORT"] = "3000"

    api_process = subprocess.Popen(
        [YARN_EXECUTABLE, "start"], 
        cwd=API_DIRECTORY, 
        env=env, 
        stdout=subprocess.DEVNULL
    )
    
    def shutdown_api():
        if api_process.poll() is None:
            print("Shutting down API...")
            terminate_process_and_children(api_process.pid)
            print("API successfully shut down.")

    return shutdown_api

def wait_for_startup(interval=1, attempts=5):
    is_running = False
    count = 1

    while not is_running and count <= attempts:
        time.sleep(interval)
        try:
            response = requests.get(url=ping_url)
            data = response.json()
            is_running = data['pong']
        except:
            print(f"API still down: attempt {count} of {attempts}.")
            count += 1

    if not is_running:
        raise Exception(f"API is not running after {count} attempts.")
    else:
        print("API is running!")

def make_results_directory(app_version):
    global result_folder
    result_folder = f"{results_directory}/{app_version}"
    print(f"Creating results directory: {result_folder}")
    makedirs(result_folder, exist_ok=True)

def create_artillery_command(filename, run):
    command = artillery_run
    result_file_path = f"{result_folder}/{splitext(filename)[0]}.json"
    config_full_path = Path(__file__).parent / "config.yaml"

    if filename != "3_login.yaml":
       command = f"{command} --config {config_full_path}"

    command += f" --output {result_file_path} {scenarios_path}/{filename}"
    return command

def run_testscripts_and_save_results(run):
    try:
        for filename in scenarios:
            subprocess.run(
                create_artillery_command(filename=filename, run=run),
                shell=True,
                check=True
            )
    except subprocess.CalledProcessError as error:
        print(f"Error while running Artillery testscripts: {error}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python load_tests.py <project_name>")
        print(f"Available projects: {', '.join(API_DIRECTORIES.keys())}")
        sys.exit(1)

    project_name = sys.argv[1].lower()
    

    if project_name not in API_DIRECTORIES:
        print(f"Error: Unknown project '{project_name}'")
        print(f"Available projects: {', '.join(API_DIRECTORIES.keys())}")
        sys.exit(1)
    

    global API_DIRECTORY
    API_DIRECTORY = API_DIRECTORIES[project_name]
    
    if not API_DIRECTORY:
        print(f"Error: API directory for '{project_name}' is not set in .env file")
        sys.exit(1)

    app_version = project_name
    print(f"--- Starting tests for {app_version} ---")

    for run in range(1, number_of_runs + 1):
        try:
            print(f"Starting run {run}/{number_of_runs} for {app_version}")
            drop_test_database()

            shutdown_api = start_api()
            wait_for_startup()

            make_results_directory(app_version)
            run_testscripts_and_save_results(run=run)

        except Exception as exception:
            print(f"An exception occurred when running tests: {exception}")

        finally:
            if shutdown_api:
                shutdown_api()

if __name__ == "__main__":
    main()