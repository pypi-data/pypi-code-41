class PyCLIMain():
    def __init__(self):
        self.MESSAGE_PROMPT = "Enter command you want to execute: "
        self.MESSAGE_PROMPT_INVALID_COMMAND = "This is an invalid key"
        self.MESSAGE_EXIT = "Aborting the programme"
        self.cli_commmands = {
            # "help": help_command,
            # "exit": exit_command
        }
    
    def add_cli_command(self, cli_command):
        if isinstance(cli_command, PyCLICommand):
            self.cli_commmands[cli_command.command] = cli_command
        else:
            raise Exception

    def build(self):
        # Generate help message ... ?
        # Generate prompt-command-excution loop
        while True:
            print(self.MESSAGE_PROMPT)
            command = input()
            if command == "exit":
                print(self.MESSAGE_EXIT)
            elif command in self.cli_commmands.keys():
                self.cli_commmands[command].run()

            else:
                print(self.MESSAGE_PROMPT_INVALID_COMMAND)

            




class PyCLICommand():
    def __init__(self):
        # Define command name
        # Add help message
        self.command = ""
        self.help_message = ""
        self.function = None

    
    def run(self):
        # Print base message
        # if arguments are needed or not
        pass
