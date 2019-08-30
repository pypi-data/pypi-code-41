class Env:

    def create_url(environment, versionNumber):
            url = {
                'sandbox' : f"https://partnershealthcare.sb01.workfront.com/attask/api/v{versionNumber}",
                'preview' : f"https://partnershealthcare.preview.workfront.com/attask/api/v{versionNumber}", 
                'prod' : f"https://partnershealthcare.my.workfront.com/attask/api/v{versionNumber}"
            }
            return url.get(environment)

if __name__ == "__main__":
    Env()