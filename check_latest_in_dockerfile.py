import csv
import git
import os
import shutil
import glob
import time

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


def main():
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

    input_file = "input/repo_list.csv"
    output_file_use = 'output/use_latest_project'
    output_file_nonuse = 'output/non_use_latest_project'

    clear_directory(target_directory)
    time.sleep(1)

    with open(input_file, 'r') as input_file:

        for reponame in input_file:
            #clear_directory(target_directory)
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
            
            print('dfile:{0}'.format(total_dfile))
            print('latest:{0}'.format(latest_dfile))

            #clear the cloned repository
            clear_directory("repo/" + dirname)
            if os.path.exists("repo/" + dirname):
                os.rmdir("repo/" + dirname)

            print('total project:{0}'.format(project_count))
            print('latest project:{0}'.format(latest_project_count))
            print('file not found or error:{0}'.format(error_count))
            print('repo not found:{0}'.format(repo_not_found))
            print("-----")

            # For operation confirmation, small number of repositories
            #test_count += 1
            #if test_count == 100:
            #    break
    output_result(use_latest_project, not_use_latest_project, output_file_use, output_file_nonuse)
            
            
if __name__ == "__main__":
    main()