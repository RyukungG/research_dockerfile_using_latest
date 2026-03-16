import os
import re

YEAR = 2026
REPO_LIST_FILE = f'/work/pakorn-l/clone-repo/research_dockerfile_using_latest/output/use_latest_repos_multiple_releases_{YEAR}.txt'     # The file containing the list of repo names
OUTPUT_FILE = f'/work/pakorn-l/clone-repo/research_dockerfile_using_latest/output/active_repo_multiple_version_dockerfile_report.txt'

def check_dockerfile(path):
    print("Checking Dockerfile in repo/{0}".format(path))
    dfile_list = []
    for pathname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename == "Dockerfile" or filename == "dockerfile":
                print("found Dockerfile: {}/{}".format(pathname, filename))
                dfile_list.append(pathname+'/'+filename)
    #print("{}:{}".format(dirname, dfile_list))
    return dfile_list

def extract_from_lines(path):
    """Return a list of FROM lines with base + tag"""
    result = []
    if not os.path.exists(path):
        return result

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("FROM "):
                result.append(line)
    return result

def parse_base_tag(from_line):
    """
    Extract image:tag from FROM lines.
    Return: (image, tag) example: ("python", "3.9")
    """
    m = re.search(r"FROM\s+([^\s:]+)(?::([^\s@]+))?", from_line)
    if not m:
        return None, None
    image = m.group(1)
    tag = m.group(2) if m.group(2) else None
    return image, tag

def number_latest_in_dockerfile(dfile_list): # I think this function have bugs
    count = 0
    error = 0
    latest_commit_year = 0
    
    dfile_count = len(dfile_list)
    for dfile_path in dfile_list:
        colon_flag = False
        latest_flag = False
        commit_year = 0
        if not os.path.isdir(dfile_path):
            try:
                extracted_lines = extract_from_lines(dfile_path)
                for line in extracted_lines:
                    image, tag = parse_base_tag(line)
                    if tag is None or tag == 'latest':
                        count += 1
                        break
            except Exception as e:
                print(f"Error processing {dfile_path}: {e}")
                error += 1
        else:
            dfile_count -= 1
    return dfile_count, count, error

def main():
    total_dfile_count = 0
    total_latest_count = 0
    total_error_count = 0
    target_repos = set()
    try:
        with open(REPO_LIST_FILE, 'r') as f:
            target_repos = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Error: Could not find {REPO_LIST_FILE}")
        return
    for repo_name in target_repos:
        repo = repo_name.replace('/','_')
        repo_path = os.path.join('/work/pakorn-l/clone-repo/research_dockerfile_using_latest/repo', repo)
        dfile_list = check_dockerfile(repo_path)
        dfile_count, latest_count, error_count = number_latest_in_dockerfile(dfile_list)
        total_dfile_count += dfile_count
        total_latest_count += latest_count
        total_error_count += error_count
        print(f"Repository: {repo_name}, Dockerfiles: {dfile_count}, Using 'latest': {latest_count}, Errors: {error_count}")
    print(f"Total Dockerfiles: {total_dfile_count}, Total Using 'latest': {total_latest_count}, Total Errors: {total_error_count}")

    with open(OUTPUT_FILE, 'a') as f_out:
        f_out.write(f"--- Report for Year {YEAR} ---\n")
        f_out.write(f"Total Dockerfiles: {total_dfile_count}, Total Using 'latest': {total_latest_count}, Total Errors: {total_error_count}\n")
        f_out.write("----------------------------------\n")
    print("Report written to", OUTPUT_FILE)

if __name__ == "__main__":
    main()