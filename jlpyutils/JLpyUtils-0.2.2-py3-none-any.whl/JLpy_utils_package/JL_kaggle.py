
def competition_download_files(competition, verbose = 1):
    from kaggle.api.kaggle_api_extended import KaggleApi
    import sys, os, zipfile
    
    api = KaggleApi()
    api.authenticate()
    
    files = api.competition_download_files(competition, path = competition)

    #unzip files
    for file in os.listdir(competition):
        if 'zip' in file:
            with zipfile.ZipFile(os.path.join(competition, file) , 'r') as zip_ref:
                zip_ref.extractall(competition)
            os.remove(os.path.join(competition, file))
    
    if verbose>=1:
        print('competition files:')
        for file in os.listdir(competition):
            print(file, '\t',round(os.path.getsize(os.path.join(competition,file))*10**-6,2),'Mb')