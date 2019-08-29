# -*- coding: utf-8 -*-

def display_help():

    help = """
Jarvis SDK Help
===============

usage : jarvis [--gcp-project-id GOOGLE_PROJECT_ID] COMMAND ARGUMENTS


Configure Jarvis SDK
--------------------

usage : jarvis config


Authenticate with Firebase
--------------------------

usage : jarvis auth login


Configuration deployment
------------------------

Please type : jarvis deploy configuration help


Generate and deploy DAG
-----------------------

Please type : jarvis [--gcp-project-id GOOGLE_PROJECT_ID] [--gcp-composer-bucket COMPOSER_BUCKET] dag-generator [dag-description.json]


Encrypt Message of file content
-------------------------------
Will encrypt data using Jarvis Public Key.

To encrypt a simple message : jarvis encrypt "My message to encrypt."
To encrypt file content     : jarvis encrypt PATH_TO_A_FILE/the_file.txt


Generate Jarvis Private and Public keys
---------------------------------------

Please type : jarvis generate-keys

"""

    print(help)