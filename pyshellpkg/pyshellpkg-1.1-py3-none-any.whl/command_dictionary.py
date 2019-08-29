cmd_dict = {'cat':""" Usage: cat [FILE]...
                    
                    Concatenate FILE(s) to standard output.

                    GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
                    Full documentation at: <http://www.gnu.org/software/coreutils/cat>
                    
                    """,                    
            'cd': """ cd [dir]
                    Change the shell working directory.

                    The variable CDPATH defines the search path for the directory containing
                    DIR.  Alternative directory names in CDPATH are separated by a colon (:).
                    A null directory name is the same as the current directory.  If DIR begins
                    with a slash (/), then CDPATH is not used.

                    If the directory is not found, and the shell option `cdable_vars' is set,
                    the word is assumed to be  a variable name.  If that variable has a value,
                    its value is used for DIR.

                    Exit Status:
                    Returns 0 if the directory is changed, non-zero otherwise.""",
            'cp' : """  cp  SOURCE... DIRECTORY
  
                        Copy SOURCE to DEST, or multiple SOURCE(s) to DIRECTORY, or source directory
                        to destination directory.
     
                        GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
                        Full documentation at: <http://www.gnu.org/software/coreutils/cp>""",

            'date':""" Usage: date
 
                    Display the current time in the given FORMAT, or set the system date.

                    GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
                    Full documentation at: <http://www.gnu.org/software/coreutils/cp>""",

            'exit' : "exit the prompt",
            'find': """Usage: find  [path...]

                    finds default path is the current directory. """,

            'grep': """ Usage: grep [OPTION]... [FILE]...
                        
                        Search for PATTERN in each FILE or standard input.
                        
                        OPTIONS:
                        -n, --line-number : print line number with output lines""",
            'head':""" Usage: head [OPTION]... [FILE]...
                    Print the first given lines of each FILE to standard output.

                    [OPTIONS]
                    -n :     print the first n lines of a file.

                    GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
                    Full documentation at: <http://www.gnu.org/software/coreutils/head>
                    or available locally via: info '(coreutils) head invocation'""",

            'help':"for help",
            'hostname':"current hostname",
            'history':"list of all commands entered",
            'ls' : "will list all directories and file ",
            'mv': "move a file",
            'mkdir': "add a new directory",
            'pwd' : "will give present working directory",
            'rm':"remove a file or directory, arguments allowed: '-r'",
            'rmdir': "remove given directory",
            'sizeof':"will give size of file",
            'tail':""" Usage: head [OPTION]... [FILE]...
                    Print the last given lines of each FILE to standard output.

                    [OPTIONS]
                    -n :      print the last n linesof a file.

                    GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
                    Full documentation at: <http://www.gnu.org/software/coreutils/head>
                    """  ,
            'timeit' : "time taken by a command",
            'whoami' : "current user"}