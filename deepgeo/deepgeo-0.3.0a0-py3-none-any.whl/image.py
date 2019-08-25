# Defalut Info
__deepgeo_category__ = "type"
__id__="Image"

#Lib
import os
import numpy as np
from PIL import Image as pImage

from deepgeo.util import create, url, error
from deepgeo.util.exif import EXIF

class obj:
    def __init__(self, data, annotations = None):
        self._uri_= None #uri
        self._path_= None #create.folder(image_path)

        if isinstance(data, tuple):
            self.__fromURI__(data)
        elif isinstance(data, np):
            self.__fromNumpy__(data)
        else:
            raise error.SupportFormatError(type(data))

        self._file_name_ = url.download_image(self._uri_, self._path_)
        
        self._uri_ = self._path_+self._file_name_

        self._image_ = None
        if annotations is None:
            annotations = []
        self._exif_ = EXIF(self._get_image_(), self.get_path() + self.get_file_name())
        self._annotation_ = annotations

        ori = self._exif_.getEXIF('Image Orientation')
        if ori is not None:
            self.save(self._path_, image=self.rotation(ori))

    def __fromNumpy__(self, data):
        image= pImage.fromarray(data)
        self._uri_ = create.name("png")
        self._path_ = create.folder("tmp")
        self.save(create_folder=self._path_, image_name = self._uri_, image_format = "png",image=image)
        del image
    
    def __fromURI__(self, data):
        self._uri_, self._path_ = data
        self._path_ = create.folder(self._path_)

    def __str__(self):
        return self.get_file_name()
    
    def _open_(self):
        return pImage.open(self._path_ + self._file_name_).convert('RGB')

    def _get_image_(self, image=None, is_new=False):
        """
            # _get_image_ : 이미지를 가져옵니다.
            is_new : 이미지를 새로 가져올 것인지 물어봅니다.
        """
        if image is not None:
            return image
        image = self._image_
        if is_new is True:
            image = self._open_()
        elif image is None:
            self._image_ = self._open_()
            image = self._image_
        else:
            return self._image_
        if image is None:
            raise error.ImageLoadError(self._file_name_)
        else:
            return image
        
    def add_annotation(self, annotation):
        """
            # add_annotation : annotation을 추가합니다.
            annotation : list 혹은 dict 데이터를 받습니다. STPhoto Type의 양식을 따릅니다.
        """
        if self._annotation_ is None:
            self._annotation_=[]
        if isinstance(annotation, list) is True:
            self._annotation_.extend(annotation)
        elif isinstance(annotation, dict) is True:
            self._annotation_.append(annotation)
        else:
            raise error.SupportFormatError(type(annotation))

    def get_annotation(self):
        """
            # get_annotation : annotation을 반환합니다.
        """
        return self._annotation_

    def create_thumbnail(self, image_name = "", image_size = (128,128), image_path = ""):
        """
            # create_thumbnail : thumbnail 생성합니다.
            image_size : 조정할 이미지 크기입니다.
            -------------------------------------
            image_name : 생성할 thumbnail 이름입니다.
            
            image_name is "" : 동일한 이름 사용합니다.
            image_name is None : 랜덤한 이름 사용합니다.
            image_name is TEXT : 입력된 이름 사용합니다.
            -------------------------------------
            image_path : thumbnail를 저장할 경로입니다.
            image_path is "" : 기존 경로에 thumbnail 이름을 추가해서 저장합니다.
            image_path is None : 기존 경로에 생성합니다.
        """
        image = self._get_image_(is_new=True)
        if image_path == "":
            image_path = self._path_ + 'thumbnail'
        elif image_path is None:
            image_path = self._path_
        image_path = create.folder(image_path)
        try:
            image.thumbnail(image_size)
        except:
            pass
        self.save(image_path, image_name=image_name, image=image)
        return image_path

    def save(self, create_folder, image_name = "", image_format = "", is_with_exif = True, image=None):
        """
            # save : 이미지를 파일로 저장합니다.
            create_folder : 이미지를 저장할 폴더 경로입니다.
            -------------------------------------
            is_with_exif : EXIF 메타 데이터까지 저장할 것인지 여부 값입니다.
            -------------------------------------
            image : 저장할 이미지 객체(Pillow Object)입니다.
            image is None : 기본 객체입니다.
            image is Pillow Object : Pillow Object 저장합니다.
            -------------------------------------
            image_name : 저장할 파일 이름입니다.
            image_name is "" : 동일한 이름 사용합니다.
            image_name is None : 랜덤한 이름 사용합니다.
            image_name is TEXT : 입력된 이름 사용합니다.
            -------------------------------------
            image_foramt : 저장할 파일의 포맷입니다.
            image_format is "" : 동일한 포맷 사용합니다.
            image_format is None : png 사용합니다.
            image_format is TEXT : 입력된 포맷 사용합니다.
                - 지원 Format : 'BMP','EPS','GIF','ICNS','ICO',
                                'IM','JPEG','MSP','PCX','PNG',
                                'PPM','SGI','SPIDER','WEBP',
                                'XBM','PALM','PDF','XV'
        """
        image = self._get_image_(image)        
        image = image.convert("RGB")
        
        #create_folder 기본 값 처리
        create_folder = create.folder(create_folder)

        # image_format 기본 값 처리
        ext = self._file_name_.split(".")[-1]
        if image_format is None:
            image_format = "png"
        elif  image_format == "":
            image_format = ext
        else:
            support_format = ['BMP','EPS','GIF','ICNS','ICO','IM','JPEG','MSP','PCX','PNG','PPM','SGI','SPIDER','WEBP','XBM','PALM','PDF','XV']
            if not(image_format.upper() in support_format):
                raise error.SupportFormatError(image_format)

        image_format = image_format.lower().replace(".","")

        if image_format in ['PNG']:
            image = image.convert("RGBA")

        # image_name 기본 값 처리
        if image_name == "":
            image_name = self._file_name_.split("."+ext)[0] + "." + image_format
        elif image_name is None:
            image_name = create.name(image_format, create_folder)
        else:
            image_name = image_name+"."+image_format
        
        full_path = create_folder+image_name

        # image EXIF(META) 정보 유지
        if is_with_exif is True:
            bexif = self._exif_.getBinaryEXIF()
            if bexif is not None:
                image.save(full_path, exif=bexif)
                return full_path

        image.save(full_path)
        return full_path

    def delete(self):
        """
            # delete : 다운로드 한 이미지를 삭제합니다.
        """
        os.remove(self._path_+self._file_name_)

    def get_size(self):
        return self._get_image_().size

    def rotation(self, ori):
        ori = ori.values
        image = self._image_
        try:
            if 2 in ori:
                image = image.transpose(pImage.FLIP_LEFT_RIGHT)
            elif 3 in ori:
                image = image.transpose(pImage.FLIP_LEFT_RIGHT)
                image = image.transpose(pImage.FLIP_TOP_BOTTOM)
            elif 4 in ori:
                image = image.transpose(pImage.FLIP_TOP_BOTTOM)
            elif 5 in ori:
                image = image.transpose(pImage.FLIP_LEFT_RIGHT)
                image = image.transpose(pImage.ROTATE_90)
            elif 6 in ori:
                image = image.transpose(pImage.ROTATE_270)
            elif 7 in ori:
                image = image.transpose(pImage.ROTATE_90)
                image = image.transpose(pImage.FLIP_LEFT_RIGHT)
            elif 8 in ori:
                image = image.transpose(pImage.ROTATE_270)
        except Exception as ex:
            raise "image Rotation ERROR : " + str(ex)

        self._exif_.setOrientation(ori)
        self._image_ = image
    
    def to_PILImage(self):
        return self._image_

    def to_numpy(self):
        """
            # to_numpy : 이미지 데이터를 Numpy 데이터로 변환합니다.
        """
        image = self._get_image_()
        return np.array(image)

    def to_gray_numpy(self):
        """
            # to_gray_numpy : 이미지를 그레이스케일로 변경 후 넘파이 데이터로 반환합니다.
        """
        image = self._get_image_()
        image = image.convert("LA")
        return np.array(image)

    def get_path(self):
        return self._path_

    def get_file_name(self):
        return self._file_name_

    def get_info(self):
        """
            # get_info : 이미지의 정보를 가져옴니다. (Include EXIF)
        """
        result = {"Width":None, "Height":None, "Latitude":None, "Longitude":None, 
                "Altitude":None, "Time":None, "HorizontalAngle":None, 
                "Direction2d":None, "Distance":None}
        
        # 크기
        result['Width'], result['Height'] = self.get_size()

        # 위치 정보
        location = self._exif_.get_location()
        if location is not None:
            result['Longitude'], result['Latitude'] = location
        result['Altitude'] = self._exif_.get_altitude()
        
        # 시간
        result['Time'] = self._exif_.get_datetime()

        # 앵글 각도
        result['HorizontalAngle'] = 66

        # 방향
        result['Direction2d'] = self._exif_.get_direction()
        
        # 거리
        result['Distance'] = self._exif_.get_distance()

        return result

    def get_uri(self):
        return self._uri_

    def display(self):
        print(self.get_file_name())