import csv
import git
import os
import shutil
import glob
import time

def clear_directory(target_dir):
    if not os.path.exists(target_dir):
        #print(f"ディレクトリ '{target_dir}' は存在しません。")
        return

    if not os.path.isdir(target_dir):
        #print(f"指定されたパス '{target_dir}' はディレクトリではありません。")
        return

    # ディレクトリ内のすべてのファイルとサブディレクトリを削除
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)  # ファイルやシンボリックリンクを削除
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # ディレクトリを再帰的に削除
            #print(f"削除完了: {item_path}")
        except Exception as e:
            print(f"削除に失敗しました: {item_path}, エラー: {e}")



#リポジトリのクローン
def clone_repo(reponame):
    dir_name = reponame.replace('/','_')
    try:
        repo = git.Repo.clone_from('https://github.com/' + reponame,'/work/wataru-m/docker_latest_research/repo/' + dir_name)
    except Exception as e:
        #print(e)
        #print("取得失敗: {0}".format(reponame))
        repo = ''
    return repo,dir_name

#リポジトリに含まれるDockerfileのリストを返す
def check_dockerfile(repo,dirname):
    dfile_list = []
    path = '/work/wataru-m/docker_latest_research/repo/' + dirname
    for pathname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename == "Dockerfile" or filename == "dockerfile":
                dfile_list.append(pathname+'/'+filename)
    #print("{}:{}".format(dirname, dfile_list))
    return dfile_list

#Dockerfile内の"FROM base:latest"を探す
def number_latest_in_dockerfile(dfile_list):
    count = 0
    error = 0
    
    dfile_count = len(dfile_list)
    for dfile_path in dfile_list:
        colon_flag = False
        latest_flag = False
        if not os.path.isdir(dfile_path):
            try:
                with open(dfile_path,'r') as dfile:
                    for line in dfile:
                        splited_line = line.split(' ')
                        if splited_line[0] == 'FROM':
                            for elements in splited_line:
                                #change to latest
                                if elements.find('latest') >= 0:
                                    count += 1
                                    latest_flag = True
                                    break
                                elif elements.find(":") > 0 or elements.find('@') > 0:
                                    colon_flag = True
                            if latest_flag:
                                break
                            elif not colon_flag:
                                count += 1
                                break                                  
            except Exception as e:
                #print("dfile error")
                error += 1
        else:
            dfile_count -= 1
    return dfile_count, count, error

def output_result(using, not_using, out, out_non):
    result = open(out, 'w')
    result_no = open(out_non, 'w')
    for file in using:
        result.write(file)
        result.write('\n')
    
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

    use_latest_project = []
    not_use_latest_project = []

    ####config####
    target_directory = "/work/wataru-m/docker_latest_research/repo"  # 削除したいディレクトリを指定

    input_file = "/work/wataru-m/docker_latest_research/repo_list_300k_380k.csv"
    output_file_use = '/work/wataru-m/docker_latest_research/result/use_latest_300k_380k.txt'
    output_file_nonuse = '/work/wataru-m/docker_latest_research/result/non_use_latest_300k_380k.txt'

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
            else: dfile_list = []
            
            if len(dfile_list) > 0:
                number_dfile, number_latest, error = number_latest_in_dockerfile(dfile_list)
                latest_dfile += number_latest
                if number_latest > 0:
                    latest_project_count += 1
                    use_latest_project.append(reponame)
                else:
                    not_use_latest_project.append(reponame)
                total_dfile += number_dfile
                error_count += error
            
            print('dfile:{0}'.format(total_dfile))
            print('latest:{0}'.format(latest_dfile))

            clear_directory("/work/wataru-m/docker_latest_research/repo/" + dirname)
            if os.path.exists("/work/wataru-m/docker_latest_research/repo/" + dirname):
                os.rmdir("/work/wataru-m/docker_latest_research/repo/" + dirname)

            print('total project:{0}'.format(project_count))
            print('latest project:{0}'.format(latest_project_count))
            print('file not found or error:{0}'.format(error_count))
            print("-----")

            #動作確認用，少ないリポジトリ数
            #test_count += 1
            #if test_count == 100:
            #    break
    output_result(use_latest_project, not_use_latest_project, output_file_use, output_file_nonuse)
            
            
if __name__ == "__main__":
    main()