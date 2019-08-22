# coding=utf-8

from fanstatic import Library, Resource, Group

library = Library('video.js', 'resources')

# By default, we bundle Video.js with Mozilla's excellent VTT.js.
videojs_js = Resource(
    library, 'video.js', minified='video.min.js')

# If you don't need VTT.js functionality for whatever reason, you can use one
# of the Video.js copies that don't include VTT.js.
videojs_js_novtt = Resource(
    library, 'alt/video.novtt.js', minified='alt/video.novtt.min.js')

# Video.js will be bundling VHS by default for ease of use for new users.
# However, some people don’t want VHS or are using another plugin.
# For this, we have a separate build of Video.js which doesn’t include VHS.
# https://blog.videojs.com/introducing-video-js-http-streaming-vhs/
videojs_core_js = Resource(
    library, 'alt/video.core.js', minified='alt/video.core.min.js')

videojs_core_js_novtt = Resource(
    library, 'alt/video.core.novtt.js', minified='alt/video.core.novtt.min.js')

videojs_css = Resource(library, 'video-js.css', minified='video-js.min.css')

videojs = Group(depends=[videojs_js, videojs_css])

videojs_novtt = Group(
    depends=[
        videojs_js_novtt,
        videojs_css])

videojs_core = Group(depends=[videojs_core_js, videojs_css])

videojs_core_novtt = Group(
    depends=[
        videojs_core_js_novtt,
        videojs_css])

locales = {}

videojs_ar = locales['ar'] = Resource(
    library, 'lang/ar.js',
    depends=[videojs])

videojs_ba = locales['ba'] = Resource(
    library, 'lang/ba.js',
    depends=[videojs])

videojs_bg = locales['bg'] = Resource(
    library, 'lang/bg.js',
    depends=[videojs])

videojs_ca = locales['ca'] = Resource(
    library, 'lang/ca.js',
    depends=[videojs])

videojs_cs = locales['cs'] = Resource(
    library, 'lang/cs.js',
    depends=[videojs])

videojs_cy = locales['cy'] = Resource(
    library, 'lang/cy.js',
    depends=[videojs])

videojs_da = locales['da'] = Resource(
    library, 'lang/da.js',
    depends=[videojs])

videojs_de = locales['de'] = Resource(
    library, 'lang/de.js',
    depends=[videojs])

videojs_el = locales['el'] = Resource(
    library, 'lang/el.js',
    depends=[videojs])

videojs_en = locales['en'] = Resource(
    library, 'lang/en.js',
    depends=[videojs])

videojs_es = locales['es'] = Resource(
    library, 'lang/es.js',
    depends=[videojs])

videojs_fa = locales['fa'] = Resource(
    library, 'lang/fa.js',
    depends=[videojs])

videojs_fi = locales['fi'] = Resource(
    library, 'lang/fi.js',
    depends=[videojs])

videojs_fr = locales['fr'] = Resource(
    library, 'lang/fr.js',
    depends=[videojs])

videojs_gl = locales['gl'] = Resource(
    library, 'lang/gl.js',
    depends=[videojs])

videojs_he = locales['he'] = Resource(
    library, 'lang/he.js',
    depends=[videojs])

videojs_hr = locales['hr'] = Resource(
    library, 'lang/hr.js',
    depends=[videojs])

videojs_hu = locales['hu'] = Resource(
    library, 'lang/hu.js',
    depends=[videojs])

videojs_it = locales['it'] = Resource(
    library, 'lang/it.js',
    depends=[videojs])

videojs_ja = locales['ja'] = Resource(
    library, 'lang/ja.js',
    depends=[videojs])

videojs_ko = locales['ko'] = Resource(
    library, 'lang/ko.js',
    depends=[videojs])

videojs_nb = locales['nb'] = Resource(
    library, 'lang/nb.js',
    depends=[videojs])

videojs_nl = locales['nl'] = Resource(
    library, 'lang/nl.js',
    depends=[videojs])

videojs_nn = locales['nn'] = Resource(
    library, 'lang/nn.js',
    depends=[videojs])

videojs_oc = locales['oc'] = Resource(
    library, 'lang/oc.js',
    depends=[videojs])

videojs_pl = locales['pl'] = Resource(
    library, 'lang/pl.js',
    depends=[videojs])

videojs_pt_br = locales['pt-BR'] = Resource(
    library, 'lang/pt-BR.js',
    depends=[videojs])

videojs_pt_bt = locales['pt-PT'] = Resource(
    library, 'lang/pt-PT.js',
    depends=[videojs])

videojs_ru = locales['ru'] = Resource(
    library, 'lang/ru.js',
    depends=[videojs])

videojs_sk = locales['sk'] = Resource(
    library, 'lang/sk.js',
    depends=[videojs])

videojs_sr = locales['sr'] = Resource(
    library, 'lang/sr.js',
    depends=[videojs])

videojs_sv = locales['sv'] = Resource(
    library, 'lang/sv.js',
    depends=[videojs])

videojs_tr = locales['tr'] = Resource(
    library, 'lang/tr.js',
    depends=[videojs])

videojs_uk = locales['uk'] = Resource(
    library, 'lang/uk.js',
    depends=[videojs])

videojs_vi = locales['vi'] = Resource(
    library, 'lang/vi.js',
    depends=[videojs])

videojs_zh_cn = locales['zh-CN'] = Resource(
    library, 'lang/zh-CN.js',
    depends=[videojs])

videojs_zh_tw = locales['zh-TW'] = Resource(
    library, 'lang/zh-TW.js',
    depends=[videojs])
