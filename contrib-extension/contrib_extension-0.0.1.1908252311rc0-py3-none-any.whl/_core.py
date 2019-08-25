import importlib
import site
import glob
import os
"""
    contrib에 있는 정보를 추가합니다
"""

class Extension:
    def __init__(self, use_lib_name, identi="contrib", category="category"):
        """contrib와 같은 추가 라이브러리를 관리합니다.

        Args:
            use_lib_name:   사용하려는 라이브러리의 이름을 입력합니다.
                            실제로 pip로 설치된 라이브러리이여야 가능합니다.
                            아니면 os.path에 등록이 되어 있어야합니다.
            identi: 라이브러리를 보관하는 폴더 명입니다. 
                    사용하려는 라이브러리의 하위 폴더로 존재해야합니다.
            category: 카테고리를 어떤 변수명으로 식별하는지 지정합니다.

        """
        self._me_ = use_lib_name
        self._identi_ = identi
        self._category_ = "__"+category+"__"
        self._id_ = "__id__"
        self._ext_ = {}
        self._base_dir_=None
        self.__set_base_dir__(identi)
        self.update()

    def __set_base_dir__(self, folder):
        """기본 폴더를 지정합니다.

        Args:
            folder: 폴더명을 입력합니다.
        """
        path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
        self._base_dir_ = path+"/"+folder+"/"

    def __reg__(self, path, is_sub=True):
        """라이브러리를 등록합니다.

        Args:
            path: 경로를 지정합니다.
            is_sub: 하위 카테고리인지 여부입니다.
        """
        _path = self._me_ + "."
        if is_sub:
            _path+="contrib."
        cs = importlib.import_module(_path+path)
        try:
            category = getattr(cs, self._category_)
            _id = getattr(cs, self._id_)
        except:
            return
        category = category.lower()
        _id = _id.lower()
        if category in self._ext_:
            self._ext_[category].append({"id":_id, "class":cs})
        else:
            self._ext_.update({category:[]})
            self._ext_[category].append({"id":_id, "class":cs})

    def __reg_file__(self, path):
        """파일을 등록합니다.

        Args:
            path: 파일의 경로입니다.
        """
        file_name = path.split("/")[-1]
        file_ext = path.split(".")[-1]
        file_name = file_name.replace("."+file_ext, "")
        if not file_name=="__init__":
            self.__reg__(file_name)

    def __reg_folder__(self, folder):
        """폴더를 등록합니다.

        Args:
            folder: 폴더의 경로입니다.
        """
        folder_name = folder.split("/")[-1]
        if not folder_name=="__pycache__":
            self.__reg__(folder.split("/")[-1])

    def __get_folder_list__(self):
        """폴더의 리스트를 가져옵니다.

        Returns:
            폴더의 절대 경로를 반환합니다.
        """
        folder_list = glob.glob(self._base_dir_+"*")
        folders = []
        for folder in folder_list:
            folders.append(folder.replace("\\","/"))
        return folders

    def importlib(self, lib_name, is_sub):
        self.__reg__(lib_name, is_sub)

    def update(self):
        """설정된 경로에 따라 클래스들을 등록하고 유지합니다.

        """
        folder_list = self.__get_folder_list__()
        for folder in folder_list:
            if os.path.isdir(folder):
                self.__reg_folder__(folder)    
            else:
                self.__reg_file__(folder)

    def get_class(self, category, _id):
        """등록된 클래스를 가져옵니다.

        Args:
            category: 클래스의 분류를 입력합니다.
            _id: 클래스의 아이디를 입력합니다.

        Returns:
            요청한 이름의 클래스를 반환합니다.
            obj_name에 벗어난 데이터는 None을 반환합니다.
        """
        category = category.lower()
        _id = _id.lower()
        classes = self._ext_[category]
        for cs in classes:
            if cs["id"]==_id:
                return cs['class']
        return None

    def get_info(self):
        """등록된 모든 정보를 가져옵니다.

        Returns:
            딕셔너리 형태의 데이터를 반환합니다.
        """
        return self._ext_
    
    def __str__(self):
        """등록된 정보를 출력합니다.

        Returns:
            딕셔너리를 string 형태로 출력합니다.
        """
        return str(self.get_info())