import os, sys
import panda3d

dir = os.path.dirname(panda3d.__file__)
del panda3d

if sys.platform in ('win32', 'cygwin'):
    path_var = 'PATH'
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dir)
elif sys.platform == 'darwin':
    path_var = 'DYLD_LIBRARY_PATH'
else:
    path_var = 'LD_LIBRARY_PATH'

if not os.environ.get(path_var):
    os.environ[path_var] = dir
else:
    os.environ[path_var] = dir + os.pathsep + os.environ[path_var]

del os, sys, path_var, dir


def _exec_tool(tool):
    import os, sys
    from subprocess import Popen
    tools_dir = os.path.dirname(__file__)
    handle = Popen(sys.argv, executable=os.path.join(tools_dir, tool))
    try:
        try:
            return handle.wait()
        except KeyboardInterrupt:
            # Give the program a chance to handle the signal gracefully.
            return handle.wait()
    except:
        handle.kill()
        handle.wait()
        raise

# Register all the executables in this directory as global functions.
egg_mkfont = lambda: _exec_tool('egg-mkfont')
flt2egg = lambda: _exec_tool('flt2egg')
x_trans = lambda: _exec_tool('x-trans')
obj2egg = lambda: _exec_tool('obj2egg')
bam2egg = lambda: _exec_tool('bam2egg')
apply_patch = lambda: _exec_tool('apply_patch')
parse_file = lambda: _exec_tool('parse_file')
dae2egg = lambda: _exec_tool('dae2egg')
check_crc = lambda: _exec_tool('check_crc')
egg_trans = lambda: _exec_tool('egg-trans')
egg_optchar = lambda: _exec_tool('egg-optchar')
image_info = lambda: _exec_tool('image-info')
egg_texture_cards = lambda: _exec_tool('egg-texture-cards')
egg_make_tube = lambda: _exec_tool('egg-make-tube')
egg_palettize = lambda: _exec_tool('egg-palettize')
build_patch = lambda: _exec_tool('build_patch')
check_md5 = lambda: _exec_tool('check_md5')
flt_info = lambda: _exec_tool('flt-info')
vrml_trans = lambda: _exec_tool('vrml-trans')
egg2x = lambda: _exec_tool('egg2x')
egg_retarget_anim = lambda: _exec_tool('egg-retarget-anim')
pfm_bba = lambda: _exec_tool('pfm-bba')
deploy_stub = lambda: _exec_tool('deploy-stub')
image_trans = lambda: _exec_tool('image-trans')
egg2c = lambda: _exec_tool('egg2c')
image_resize = lambda: _exec_tool('image-resize')
flt_trans = lambda: _exec_tool('flt-trans')
pzip = lambda: _exec_tool('pzip')
pview = lambda: _exec_tool('pview')
punzip = lambda: _exec_tool('punzip')
egg_qtess = lambda: _exec_tool('egg-qtess')
show_ddb = lambda: _exec_tool('show_ddb')
dxf_points = lambda: _exec_tool('dxf-points')
egg2flt = lambda: _exec_tool('egg2flt')
egg2bam = lambda: _exec_tool('egg2bam')
egg_topstrip = lambda: _exec_tool('egg-topstrip')
pencrypt = lambda: _exec_tool('pencrypt')
vrml2egg = lambda: _exec_tool('vrml2egg')
interrogate = lambda: _exec_tool('interrogate')
fltcopy = lambda: _exec_tool('fltcopy')
interrogate_module = lambda: _exec_tool('interrogate_module')
pdecrypt = lambda: _exec_tool('pdecrypt')
make_prc_key = lambda: _exec_tool('make-prc-key')
lwo_scan = lambda: _exec_tool('lwo-scan')
p3dcparse = lambda: _exec_tool('p3dcparse')
egg_rename = lambda: _exec_tool('egg-rename')
egg_crop = lambda: _exec_tool('egg-crop')
egg2obj = lambda: _exec_tool('egg2obj')
egg2dxf = lambda: _exec_tool('egg2dxf')
bam_info = lambda: _exec_tool('bam-info')
dxf2egg = lambda: _exec_tool('dxf2egg')
pfm_trans = lambda: _exec_tool('pfm-trans')
x2egg = lambda: _exec_tool('x2egg')
check_adler = lambda: _exec_tool('check_adler')
multify = lambda: _exec_tool('multify')
test_interrogate = lambda: _exec_tool('test_interrogate')
egg_list_textures = lambda: _exec_tool('egg-list-textures')
text_stats = lambda: _exec_tool('text-stats')
lwo2egg = lambda: _exec_tool('lwo2egg')

