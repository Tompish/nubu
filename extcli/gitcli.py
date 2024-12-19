import subprocess
import sys


def run_subprocess(*args, **kwargs):
    """Some predefined args to subprocess.run.
    args: text=True, stdout=subprocess.PIPE, check=True"""
    return subprocess.run(*args, text=True, check=True, stdout=subprocess.PIPE,
                          **kwargs)


def git_fetch(cwd):
    """Git fetch command in current working directory. Sys exit on fail"""
    try:
        run_subprocess(['git', 'fetch'], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('Failed to fetch with git!', file=sys.stderr)
        print(err.stdout)
        sys.exit()
    except Exception as err:
        print('a general exception in git fetch')
        print(err.args)
        sys.exit()


def git_status(cwd):
    """Git status command in current working directory. Sys exit on fail"""
    res = []
    try:
        res = run_subprocess(['git', 'status', '-s'], cwd=cwd).stdout
    except subprocess.CalledProcessError as err:
        print('Failed git status', file=sys.stderr)
        print(err.stdout)
        sys.exit()
    except Exception as err:
        print('a general exception in git status')
        print(err.args)
        sys.exit()
    else:
        return res


def git_checkout_new_branch(cwd, branch_name, remote_branch):
    """Git checkout new branch in current working directory.
        Sys exit on fail"""
    try:
        subprocess.run(['git', 'checkout',
                        '-b', branch_name,
                        'origin/' + remote_branch],
                       cwd=cwd, text=True, stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as err:
        print('git could not check out new branch! See error:',
              file=sys.stderr)
        print(err.stdout)
        sys.exit()


def git_checkout_branch(cwd, branch_name):
    """Git checkout existing branch in current working directory.
        Sys exit on fail"""
    try:
        subprocess.run(['git', 'checkout', branch_name],
                       cwd=cwd, text=True, stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as err:
        print('git could not check out branch! See error:', file=sys.stderr)
        print(err.stdout)
        sys.exit()


def reset_branch(cwd, branch_name, remote_name):
    """Git reset branch hard. CARE! May lose work.
        Sys exit on fail"""
    try:
        run_subprocess(['git', 'reset', '--hard', 'origin/'+remote_name],
                       cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('failed to reset branch to origin. See error:')
        print(err.stdout)


def git_add(cwd):
    """Git adds all files currently being tracked.
    sys.exit on fail"""
    try:
        run_subprocess(['git', 'add', '-u'], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('git could not stage changes', file=sys.stderr)
        print(err.stdout, file=sys.stderr)
        sys.exit()


def git_commit_bump(cwd):
    """Git commits with the message "bumping nugets".
    sys.exit on fail"""
    try:
        subprocess.run(['git', 'commit', '-m', 'bumping nugets'], cwd=cwd)
    except subprocess.CalledProcessError as err:
        print('git could not commit on branch', file=sys.stderr)
        print(err.stdout, file=sys.stderr)
        sys.exit()


def git_push_remote(cwd, branch_name):
    """Pushes and creates a remote branch named as "branch_name"
    sys.exit on fail"""
    try:
        run_subprocess(['git', 'push', '-u', 'origin', branch_name], cwd=cwd)
    except Exception:
        print('Unable push to remote. Is there an existing bump branch on the remote?', file=sys.stderr)
        sys.exit()
