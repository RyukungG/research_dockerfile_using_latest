import os
import os
import subprocess
import datetime
import argparse
import tempfile
import shutil

# Configuration
YEAR = range(2013, 2026)  # Change this or read dynamically
repo_dir = "repo"

### Working on ###
def singularity_build(repo_path, repo_name, runtime="podman"):
    """
    Build and test Dockerfiles from a repository using Podman or Docker.

    Args:
        repo_path (str): Path to repository root
        repo_name (str): Repo name (used for tagging)
        temp_dir (str): Temporary directory for builds
        runtime (str): 'podman' or 'docker'
    Returns:
        (bool, str): (success flag, message)
    """

    print(f"Checking Dockerfile in {repo_path}/{repo_name}")
    dfile_list = []
    for pathname, _, filenames in os.walk(repo_path):
        for filename in filenames:
            if filename.lower() == "dockerfile":
                dfile_list.append(os.path.join(pathname, filename))

    if not dfile_list:
        return False, "No Dockerfile found"

    build_errors = []

    for dfile_path in dfile_list:
        df_dir = os.path.dirname(dfile_path)
        tag = f"{repo_name.replace('/', '_')}_latest"
        print(f"Building image: {tag} from {dfile_path}")

        build_cmd = [
            runtime, "build", "--storage-driver=vfs", "-t", tag, "-f", dfile_path, df_dir
        ]

        try:
            subprocess.run(build_cmd, check=True, capture_output=True, text=True)
            print(f"Build succeeded for {tag}")

            # --- Run test container ---
            print(f"Running container {tag} ...")
            run_cmd = [runtime, "run", "--rm", tag]
            run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=120)

            print(run_result.stdout)
            if run_result.returncode != 0:
                raise subprocess.CalledProcessError(run_result.returncode, run_cmd, run_result.stdout, run_result.stderr)

        except subprocess.CalledProcessError as e:
            build_errors.append(f"Failed for {dfile_path}\n{e.stderr or e.stdout}")
        except subprocess.TimeoutExpired:
            build_errors.append(f"Timeout running {tag}")
        except FileNotFoundError:
            return False, f"{runtime} not found on system"
        finally:
            # --- Cleanup to prevent trash images ---
            cleanup(tag, runtime)

    if build_errors:
        return False, "\n".join(build_errors)

    return True, "All builds succeeded"


def cleanup(tag, runtime):
    """Remove containers and images to avoid clutter."""
    try:
        subprocess.run([runtime, "rm", "-f", tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        subprocess.run([runtime, "rmi", "-f", tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
### Woring on ###

def output_result(able, unable, out_able, out_unable):
    with open(out_able, 'w') as f_able:
        for able_repo in able:
            f_able.write(f"{able_repo}\n")

    with open(out_unable, 'w') as f_unable:
        for unable_repo in unable:
            f_unable.write(f"{unable_repo}\n")

def output_summary(total_project, able_to_build, unable_to_build, repo_not_found, process_id, year):
    summary = open('output/build_check/summary_check_build_latest.txt', 'a')
    summary.write(f"Process {process_id} results for year {year}:\n")
    summary.write('Total project: {0}\n'.format(total_project))
    summary.write('Project able to build Dockerfile: {0}\n'.format(able_to_build))
    summary.write('Project unable to build Dockerfile: {0}\n'.format(unable_to_build))
    summary.write('Repo not found: {0}\n'.format(repo_not_found))
    summary.write('--------------------------------------------------\n')
    summary.close()
    print(f"Build summary saved to 'output/build_check/summary_check_build_latest.txt'")

def main(index):
    year_to_process = 0
    if index == -1:
        year_to_process = 1970  # Dummy value to indicate all years
    else:
        year_to_process = YEAR[index]

    repo_count = 0
    able_to_build_repo_count = 0
    unable_to_build_repo_count = 0
    repo_not_found = 0

    able_to_build_repo = []
    unable_to_build_repo = []

    input_file = f"output/use_latest_project_{year_to_process}.txt"

    output_able = f"output/build_check/buildable_project_{year_to_process}.txt"
    output_unable = f"output/build_check/unbuildable_project_{year_to_process}.txt"

    if not os.path.exists(input_file):
        print(f"Cannot find {input_file}")
        return

    with open(input_file) as f:
        repo_names = [line.strip() for line in f if line.strip()]

    results = []
    for repo_name in repo_names:
        dir_name = repo_name.replace('/','_')
        repo_path = os.path.join(repo_dir, dir_name)
        if not os.path.isdir(repo_path):
            print(repo_name, "Not found")
            repo_not_found += 1
            continue

        print(f"Building {repo_name}...")
        success, info = singularity_build(repo_path, repo_name)
        if success:
            results.append((repo_name, "Build success"))
            able_to_build_repo.append(repo_name)
            able_to_build_repo_count += 1
        else:
            results.append((repo_name, f"Build failed\n{info}"))
            unable_to_build_repo.append(repo_name)
            unable_to_build_repo_count += 1

    # Write summary log
    log_file = f"output/log/build_check/build_check_log_{year_to_process}.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "w") as f:
        f.write(f"Singularity Build Check — {timestamp}\n\n")
        for name, result in results:
            f.write(f"{name}: {result}\n\n")

    output_result(able_to_build_repo, unable_to_build_repo, output_able, output_unable)
    output_summary(repo_count, able_to_build_repo_count, unable_to_build_repo_count, repo_not_found, index, YEAR[index])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=-1)
    parser.add_argument("--total_array_size", type=int, default=1)
    args = parser.parse_args()
    args = vars(args)
    main(int(args["index"]))
