#le!/usr/bin/env python
import sys
import os
import re
import subprocess
from pathlib import Path

environments = ['develop', 'release', 'master']

def parse_args(args):
    prevArg = ''
    for arg in args:
        match arg:
            case '-h':
                print("Not implemented yet!")
            case _:
                print("Invalid. Type -h for help")

def is_git_repo(path):
    gitfolder = os.path.join(path, '.git')
    return os.path.exists(gitfolder), gitfolder

def run_subprocess(*args, **kwargs):
    return subprocess.run(*args, text=True, check=True, stdout=subprocess.PIPE, **kwargs)

def find_projects():

    result = []

    path = Path('.')
    cwd_is_repo, cwdpath = is_git_repo(os.getcwd())
    if cwd_is_repo:
        result.append({1, cwdpath})
        return result

    projectFolders = sorted(Path('.').glob('*/.git'))
    for folder in projectFolders.copy():
        result.append(folder.parents[0])

    return result

def display_list(items):
    
    for index, item in enumerate(items, 1):
        print('{0:3} {1}'.format(str(index)+'.', str(item)))
    print('\nq.  quit')

def input_choose_proj(projects):
    choice = input()
    project_count = len(projects)

    if choice == 'q':
        sys.exit()
    elif not choice.isnumeric():
        return -1
    elif int(choice) <= project_count:
        return abs(int(choice))-1
    else:
        return -1

def get_csproj(project):
    return sorted(project.glob("**/*.csproj"))

def get_project_dependencies(project_file):
    package_lines = []
    with open(project_file) as f:
        for line in f:
            if re.search('#Nuget_To_Bump', line):
               package_lines.append(line) 
    return package_lines

def get_top_20_nugets():
   response = subprocess.run(['dotnet', 'package', 'search', '#nuget name', '--source', '#any_source_url', '--exact-match', '--prerelease', '--verbosity', 'minimal'], text=True,
             stdout=subprocess.PIPE,
             check=True)
   top20 = response.stdout.splitlines()[4:24]
   return [ line.split('|')[2] for line in top20 ]

def prompt_input(choices):
    choice = 0
    while True:
        choice = input_choose_proj(choices)
        if choice >= 0:
            break
    return choice

def update_csproj(version, csproj):
    print('Updating project files...')
    document = []
    with open(csproj, 'r') as rf:
        for line in rf:
            if re.search('#Nuget_To_Bump', line):
                words = line.split('"')
                i = words.index(' Version=')
                words[i+1] = version.strip()
                document.append('"'.join(words))
            else:
               document.append(line)

    with open(csproj, 'w') as wf:
        wf.write(''.join(document))

def build_project(csproj):

    is_success = False
    try:
        res = subprocess.run(['dotnet', 'build', csproj],
                             text = True,
                             stdout = subprocess.PIPE,
                             check=True)
    except subprocess.CalledProcessError as err:
        print('Building the application failed!', file=sys.stderr)
    except FileNotFoundError:
        print('dotnet is not installed', file=sys.stderr)
    else:
        print('Succesfully built!')
        is_success = True
    finally:
        return is_success

def git_fetch(cwd):
    try:
        run_subprocess(['git', 'fetch'], shell=True, cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('Failed to fetch with git!', file=sys.stderr)
        Errorprint(err.stdout)
        sys.exit()
    except Exception as err:
        print('a general exception in git fetch')
        print(err.args)

def git_status(cwd):
    res = []
    try:
        res = run_subprocess(['git', 'status', '-s'], cwd=cwd).stdout
    except subprocess.CalledProcessError as err:
        print('Failed git status', file=sys.stderr)
        Errorprint(err.stdout)
        sys.exit()
    except Exception as err:
        print('a general exception in git status')
        print(err.args)
        sys.exit()
    else:
        return res

def git_checkout_new_branch(cwd, branch_name, remote_branch):
    try:
        subprocess.run(['git', 'checkout', '-b', branch_name, 'origin/' + remote_branch], cwd=cwd, text=True, stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as err:
        print('git could not check out new branch! See error:', file=sys.stderr)
        print(err.stdout)
        sys.exit()

def git_checkout_branch(cwd, branch_name):
    try:
        subprocess.run(['git', 'checkout', branch_name], cwd=cwd, text=True, stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as err:
        print('git could not check out branch! See error:', file=sys.stderr)
        print(err.stdout)
        sys.exit()

def reset_branch(cwd, branch_name, remote_name):
    try:
        run_subprocess(['git', 'reset', '--hard', 'origin/'+remote_name], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('failed to reset branch to origin. See error:')
        print(err.stdout)

def git_add(cwd):
    try:
        run_subprocess(['git', 'add', '-u'], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('git could not stage changes', file=sys.stderr)
        print(err.stdout, file=sys.stderr)
        sys.exit()

def git_commit_bump(cwd):
    try:
        subprocess.run(['git', 'commit', '-m', 'bumping nugets'], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('git could not commit on branch', file=sys.stderr)
        print(err.stdout, file=sys.stderr)
        sys.exit()

def git_push_remote(cwd, branch_name):
    try:
        run_subprocess(['git', 'push', '-u', 'origin', branch_name], cwd=cwd)
    except Exception:
        print('Unable push to remote. Is there an existing bump branch on the remote?', file=sys.stderr)
        sys.exit()

def grep_file(searchterm, fullfilename):
    matches = []

    try:
        with open(fullfilename) as f:
            for line in f:
                if re.search(searchterm, line):
                    matches.append(line)
    except Exception:
        print('Could not read from file', fullfilename)
    finally:
        return matches

def grep_input(searchterm, stringlist):
    matches = []
    for line in stringlist:
        exists = re.search(searchterm, line)
        if exists:
            matches.append(exists)
    return matches

def get_work_items(environment, project):
    res = run_subprocess(['git', 'log', 'origin/{0}..head'.format(environment)], cwd=project)
    tasks = grep_input(r'#\d+', res.stdout.split('\n'))
    cleantasks = [task[1:] for task in tasks]
    uniqtasks = set(cleantasks)
    return uniqtasks


def initialize_branch(env_id, project):
    environment = environments[env_id]
    resolve_branch = 'bump-nugets-' + environment

    unsaved_work = git_status(project)
    if len(unsaved_work) > 0:
        print('Please commit or undo changes in your repo:')
        print('\r\n'.join(unsaved_work))

    print('Fetching...')
    git_fetch(project)

    gitconf = project.joinpath('.git', 'config')
    bump_branches = grep_file(resolve_branch, gitconf)

    if len(bump_branches) > 0:
        print('found existing bump branch..')
        git_checkout_branch(project, resolve_branch)
        print('syncing branch to origin/'+environment)
        reset_branch(project, resolve_branch, environment)
    else:
        print('creating new local branch: ', resolve_branch)
        git_checkout_new_branch(project, resolve_branch, environment)
    
    if env_id > 0:
        print('merging {0} into bump branch'.format(environments[env_id-1]))
        run_subprocess(['git', 'merge', 'origin/'+environments[env_id-1],
                        '-Xtheirs']
                       , cwd=project)

    tasks = get_work_items(environments[env_id], project)



def finalize_git(environment, project):
    print('staging changes...')
    git_add(project)
    print('committing in git...')
    git_commit_bump(project)
    print('pushing to remote...')
    git_push_remote(project, 'bump-nugets-'+environment)

def create_pullrequest(environment, project):
    url_line = grep_file('url', project.joinpath('.git', 'config'))[0]
    remote_url = url_line.split(' ')[-1].strip()

    print(remote_url)

    try:
        az_repo_id = run_subprocess(['az', 'repos', 'list', '--query', "[?contains(remoteUrl, '{0}')].id".format(remote_url), '-o', 'json'], shell=True)
    except subprocess.CalledProcessError as err:
        print('Failed to get az repo id')
        print(err.stdout)
        sys.exit()
    else:
        az_repo_id = str(az_repo_id.stdout).strip().split('"')[1]

    try:
        run_subprocess(['az', 'repos', 'pr', 'create', 
                        '-r', az_repo_id,
                        '-s', 'refs/heads/bump-nugets-'+environment,
                        '-t', 'refs/heads/'+environment,
                        '--title', 'bumping nugets to '+environment,
                        '--open'],
                       shell=True)
    except subprocess.CalledProcessError as err:
        print('Branch is ready on the remote, but failed to create PR')


def main():
    parse_args(sys.argv[1:])

    while True:
        print('In what project would you like to bump nugets?')
        projects = find_projects()
    
        display_list(projects)
    
        project_id = prompt_input(projects)
    
        print('\nTo what environment would you like to push?')
        display_list(environments)
        env_id = prompt_input(environments)
    
        print('\npreparing git branch for bumping...')
        initialize_branch(env_id, projects[project_id])
    
        csprojs = get_csproj(projects[project_id])
    
        csproj_id = 0
        if len(csprojs) > 1:
            print('found multiple project files! Please pick one.')
            csproj_displayname = [x.name for x in csprojs]
            display_list(csproj_displayname)
            csproj_id = prompt_input(csprojs)
    
    
        packages = get_project_dependencies(csprojs[csproj_id])
    
        print('\nReferences to update:')
        for package in packages:
            print(package)
    
        package_versions = get_top_20_nugets()
    
        display_list(package_versions)
        version_id = prompt_input(package_versions)
    
        update_csproj(package_versions[version_id], csprojs[csproj_id])
    
        print('\ntrying to build project')
        build_succeeded = build_project(csprojs[csproj_id])
        if not build_succeeded:
            print('Aborting...', file=sys.stderr)
            continue
    
        finalize_git(environments[env_id], projects[project_id])
    
        create_pullrequest(environments[env_id], projects[project_id])
    

if __name__ == "__main__":
    main()
