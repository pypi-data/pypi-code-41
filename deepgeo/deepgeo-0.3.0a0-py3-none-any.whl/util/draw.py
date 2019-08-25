from PIL import Image as pImage, ImageDraw, ImageFont
import numpy as np

from deepgeo.util import byte as Byte, create as Create
from deepgeo.util.polygon import get_info

class Tool:
    # option
    WithFill = 1
    WithoutFill = 2

    @staticmethod
    def __load_image__(ori_image):
        image = ori_image._get_image_()
        image = image.convert("RGBA")
        y, x, z = ori_image.to_numpy().shape
        # 도화지 가져오기
        mask_image = pImage.fromarray(np.uint8(np.zeros((y, x, z + 1))))
        return ImageDraw.Draw(mask_image), mask_image

    @staticmethod
    def box(image, x, y, width, height, color, opacity, option=WithFill):
        if isinstance(image, ImageDraw.Draw):
            fill_color = (color[0],color[1],color[2],opacity)
            coordinates = [x,y,width,height]
            if option==WithFill:
                image.rectangle(coordinates, fill=fill_color, outline=fill_color)
            else:
                image.rectangle(coordinates, outline=fill_color)
            return image, None
        else:
            image, mask_iamge = __load_image__(image)
            return box(image, x, y, width, height, color, opacity), mask_iamge

    @staticmethod
    def text(image, text, x, y, color, opacity, font, font_size, option=WithoutFill):
        if isinstance(image, ImageDraw.Draw):
            fill_color = (color[0],color[1],color[2],opacity)
            if option == WithoutFill:
                width = x + Byte.count(text)*+font_size*0.5
                image = box(image, x, y, width, y+(font_size*1.2))
                fill_color = (255, 255, 255, opacity)
            image.text((x,y), text, fill=fill_color, font=font)
            return image, None
        else:
            image, mask_iamge = __load_image__(image)
            return text(image, text, x, y, color, font, option), mask_iamge

    @staticmethod
    def polygon(image, coordinates, color, opacity, option = WithFill):
        if isinstance(image, ImageDraw.Draw):
            fill_color = (color[0],color[1],color[2],opacity)
            if option==WithFill:
                image.polygon(coordinates, fill=fill_color, outline=fill_color)
            else:
                image.polygon(coordinates, outline=fill_color)
            return image, None
        else:
            image, mask_iamge = __load_image__(image)
            return polygon(image, coordinates, color, opacity, option), mask_iamge

    @staticmethod
    def set_mask(ori, cpy, color):
        _, _, z = cpy.shape
        _, _, o = ori.shape
        for i in range(z):
            for j in range(o):
                a = cpy[:, :, i]
                b = color[i][j]
                k = a * b
                ori[:, :, j] = ori[:, :, j] + k
        return ori

class Annotations:
    TextWithBackground = 1
    PolygonToRectangle = 2
    PolygonAndRectangle = 3
    PolygonToRectangleTextWithBackground = 4
    PolygonAndRectangleTextWithBackground = 5

    @staticmethod
    def _draw_annotation_(draw_image, annotation, color, font, opacity=0.5,option="",font_size=0):
        
        # Option is not Work
        if 'areaInImage' in annotation:
            areaInImage = annotation['areaInImage']
            coordinates = areaInImage['coordinates'] if 'coordinates' in areaInImage else None
            XY = None
            if 'type' in areaInImage:
                opacity = int(255 * opacity)
                sel_type = areaInImage['type']
                
                fill_color = (color[0],color[1],color[2],opacity)
                if sel_type in ['polygon','Polygon']:
                    if option in ["PolygonToRectangle", "PolygonToRectangleTextWithBackground"]:
                        sel_type="rectangle"
                        poly_info = get_info(coordinates)
                        coordinates = poly_info['diagonal']
                    else:
                        XY = get_info(coordinates)
                        coordinates = sum(coordinates, [])
                        draw_image.polygon(coordinates, fill=fill_color)
                        if option in ['PolygonAndRectangleTextWithBackground']:
                            sel_type="rectangle2"
                            coordinates = XY['diagonal']
                if sel_type in ['rectangle','Rectangle', 'mbr','bbox','BBOX','rectangle2']:
                    if sel_type in ['rectangle2']:
                        draw_image.rectangle(coordinates, outline=fill_color)
                    else:
                        draw_image.rectangle(coordinates, fill=fill_color)
                    XY = {'diagonal':coordinates}
                
                opacity = 255
        if 'annotationText' in annotation:
            fill_color = (color[0],color[1],color[2],opacity)
            xy1 = XY['diagonal'][0:2]
            xy2 = XY['diagonal'][2:4]
            text = annotation['annotationText']
            x = xy1[0] if xy1[0]<xy2[0] else xy2[0]
            y = xy1[1] if xy1[1]<xy2[1] else xy2[1]
            y = y - (font_size*1.2)
            if y<0:
                y = xy1[1] if xy1[1]>xy2[1] else xy2[1]
                y + (font_size*1.2)
            if option in ['TextWithBackground', 'PolygonToRectangleTextWithBackground','PolygonAndRectangleTextWithBackground']:
                width = x+Byte.count(text)*+font_size*0.5
                coordinates = [x,y,width,y+(font_size*1.2)]
                draw_image.rectangle(coordinates, fill=fill_color)
                fill_color = (255,255,255,opacity)
            draw_image.text((x,y), text, fill=fill_color, font=font)

    @staticmethod
    def draw(image, annotations, opacity, font, font_size, option=1):
        """
            # draw_annotations : 이미지에 annotation 데이터에 따라 그려줍니다.
            annotations : STPhoto의 annotations Dictionary 데이터만 사용 가능합니다.
            annotations is "" or annotations is not dict : 아무것도 하지 않습니다.
            annotations type is dict : dDictionary 데이터에 따라 이미지를 변형 및 위에 그립니다.
            -------------------------------------
            opacity : 객체를 식별할 폴리곤이나 박스의 투명도를 설정한다.
            -------------------------------------
            font : 사용할 글꼴을 선택합니다. 이 글꼴은 Image.py가 있는 폴더의 fonts 폴더 내에 있으면 인식합니다.
            -------------------------------------
            font_size : 폰트의 크기를 지정한다.
            0 : 폰트의 크기를 이미지 크기에 맞게 비례하여 지정한다.
            1 이상 : 해당 크기에 맞게 표시한다.
            -------------------------------------
            option:
                - TextWithBackground: 텍스트에 배경을 줍니다.
                - PolygonToRectangle: 폴리곤을 박스로 변환합니다.
                - PolygonToRectangleTextWithBackground: 위 옵션 모드 적용
                
        """
        
        
        if annotations is None or not isinstance(annotations, dict) == 0:
            return

        draw_mask_image, mask_image = Tool.__load_image__(image)
        colors = Create.colors(len(annotations))
        
        for idx in range(len(annotations)):
            annotation = annotations[idx]
            _draw_annotation_(draw_mask_image, annotation, colors[idx], opacity=opacity, 
                                                    option=option, font=font, font_size=font_size)
        if mask_image:
            image = pImage.alpha_composite(image, mask_image)
        return image