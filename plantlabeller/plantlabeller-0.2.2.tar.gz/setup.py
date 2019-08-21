from setuptools import setup,find_packages

with open('./plantlabeller/README.md',encoding='utf-8') as f:
        longtext=f.read()


setup(
        name="plantlabeller",
        version="0.2.2",
        keywords=("pip3","GridFree","droneimage","yanghu"),
        description="label plants",
        #long_description="A pixel-level label plants in drone images.\n Implement Python version= 3.6.5,QGIS version = 3.4 \n *** Need to modify matplotlibrc file *** backend: TkAgg",
        long_description=longtext,
        long_description_content_type='text/markdown',
        license = "MIT Licence",

        url="http://css.wsu.edu/people/research-associates/yang-hu/",
        author="yangh",
        author_email="yang.hu@wsu.edu",

        packages=find_packages(),
        include_package_data=True,
        platforms="any",
        install_requires=["pillow","opencv-python","matplotlib","scipy","sklearn","GDAL>=2.4.2","scikit-image"],
        python_requirements='>=3'
        )
