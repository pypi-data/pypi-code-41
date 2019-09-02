import argparse
import os
import requests
import shutil
from zipfile import ZipFile
from dotenv import load_dotenv


class KetricsDevTools:
    def __init__(self):
        load_dotenv('ketrics.env')

        parser = argparse.ArgumentParser()
        parser.add_argument('action', help='Available options: setup, push')
        parser.add_argument('files', nargs='*', help='List of files to upload to ketrics aplication dev instance')

        self.args = parser.parse_args()
        self.actions = {
            "setup": self.setup,
            "push": self.push
        }
        self.env = {key: os.getenv(key) for key in
                    ["KETRICS_USERNAME", "KETRICS_API_URL", "KETRICS_CDN_URL", "KETRICS_WS_URL",
                     "KETRICS_TOKEN", "applicationUUID", "dataServerUUID", "dataSourceUUID"]}

        self.build_path = "build-ketrics"
        self.build_filename = "ketrics-package.zip"

        self.handle()

    @property
    def build_fullpath(self):
        return os.path.join(self.build_path, self.build_filename)

    def handle(self):
        action = self.actions.get(self.args.action)
        if action:
            action()

    def create_from_template(self, template_path):
        output_path = template_path.replace('template.', "")

        with open(template_path) as src:
            with open(output_path, "w") as target:
                target.write(src.read().format(**self.env))
                print(f"{output_path} was created")

    def add_dir_to_zip(self, zipObj, dirName):
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath)

    def setup(self):
        self.create_from_template("public/template.index.html")
        self.create_from_template("public/template.config.js")

    def build(self):
        if os.path.exists(self.build_path) and os.path.isdir(self.build_path):
            shutil.rmtree(self.build_path)
        os.mkdir(self.build_path)

        if len(self.args.files)>0:
            with ZipFile(self.build_fullpath, 'w') as zipObj:
                for f in self.args.files:
                    if os.path.isdir(f):
                        self.add_dir_to_zip(zipObj, f)
                    else:
                        zipObj.write(f)
                    print(f"{f} has been added to the package")
            return True

        print("0 files selected!")
        return False

    def push(self):
        try:
            if self.build():
                headers = {"Authorization": f"Bearer {self.env.get('KETRICS_TOKEN')}"}
                end_point = f"{self.env.get('KETRICS_API_URL')}/applications/{self.env.get('applicationUUID')}/upload"
                files = {'file': open(self.build_fullpath, 'rb')}

                r = requests.post(end_point, headers=headers, files=files)
                r.raise_for_status()
                print("The files uploaded successfully!")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            print("The files couldn't be uploaded!")

