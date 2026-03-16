# --- CONFIGURATION ---
REPORT_FILE = '/work/pakorn-l/clone-repo/research_dockerfile_using_latest/output/change_tag_report.txt'       # The file containing the "Process X change tag report"
REPO_LIST_FILE = '/work/pakorn-l/clone-repo/research_dockerfile_using_latest/output/use_latest_project_2026.txt'     # The file containing the list of repo names
OUTPUT_FILE = '/work/pakorn-l/clone-repo/research_dockerfile_using_latest/output/extracted_change_tag_report_2026.txt'

def group_repo_data():

    target_repos = set()
    try:
        with open(REPO_LIST_FILE, 'r') as f:
            target_repos = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Error: Could not find {REPO_LIST_FILE}")
        return

    groups = {
        "Changes pinned to latest": [],
        "Changes latest to pinned": []
    }

    current_category = None
    current_block = []   # Temporary buffer to hold lines for one repo
    save_current_block = False # Flag: should we save the current buffer?

    print("Reading and grouping data...")

    try:
        with open(REPORT_FILE, 'r') as f_in:
            for line in f_in:
                stripped = line.strip()

                if "Changes pinned to latest:" in line:
                    current_category = "Changes pinned to latest"
                    continue # Move to next line
                elif "Changes latest to pinned:" in line:
                    current_category = "Changes latest to pinned"
                    continue # Move to next line

                if line.startswith("Repository:"):
                    # 1. If we were processing a previous block, save it now
                    if save_current_block and current_block and current_category:
                        groups[current_category].append("".join(current_block))
                    
                    # 2. Reset for the new block
                    current_block = []
                    save_current_block = False
                    
                    # 3. Check if this new repo is in our list
                    parts = stripped.split(":", 1)
                    if len(parts) > 1:
                        repo_name = parts[1].strip()
                        if repo_name in target_repos:
                            save_current_block = True
                            current_block.append(line) # Add the Repository: line
                    continue

                if save_current_block:
                    # If line is empty, it marks the end of the block
                    if not stripped:
                        # End of block logic
                        if current_block and current_category:
                            groups[current_category].append("".join(current_block))
                            current_block = []
                            save_current_block = False
                    # If line is indented, add to buffer
                    elif line.startswith(" ") or line.startswith("\t"):
                        current_block.append(line)
                    # If line is not indented and not empty (e.g. "Process 76..."), stop capturing
                    else:
                        if current_block and current_category:
                            groups[current_category].append("".join(current_block))
                        current_block = []
                        save_current_block = False

            if save_current_block and current_block and current_category:
                 groups[current_category].append("".join(current_block))

    except FileNotFoundError:
        print(f"Error: Could not find {REPORT_FILE}")
        return

    with open(OUTPUT_FILE, 'w') as f_out:
        
        header1 = "Changes pinned to latest"
        data1 = groups[header1]
        
        f_out.write("=" * 50 + "\n")
        f_out.write(f"{header1} (Found: {len(data1)})\n")
        f_out.write("=" * 50 + "\n\n")
        
        if data1:
            for block in data1:
                f_out.write(block)
                f_out.write("-" * 20 + "\n") # Separator between items
        else:
            f_out.write("No matching repositories found for this category.\n")
        
        f_out.write("\n\n")

        header2 = "Changes latest to pinned"
        data2 = groups[header2]
        
        f_out.write("=" * 50 + "\n")
        f_out.write(f"{header2} (Found: {len(data2)})\n")
        f_out.write("=" * 50 + "\n\n")

        if data2:
            for block in data2:
                f_out.write(block)
                f_out.write("-" * 20 + "\n")
        else:
            f_out.write("No matching repositories found for this category.\n")

    print(f"Done! Data grouped and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    group_repo_data()