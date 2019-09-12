import argparse
import getpass
import os
import shutil
import stashy
import sys
import tempfile
from termcolor import colored
import urllib

# fix the ascii error, from:
# http://mypy.pythonblogs.com/12_mypy/archive/1253_workaround_for_python_bug_ascii_codec_cant_encode_character_uxa0_in_position_111_ordinal_not_in_range128.html
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf8")

# read input parameters
parser = argparse.ArgumentParser(
  formatter_class=argparse.RawTextHelpFormatter,
  description="""
ROBOSTASH!

This tool was developed to provide and easy way to clone all of the repositories contained
within an Atlassian Bitbucket Project. In the future the ability to push multiple repositories
to an Atlassian Bitbucket Project will also be included. Other platforms (ex. GitHub, GitLab, etc)
may eventually be supported as well.

Currently robostash only supports "archive" mode which will create a tarball containing mirror
(bare) copies of all of the Git repositories contained within a single Bitbucket project. The tarball
will be created within your current working directory.

examples:
  Run the program to archive all of the repos in a Bitbucket project
    robostash archive -u thomas.magnum -p H1ggyBabby -k rmasters -u https://bitbucket.com
    
  Run the program to display the version
    robostash -v
    
  Run the program with no arguments or the -h/--help option to display help 
    robostash -h

""")

# going to create our own groups so they show up in correct order in help
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

# required arguments
required.add_argument('mode', type=str, help='Specify stashbot action. Valid actions: archive')
required.add_argument('-u', '--user', help='Bitbucket username\n  example: thomas.magnum', required=True)
required.add_argument('-k', '--key', help='Bitbucket project key\n  example: rmasters', required=True)
required.add_argument('-b', '--url', help='Bitbucket url\n  example: https://bitbucket.com', required=True)

# optional arguments
# TODO: always update VERSION number, it is right ---------------------------->HERE!<
optional.add_argument('-v', '--version', action='version', version='robostash - v0.1.0 Higgins')
optional.add_argument('-p', '--password', help='Bitbucket password\n  example: H1ggyBabby')
optional.add_argument('-f', '--credfile', help='path to a Bitbucket password file\n')

args = parser.parse_args()

# Set parameters
stash_slug = args.key
stash_url = args.url
stash_username = args.user

# If a password or credfile path was not provided, prompt for password.
if args.password is not None:
  stash_password = args.password
elif args.credfile is not None:
  password_file = open(args.credfile, "r")
  password_line = (password_file.readline())
  stash_password = (password_line.split()[0])
  password_file.close()
else:
    stash_password = getpass.getpass("Password: ")

# get the current working directory
os_path = os.getcwd()

def main():
  # create temporary directories and change working directory
  tmp_dir = tempfile.mkdtemp(prefix="rstash_", dir=os_path)
  arch_dir = os.path.join(tmp_dir, stash_slug)
  os.mkdir(arch_dir)
  os.chdir(arch_dir)

  # create a stash object
  print (colored("connecting to Bitbucket\n", 'white', attrs=['bold']))
  stash = stashy.connect(stash_url, stash_username, stash_password)
  try:
    stash.projects.list()
  except:
    print (colored("connecting to Bitbucket : ", 'white', attrs=['bold']) + colored("Failed\n", 'red', attrs=['bold']))
    shutil.rmtree(tmp_dir, ignore_errors=True)
    exit(1)
  else:
    print (colored("connecting to Bitbucket : ", 'white', attrs=['bold']) + colored("Success\n", 'green', attrs=['bold']))

  # query bitbucket api for a list of repos, iterate, and clone
  for repo in stash.projects[stash_slug].repos.list():
    for url in repo["links"]["clone"]:
      if url["name"] == "http":
        print (colored("cloning : ", 'white', attrs=['bold']) + colored(repo["name"], 'blue', attrs=['bold']))
        url = url["href"][:8] + stash_username + ':' + urllib.quote(stash_password, safe='') + '@' + url["href"][8:]
        try:
          os.system("git clone --mirror {0}".format(url))
        except:
          print (colored("cloning : ", 'white', attrs=['bold']) + colored("Failed\n", 'red', attrs=['bold']))
          break
        else:
          print (colored("cloning : ", 'white', attrs=['bold']) + colored("Success\n", 'green', attrs=['bold']))
        break

  # compress project
  print (colored("creating archive\n", 'white', attrs=['bold']))
  arch_name = stash_slug + '.tar.gz'
  os.chdir(tmp_dir)
  os.system("tar -czf {0} {1}".format(arch_name, stash_slug))
  os.rename(os.path.join(tmp_dir, arch_name), os.path.join(os_path, arch_name))
  print (colored("creating archive : ", 'white', attrs=['bold']) + colored("Success\n", 'green', attrs=['bold']))

  # remove temporary directory
  print (colored("cleaning up\n", 'white', attrs=['bold']))
  try:
    shutil.rmtree(tmp_dir, ignore_errors=True)
  except:
    print (colored("cleaning up : ", 'white', attrs=['bold']) + colored("Failed\n", 'red', attrs=['bold']))
  else:
    print (colored("cleaning up : ", 'white', attrs=['bold']) + colored("Success\n", 'green', attrs=['bold']))

if __name__ == "__main__":
    main()