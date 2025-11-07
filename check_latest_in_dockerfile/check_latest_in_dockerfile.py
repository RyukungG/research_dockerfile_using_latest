import csv
import git
import os
import shutil
import glob
import time
import argparse

def clear_directory(target_dir):
    if not os.path.exists(target_dir):
        #print(f"directory '{target_dir}' does not exist.")
        return

    if not os.path.isdir(target_dir):
        #print(f"specified path  '{target_dir}' have no directory.")
        return

    # Delete all files and subdirectories in a directory
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)  # Delete files and symbolic links
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete directories recursively
            #print(f"Delete completed: {item_path}")
        except Exception as e:
            print(f"Failed to delete: {item_path}, Error: {e}")



# Clone the repository
def clone_repo(reponame):
    dir_name = reponame.replace('/','_')
    try:
        repo = git.Repo.clone_from('git@github.com:' + reponame + '.git','repo/' + dir_name)
        print("Clone completed: {0}".format(reponame))
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        repo = ''
    except Exception as e:
        print(e)
        print("Delete completed: {0}".format(reponame))
        repo = ''
    return repo,dir_name

# Return a list of Dockerfiles included in the repository
def check_dockerfile(repo,dirname):
    print("Checking Dockerfile in repo/{0}".format(dirname))
    dfile_list = []
    path = 'repo/' + dirname
    for pathname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename == "Dockerfile" or filename == "dockerfile":
                print("found Dockerfile: {}/{}".format(pathname, filename))
                dfile_list.append(pathname+'/'+filename)
    #print("{}:{}".format(dirname, dfile_list))
    return dfile_list

#Find "FROM base:latest" in the Dockerfile
def number_latest_in_dockerfile(repo, dfile_list): # I think this function have bugs
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
                with open(dfile_path,'r') as dfile:
                    for line in dfile:
                        splited_line = line.split(' ')
                        if splited_line[0] == 'FROM':
                            for elements in splited_line:
                                #change to latest
                                if elements.find('latest') >= 0:
                                    latest_flag = True
                                    break
                                elif elements.find(":") > 0 or elements.find('@') > 0:
                                    colon_flag = True
                            if latest_flag or not colon_flag:
                                count += 1
                                print("Try to check the latest commit year of {}".format("/".join(dfile_path.split('/')[2::])))
                                commit_year = int(list(repo.iter_commits(paths="/".join(dfile_path.split('/')[2::]), max_count=1))[0].committed_datetime.year)
                                break
            except Exception as e:
                #print("dfile error")
                error += 1
        else:
            dfile_count -= 1
        if commit_year > latest_commit_year:
            latest_commit_year = commit_year
    print("latest commit year: {0}".format(latest_commit_year))
    return dfile_count, count, latest_commit_year, error

def output_result(using, not_using, out, out_non):
    result_no = open(out_non + '.txt', 'w')
    for file in using:
        if not os.path.exists(out + '_{}.txt'.format(file[1])):
            result = open(out + '_{}.txt'.format(file[1]), 'w')
        else:
            result = open(out + '_{}.txt'.format(file[1]), 'a')
        result.write(file[0])
        result.write('\n')
        result.close()
    
    for file in not_using:
        result_no.write(file)
        result_no.write('\n')
    
    result.close()
    result_no.close()

def output_summary(total_project, latest_project, total_dfile, latest_dfile, error_count, repo_not_found, process_id):
    summary = open('output/summary_check_latest_in_dockerfile.txt', 'a')
    summary.write(f"Process {process_id} results:\n")
    summary.write('Total project: {0}\n'.format(total_project))
    summary.write('Project using latest: {0}\n'.format(latest_project))
    summary.write('Total Dockerfile: {0}\n'.format(total_dfile))
    summary.write('Dockerfile using latest: {0}\n'.format(latest_dfile))
    summary.write('File not found or error: {0}\n'.format(error_count))
    summary.write('Repo not found: {0}\n'.format(repo_not_found))
    summary.write("--------------------------------------------------\n")
    summary.close()

def setup_index(input_file, index, total_array_size):
    start = 0
    stop = -1
    if index == -1:
        return start, stop
    else:
        total_repo = sum(1 for line in open(input_file))
        base = total_repo // total_array_size
        start = index * base + min(index, total_repo % total_array_size)
        stop = (index + 1) * base + min(index + 1, total_repo % total_array_size)
        if stop > total_repo:
            stop = total_repo
        print("process repo from {} to {}".format(start, stop))
        return start, stop

def main(input_file, start=0, stop=-1, process_id=0):
    test_count = 0
    project_count = 0
    error_count = 0
    latest_project_count = 0
    total_dfile = 0
    latest_dfile = 0
    repo_not_found = 0

    use_latest_project = []
    not_use_latest_project = []

    ####config####
    target_directory = "repo"  # Specify the directory to delete

    output_file_use = 'output/use_latest_project'
    output_file_nonuse = 'output/non_use_latest_project'

    # clear_directory(target_directory)
    time.sleep(1)

    with open(input_file, 'r') as input_file:
        for i, reponame in enumerate(input_file):
            #clear_directory(target_directory)
            if i < start:
                continue
            if stop != -1 and i >= stop:
                break
            reponame = reponame.rstrip("\n")
            print(reponame)

            repo, dirname = clone_repo(reponame)
            if repo != '': 
                project_count += 1
                dfile_list = check_dockerfile(repo,dirname)
            else: 
                dfile_list = []
                repo_not_found += 1
            
            if len(dfile_list) > 0:
                number_dfile, number_latest, commit_year, error = number_latest_in_dockerfile(repo, dfile_list)
                latest_dfile += number_latest
                if number_latest > 0:
                    latest_project_count += 1
                    use_latest_project.append([reponame, commit_year])
                else:
                    not_use_latest_project.append(reponame)
                total_dfile += number_dfile
                error_count += error
            
            if len(dfile_list) == 0 or number_latest == 0:
                #clear the cloned repository that do not have Dockerfile or do not use latest
                clear_directory("repo/" + dirname)
                if os.path.exists("repo/" + dirname):
                    os.rmdir("repo/" + dirname)
        
            print("--------------------------------------------------")

            # For operation confirmation, small number of repositories
            #test_count += 1
            #if test_count == 100:
            #    break
    output_result(use_latest_project, not_use_latest_project, output_file_use, output_file_nonuse)
    output_summary(project_count, latest_project_count, total_dfile, latest_dfile, error_count, repo_not_found, process_id)
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="input/repo_list_test.csv")
    parser.add_argument("--index", type=int, default=-1)
    parser.add_argument("--total_array_size", type=int, default=1)
    args = parser.parse_args()
    args = vars(args)
    start, stop = setup_index(args['input_file'], args['index'], args['total_array_size'])
    main(args['input_file'], start, stop, args['index'])