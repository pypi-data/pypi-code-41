"""Console script for picturebot."""

import sys
import os
import json
import shutil
import subprocess
import click
import picturebot as pb
import picturebot.helper as helper
import generalutils.guard as grd

def Location(path):
    '''Config file location method
    
    Args:
        path (string): Path to the config file
    '''

    click.echo(f'Config file location: {path}')

    # Check whether the the path to the config file exists
    grd.Filesystem.PathExist(path)

    #  Open the config file
    os.system(f"start {path}")  

def Create(config):
    '''Setup the workspace method
    
    Args:
        config (Config): Config data object
    '''

    # Get the current working directory of where the script is executed
    cwd = os.getcwd()

    #Check whether the current working directory exists
    grd.Filesystem.PathExist(cwd)

    #Check whether the workplace folder exists    
    grd.Filesystem.PathExist(config.Workplace)

    counter = 0

    # Only create the flow when the script is executed from the workspace directory
    if cwd == config.Workplace:
        #Loop-over the workflows
        for flow in config.Workflow:
            pathToFlow = helper.FullFilePath(config.Workplace, flow)

            # Only create non existing flows
            if not grd.Filesystem.IsPath(pathToFlow):
                helper.CreateFolder(pathToFlow)
                grd.Filesystem.PathExist(pathToFlow)
                click.echo(f'Flow created: {pathToFlow}')
                counter += 1 
        
        click.echo(f"Flows created: {counter}")
    else:
        click.echo(f'Script command should be called from the workspace directory: {config.Workplace}')

def Rename(config):
    '''Method to rename files within the baseflow directory
    
    Args:
        config (Config): Config data object
    '''

    # Get the current working directory of where the script is executed
    cwd = os.getcwd()

    # Check whether the current working directory exists
    grd.Filesystem.PathExist(cwd)

    # Obtain the name of the base directory of the current working directory
    basename = os.path.basename(cwd)
    
    # Obtain the path to the base flow project
    pathToBaseflowProject = helper.FullFilePath(config.Workplace, config.Baseflow, basename)
    # Check whether the the path to the base flow project exists
    grd.Filesystem.PathExist(pathToBaseflowProject)

    # Only rename filenames within a baseflow project directory
    if cwd == pathToBaseflowProject:
        # Loop-ver the workflows and add an project directory to each flow
        for flow in config.Workflow:
            # Obtain the path to the project flow
            pathToFlowProject = helper.FullFilePath(config.Workplace,flow,basename)

            # Check if folder exists and whether the directory isn't the backup flow
            if (not grd.Filesystem.IsPath(pathToFlowProject)) and (flow != config.Backup):
                helper.CreateFolder(pathToFlowProject)

                grd.Filesystem.PathExist(pathToFlowProject)

                click.echo(f'Project created: {pathToFlowProject}')

        print('\r\n')
    else:
        click.echo(f'Script command should be called from the baseflow directory: {pathToBaseflowProject}')

    flow = ''
    counter = 0

    # Loop over every word of the flow name directory
    for i in basename.split(' '):
        # Append the individual words to an '_'
        flow += f'{i}_'

    # Obtain the original picture name within a flow directory
    pictures = os.listdir(cwd)
    # sort by date
    pictures.sort(key=os.path.getmtime)

    # Loop over every picture withing the flow directory
    for index, picture in enumerate(pictures, 1):
        # Get the extension of the original picture
        extension = picture.split('.')[1]

        # Get absolute path to the picture
        pathToPicture = os.path.join(cwd,picture)

        # Check whether the absolute path to the picture is existing
        grd.Filesystem.PathExist(pathToPicture)

        # Get the new name for the picture
        newName = f"{flow}{index}.{extension}"

        # Obtain the absolute path to the new picture name
        pathToNewPicture = os.path.join(cwd, newName)

        # Only rename the changed files
        if not pathToNewPicture == pathToPicture:
            # Rename the picture file
            os.rename(pathToPicture, pathToNewPicture)

            click.echo(f"Renaming: {picture} -> {newName}")

            # Check whether the new picture file exists after renaming
            grd.Filesystem.PathExist(pathToNewPicture)

            counter += 1

    click.echo(f"Renamed files: {counter}")

def Version():
    '''Method which prints the current script version'''

    click.echo(f'Script version: {pb.__version__}')
   
def Backup(config):
    '''Method to backup files from the baseflow project

    Args:
        config (Config): Config data object
    '''

    # Get the current working directory of where the script is executed
    cwd = os.getcwd()

    # Check whether the current working directory exists
    grd.Filesystem.PathExist(cwd)

    # Obtain the name of the base directory of the current working directory
    basename = os.path.basename(cwd)
    
    # Obtain the path to the base flow project
    pathToBaseflowProject = helper.FullFilePath(config.Workplace, config.Baseflow, basename)

    # Check whether the the path to the base flow project exists
    grd.Filesystem.PathExist(pathToBaseflowProject)

    # Check whether you're within the backup flow directory
    if cwd == pathToBaseflowProject:
        # Loop-ver the workflows
        for flow in config.Workflow:
            # Obtain the path to the project flow
            pathToFlowProject = helper.FullFilePath(config.Workplace, flow, basename)

            # Check if folder exists and whether the flow is the backup flow
            if (not grd.Filesystem.IsPath(pathToFlowProject)) and (flow == config.Backup):
                helper.CreateFolder(pathToFlowProject)

                # Check whether the project is successfully created within the backup directory
                grd.Filesystem.PathExist(pathToFlowProject)

                click.echo(f'Backup project created: {pathToFlowProject}')

        print('\r\n')
    else:
        click.echo(f'Script command should be called from the baseflow directory: {pathToBaseflowProject}')

    # Obtain the filenames within the baseflow directory
    pictures = os.listdir(cwd)

    counter = 0

    for picture in pictures:
        # Obtain the path to the baseflow directory
        pathToBaseflow = helper.FullFilePath(config.Workplace, config.Baseflow, basename)
        # Check whether the baseflow directory exists
        grd.Filesystem.PathExist(pathToBaseflow)

        # Obtain the path the source picture within the baseflow directory
        pathToPictureSource = helper.FullFilePath(pathToBaseflow, picture)
        # Check whether the source picture path exists
        grd.Filesystem.PathExist(pathToPictureSource)
        
        # Obtain the path to the backupflow directory
        pathToBackupFlow = helper.FullFilePath(config.Workplace, config.Backup, basename)
        # Check whether the backupflow directory exists
        grd.Filesystem.PathExist(pathToBackupFlow)

        # Obtain the full path name to the picture's destition path
        pathToPictureDestination = helper.FullFilePath(pathToBackupFlow, picture)
        
        click.echo(f'Copying: {picture} -> {pathToBackupFlow} [{counter + 1}/{len(pictures)}]')

        # Copying picture from source to destination including the metadata
        shutil.copy2(pathToPictureSource, pathToPictureDestination)

        # Check whether the file is successfully copied
        grd.Filesystem.PathExist(pathToPictureDestination)

        counter += 1

    click.echo(f"Copied files: {counter}")

def Completed(config):
    '''Method to check whether a shoot is completely edited 

    Args:
        config (Config): Config data object
    '''

    # Get the current working directory of where the script is executed
    cwd = os.getcwd()

    # Check whether the current working directory exists
    grd.Filesystem.PathExist(cwd)
    
    # Check whether the script is executed from the workspace directory
    grd.Filesystem.PathCwdExists(config.Workplace, cwd)

        # Obtain the path to the the edit root directory
    pathToEditedRoot = helper.FullFilePath(config.Workplace, config.Edited)

    # Check whether the path to the edit root directory exists
    grd.Filesystem.PathExist(pathToEditedRoot)

    # Loopover every shoot within the edit directory
    for shoot in os.listdir(pathToEditedRoot):
        # Obtain the path to the shoot within the edit root directory
        pathToEditedShoots = helper.FullFilePath(pathToEditedRoot, shoot)

        # Check whether the shoot exists within the edit root directory
        grd.Filesystem.PathExist(pathToEditedShoots)

        # Amount of pictures within the edit shoot directory
        shootAmountPicturesEdited = len(os.listdir(pathToEditedShoots))

        pathToSelectedShoot = helper.FullFilePath(config.Workplace, config.Selection, shoot)
        grd.Filesystem.PathExist( pathToSelectedShoot)

        # Amount of pictures within the selection shoot directory
        shootAmountPicturesSelection = len(os.listdir(pathToSelectedShoot))

        # Check whether the amount of pictures are equal
        if shootAmountPicturesEdited != shootAmountPicturesSelection:
            print(f'Shoot: {shoot} is not fully edited')

@click.command()
@click.option('--create', '-c', is_flag=True, help='Create workspace directory')
@click.option('--rename', '-r', is_flag=True, help='Rename the files in the main flow directory')
@click.option('--location', '-l', is_flag=True, help='Config file location')
@click.option('--version', '-v', is_flag=True, help='Script version')
@click.option('--backup', '-b', is_flag=True, help='Create a backup folder from the baseflow directory')
@click.option('--completed', '-cmp', is_flag=True, help='Create a backup folder from the baseflow directory')
def main(create,rename, location, version, backup, completed):
    """Console script for picturebot."""
    
    pathToConfig = helper.FullFilePath("config.json")
    
    # Check whether the path to the confile exists
    grd.Filesystem.PathExist(pathToConfig)

    with open(pathToConfig) as f:
         # Load data from file
        data = json.load(f)
        config = helper.Config(data['workplace'], data['workflow'], data['baseflow'], data['backup'], data['selection'], data['edited'])

    if create:
        Create(config)
    elif rename:
        Rename(config)
    elif location:
        Location(pathToConfig)
    elif version:
        Version()
    elif backup:
        Backup(config)
    elif completed:
        Completed(config)
    else:
        click.echo('No arguments were passed, please enter --help for more information')

if __name__ == "__main__":
    main() # pragma: no cover
