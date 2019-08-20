# coding=utf-8

from __future__ import unicode_literals
from collections import OrderedDict

from .. import Provider as PersonProvider


class Provider(PersonProvider):
    formats_female = OrderedDict((
        ('{{last_name}}{{first_name_female}}', 1.00),
    ))
    formats_male = OrderedDict((
        ('{{last_name}}{{first_name_male}}', 1.00),
    ))

    formats = formats_male.copy()
    formats.update(formats_female)

    # https://ko.wikipedia.org/wiki/%ED%95%9C%EA%B5%AD%EC%9D%98_%EC%84%B1%EC%94%A8%EC%99%80_%EC%9D%B4%EB%A6%84
    first_names_female = OrderedDict((
        ('경숙', 1),
        ('경자', 1),
        ('경희', 1),
        ('명숙', 1),
        ('명자', 1),
        ('미경', 1),
        ('미숙', 1),
        ('미영', 1),
        ('미정', 1),
        ('민서', 1),
        ('민지', 1),
        ('보람', 1),
        ('서연', 1),
        ('서영', 1),
        ('서윤', 1),
        ('서현', 1),
        ('선영', 1),
        ('수민', 1),
        ('수빈', 1),
        ('수진', 1),
        ('숙자', 1),
        ('순옥', 1),
        ('순자', 1),
        ('아름', 1),
        ('영미', 1),
        ('영숙', 1),
        ('영순', 1),
        ('영자', 1),
        ('영희', 1),
        ('예원', 1),
        ('예은', 1),
        ('예지', 1),
        ('예진', 1),
        ('옥순', 1),
        ('옥자', 1),
        ('유진', 1),
        ('윤서', 1),
        ('은경', 1),
        ('은서', 1),
        ('은영', 1),
        ('은정', 1),
        ('은주', 1),
        ('은지', 1),
        ('정숙', 1),
        ('정순', 1),
        ('정자', 1),
        ('정희', 1),
        ('지민', 1),
        ('지아', 1),
        ('지연', 1),
        ('지영', 1),
        ('지우', 1),
        ('지원', 1),
        ('지은', 1),
        ('지현', 1),
        ('지혜', 1),
        ('채원', 1),
        ('춘자', 1),
        ('하윤', 1),
        ('하은', 1),
        ('현숙', 1),
        ('현정', 1),
        ('현주', 1),
        ('현지', 1),
        ('혜진', 1),
    ))

    first_names_male = OrderedDict((
        ('건우', 1),
        ('경수', 1),
        ('광수', 1),
        ('도윤', 1),
        ('도현', 1),
        ('동현', 1),
        ('민석', 1),
        ('민수', 1),
        ('민재', 1),
        ('민준', 1),
        ('병철', 1),
        ('상철', 1),
        ('상현', 1),
        ('상호', 1),
        ('상훈', 1),
        ('서준', 1),
        ('성민', 1),
        ('성수', 1),
        ('성진', 1),
        ('성현', 1),
        ('성호', 1),
        ('성훈', 1),
        ('승민', 1),
        ('승현', 1),
        ('시우', 1),
        ('영길', 1),
        ('영수', 1),
        ('영식', 1),
        ('영일', 1),
        ('영진', 1),
        ('영철', 1),
        ('영호', 1),
        ('영환', 1),
        ('예준', 1),
        ('우진', 1),
        ('재현', 1),
        ('재호', 1),
        ('정남', 1),
        ('정수', 1),
        ('정식', 1),
        ('정웅', 1),
        ('정호', 1),
        ('정훈', 1),
        ('종수', 1),
        ('주원', 1),
        ('준서', 1),
        ('준영', 1),
        ('준혁', 1),
        ('준호', 1),
        ('중수', 1),
        ('지후', 1),
        ('지훈', 1),
        ('진우', 1),
        ('진호', 1),
        ('현우', 1),
        ('현준', 1),
    ))

    first_names = first_names_male.copy()
    first_names.update(first_names_female)

    # https://ko.wikipedia.org/wiki/%ED%95%9C%EA%B5%AD%EC%9D%98_%EC%84%B1%EC%94%A8
    last_names = OrderedDict((
        ('김', 0.10689),
        ('이', 0.07307),
        ('박', 0.04192),
        ('정', 0.02333),
        ('최', 0.02151),
        ('조', 0.01176),
        ('강', 0.01055),
        ('윤', 0.01020),
        ('장', 0.00992),
        ('임', 0.00823),
        ('한', 0.00773),
        ('오', 0.00763),
        ('서', 0.00751),
        ('신', 0.00741),
        ('권', 0.00705),
        ('황', 0.00697),
        ('안', 0.00685),
        ('송', 0.00683),
        ('류', 0.00642),
        ('전', 0.00559),
        ('홍', 0.00558),
        ('고', 0.00471),
        ('문', 0.00464),
        ('양', 0.00460),
        ('손', 0.00457),
        ('배', 0.00400),
        ('조', 0.00398),
        ('백', 0.00381),
        ('허', 0.00326),
        ('유', 0.00302),
        ('남', 0.00275),
        ('심', 0.00271),
        ('노', 0.00256),
        ('정', 0.00243),
        ('하', 0.00230),
        ('곽', 0.00203),
        ('성', 0.00199),
        ('차', 0.00194),
        ('주', 0.00194),
        ('우', 0.00194),
        ('구', 0.00193),
        ('신', 0.00192),
        ('임', 0.00191),
        ('나', 0.00186),
        ('전', 0.00186),
        ('민', 0.00171),
        ('유', 0.00167),
        ('진', 0.00159),
        ('지', 0.00153),
        ('엄', 0.00144),
    ))
