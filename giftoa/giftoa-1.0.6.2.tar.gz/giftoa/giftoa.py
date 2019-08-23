#!/usr/bin/python3

# Copyright (c) 2016, Teriks
# All rights reserved.

# giftoa is distributed under the following BSD 3-Clause License

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import os
import atexit
import os.path
import tempfile
import subprocess
import re
import argparse
import imghdr
import urllib.request
import urllib.parse
import urllib.error
import shutil
import platform

__author__ = 'Teriks'
__copyright__ = 'Copyright (c) 2016 Teriks'
__license__ = 'Three Clause BSD'
__version__ = '1.0.6.0'

C_HEADERS = """
#include <signal.h>
#include <curses.h>
#include <stdlib.h>
#include <time.h>

"""

GETTIME_DEFAULT_IMPL = """

#define _clock_gettime_monotonic(t) clock_gettime(CLOCK_MONOTONIC, t)

"""

# For MacOS < 10.12
GETTIME_MACOS_IMPL = """

#include <mach/mach_time.h>

#define ORWL_NANO (+1.0E-9)
#define ORWL_GIGA UINT64_C(1000000000)

static double _orwl_timebase = 0.0;
static uint64_t _orwl_timestart = 0;

int _clock_gettime_monotonic(struct timespec* t) {

  if (!_orwl_timestart) {
    mach_timebase_info_data_t tb = { 0 };
    mach_timebase_info(&tb);
    _orwl_timebase = tb.numer;
    _orwl_timebase /= tb.denom;
    _orwl_timestart = mach_absolute_time();
  }

  double diff = (mach_absolute_time() - _orwl_timestart) * _orwl_timebase;

  t->tv_sec = diff * ORWL_NANO;
  t->tv_nsec = diff - (t->tv_sec * ORWL_GIGA);
  
  return 0;
}

"""

C_PROGRAM = """

WINDOW * mainwin = 0;

void cleanup()
{
    if(mainwin!=0)
    {
        delwin(mainwin);
        endwin();
        refresh();
    }
}

void signal_handler(int s)
{
    cleanup();
    exit(EXIT_SUCCESS);
}


int main(int argc, char *argv[]) 
{
    struct timespec frameDelay;

    GIFTOA_FRAMEDELAY_INIT(frameDelay)

    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = signal_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, NULL);


    if ( (mainwin = initscr()) == NULL ) {
        fprintf(stderr, "Error initialising ncurses.\\n");
        exit(EXIT_FAILURE);
    }
        
    const char * frames[] = GIFTOA_FRAMES_INIT;
    int framecnt = sizeof(frames) / sizeof(const char*);

    curs_set(0);

    nodelay(mainwin, 1);

    struct timespec startTime;
    struct timespec endTime;
    struct timespec computedDelay;

    int frame = 0;

    while(true) 
    {
        _clock_gettime_monotonic(&startTime);

        if(getch() == 27)
        {
            break;
        }

        clear();
        mvaddstr(0, 0, frames[frame]);
        refresh();
        
        frame = frame == framecnt-1 ? 0 : frame+1;

        _clock_gettime_monotonic(&endTime);

        time_t tv_sec = frameDelay.tv_sec - (endTime.tv_sec - startTime.tv_sec);
        long tv_nsec = frameDelay.tv_nsec - (endTime.tv_nsec - startTime.tv_nsec);

        // hope that time_t is signed?

        computedDelay.tv_sec = tv_sec < 0 ? 0 : tv_sec;
        computedDelay.tv_nsec = tv_nsec < 0 ? 0 : tv_nsec;

        nanosleep(&computedDelay, NULL);
    }

    cleanup();

    return EXIT_SUCCESS;
}
"""


def is_url(path):
    return urllib.parse.urlparse(path).scheme != ""


# This class allows a named temp file to be closed after writing without instantly deleting it, 
# which is something NamedTemporaryFile will do by default.  This class deletes the temporary file
# when the program exits however, which is something NamedTemporaryFile does not do when its 'delete'
# parameter is set to False.

class GCNamedTempFile:
    def __init__(self, mode='w+b'):
        self.file = tempfile.NamedTemporaryFile(mode=mode, delete=False)
        atexit.register(self.on_exit)

    def on_exit(self):
        os.unlink(self.file.name)


# The temporary file created by a gif download is deleted when the program exits.
# The object needs to be global so it does not get eaten by the garbage collector.

downloaded_gif_temp_file = None


# Download a gif to a temporary file and return the full path to it on disk.

def download_gif(parser, path):
    global downloaded_gif_temp_file

    downloaded_gif_temp_file = GCNamedTempFile()

    try:
        req = urllib.request.Request(path, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        parser.error('Failed downloading "{path}", message: "{reason}"'.format(path=path, reason=e.reason))

    downloaded_gif_temp_file.file.write(data.read())
    downloaded_gif_temp_file.file.close()

    return downloaded_gif_temp_file.file.name


def is_valid_input(parser, path):
    if os.path.isfile(path):
        if imghdr.what(path) != 'gif':
            parser.error('"{path}" is not a GIF file.'.format(path=path))
        return path
    elif is_url(path):
        path = download_gif(parser, path)
        if imghdr.what(path) != 'gif':
            parser.error('"{path}" is not a GIF file.'.format(path=path))
        return path
    elif os.path.isdir(path):
        return path
    else:
        parser.error('The path "{path}" is not a file, url or directory.'.format(path=path))


def is_valid_frames_per_second(parser, sleep):
    err_prefix = 'argument -fps/--frames-per-second: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 1000000000:
        parser.error(err_prefix + 'Value cannot be greater than 1000000000.')
    if i_value < 1:
        parser.error(err_prefix + 'Value cannot be less than 1.')
    return i_value


def is_valid_framesleep_seconds(parser, sleep):
    err_prefix = 'argument -fsn/--framesleep-nanoseconds: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 2147483647:
        parser.error(err_prefix + 'Value cannot be greater than 2147483647.')
    if i_value < 0:
        parser.error(err_prefix + 'Value cannot be less than 0.')
    return i_value


def is_valid_framesleep_nanoseconds(parser, sleep):
    err_prefix = 'argument -fsn/--framesleep-nanoseconds: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 999999999:
        parser.error(err_prefix + 'Value cannot be greater than 999999999.')
    if i_value < 0:
        parser.error(err_prefix + 'Value cannot be less than 0.')
    return i_value


arg_parser = argparse.ArgumentParser(
    prog='giftoa',

    description=
    'Compile a GIF into an native executable that plays the GIF in ASCII on the console using libncurses.  '
    'See: https://github.com/Teriks/giftoa',

    epilog=
    'All arguments following the arguments listed above will be '
    'passed as options to jp2a.  ANSI colors are not supported...  '
    'Also note that this program requires: gcc, libncurses-dev, jp2a and ImageMagick.'
)

arg_parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

arg_parser.add_argument('-i', '--input',
                        help='A GIF file, GIF URL, or a directory full of jp2a compatible image frames (jpegs).  '
                             'If you provide a directory the jpeg images are sorted by name in natural order, '
                             'you should include a frame number at the beginning or end of the file name accordingly '
                             'to keep the frames sorted correctly.  Specifying the output file name with --output is '
                             'required when a directory or URL is passed to --input.',

                        dest='input_path', default=None,
                        type=lambda file_or_dir: is_valid_input(arg_parser, file_or_dir))

arg_parser.add_argument('--stdin-frames', dest='stdin_frames', action='store_true',
                        help='Accept input frames from stdin as '
                             'a newline separated list of jpeg file paths.')

arg_parser.add_argument('-o', '--output',

                        help='The name of the output executable.  '
                             'If a GIF file is passed and no output name is supplied, '
                             'the name of the input file without its extension is used.  '
                             'When passing a directory to -i / --input, you must specify an output file name.',
                        dest='out_file')

arg_parser.add_argument('-fps', '--frames-per-second', default=None, dest='frames_per_second',

                        type=lambda sleep: is_valid_frames_per_second(arg_parser, sleep),

                        help='The frames per second to attempt to play the animation at (defaults to 10).  '
                             'The minimum value is 1 and the maximum value is 1000000000, FPS must be a whole number.  '
                             'This cannot be used when either -fss or -fsn is specified.'
                        )

arg_parser.add_argument('-fss', '--framesleep-seconds', default=None, dest='framesleep_seconds',

                        type=lambda sleep: is_valid_framesleep_seconds(arg_parser, sleep),

                        help='The number of seconds to sleep before moving to the next frame of the GIF.  '
                             'This is in addition to the number of nanoseconds specified by "-fsn".  '
                             'The value cannot be greater than 2147483647.'
                        )

arg_parser.add_argument('-fsn', '--framesleep-nanoseconds', default=None, dest='framesleep_nanoseconds',

                        type=lambda sleep: is_valid_framesleep_nanoseconds(arg_parser, sleep),

                        help='The number of nanoseconds to sleep before moving to the next frame of the GIF. '
                             'This is in addition to the number of seconds specified by "-fss."  '
                             'The value cannot be greater than 999999999.'
                        )

arg_parser.add_argument('-cc', '--compiler', type=str, default='cc',
                        help='The command used to invoke the C compiler, default is "cc".')


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def write_clock_gettime_impl(file):
    mac_ver = platform.mac_ver()[0].split('.')

    if mac_ver == ['']:
        file.write(GETTIME_DEFAULT_IMPL)
    elif [int(x) for x in mac_ver[:2]] < [10, 12]:
        # Need to emulate if MacOS < 10.12
        file.write(GETTIME_MACOS_IMPL)


def write_jp2a_cvar_into_file(environment, file, var_name, image_filename, jp2a_args):
    jp2a = ['jp2a', image_filename]
    jp2a.extend(jp2a_args)

    success = True
    first_line = True

    with subprocess.Popen(jp2a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment) as p:
        data = p.communicate()

        data_stdout = data[0].decode().split('\n')
        data_stderr = data[1].decode().split('\n')

        for line in data_stderr:
            if line != '':
                print(line, file=sys.stderr)
                success = False

        if not success:
            return False

        for line in data_stdout:
            if line != '':
                str_content = line.rstrip().replace('\\', '\\\\')
                if first_line:
                    file.write('const char* ' + var_name + '= "\\\n' + str_content + '\\n\\\n')
                    first_line = False
                else:
                    file.write(str_content + '\\n\\\n')

        file.write('";\n\n')

    return success


def get_framedelay_init_macro_define(macro_name, args):
    if args.frames_per_second:
        if args.frames_per_second == 1:
            frame_sleep_seconds = 1
            frame_sleep_nanoseconds = 0
        else:
            frame_sleep_seconds = 0
            frame_sleep_nanoseconds = 1000000000 // args.frames_per_second
    else:
        frame_sleep_seconds = args.framesleep_seconds if \
            args.framesleep_seconds else 0

        # default to 10 fps (0.1 second frame delay) if -fss
        # and -fsn are not specified.
        #
        # if -fss is specified and -fsn is not, -fsn defaults to 0
        # instead of 100000000
        frame_sleep_nanoseconds = args.framesleep_nanoseconds if \
            args.framesleep_nanoseconds else 100000000 if \
            not args.framesleep_seconds else 0

    return '#define {macro_name}(VAR) ' \
           'VAR.tv_nsec = {nanoseconds}; ' \
           'VAR.tv_sec = {seconds};' \
        .format(macro_name=macro_name,
                nanoseconds=frame_sleep_nanoseconds,
                seconds=frame_sleep_seconds)


def yield_paths_from_stdin():
    for path in sys.stdin:
        path = path.rstrip()
        if not os.path.isfile(path):
            arg_parser.error('File "{file}" from stdin does not exist.'.format(file=path))
        if imghdr.what(path) != 'jpeg':
            arg_parser.error('File "{file}" from stdin is not a JPEG.'.format(file=path))
        yield path


def main():
    args = arg_parser.parse_known_args()

    try:
        _ = subprocess.check_output(['which', 'jp2a'])
    except:
        print('Cannot find the jp2a command, please install jp2a.  Info: https://csl.name/jp2a/', file=sys.stderr)
        exit(1)

    try:
        _ = subprocess.check_output(['which', 'convert'])
    except:
        print('Cannot find ImageMagick\'s "convert" command, please install ImageMagick.', file=sys.stderr)
        exit(1)

    jp2a_args = args[1]
    args = args[0]

    try:
        _ = subprocess.check_output(['which', args.compiler])
    except:
        print('Unable to find C compiler "{}", please specify or install one.'.format(args.compiler), file=sys.stderr)
        exit(1)

    if args.frames_per_second and (args.framesleep_seconds or args.framesleep_nanoseconds):
        arg_parser.error('-fss (--framesleep-seconds) and -fsn (--framesleep-nanoseconds) '
                         'cannot be used with -fps (--frames-per-second).')
        # parser.error calls exit(2) immediately

    input_path = args.input_path

    if args.stdin_frames and input_path:
        arg_parser.error('-i/--input and --stdin-frames cannot be used together.')

    if not input_path and not args.stdin_frames:
        arg_parser.error('-i/--input must be specified when not using --stdin-frames.')

    if downloaded_gif_temp_file and not args.out_file:
        arg_parser.error('-o/--output must be specified when -i/--input is a URL.')

    out_file = args.out_file
    compiler = args.compiler

    environment = os.environ.copy()

    if 'TERM' not in environment:
        environment['TERM'] = 'xterm'

    with tempfile.TemporaryDirectory() as temp_dir:

        if args.stdin_frames:
            image_paths = yield_paths_from_stdin()
        elif os.path.isfile(input_path):
            if not out_file:
                out_file = os.path.splitext(os.path.basename(input_path))[0]

            subprocess.call([
                'convert',
                '-background', 'none',
                input_path,
                '-coalesce',
                '-bordercolor', 'none',
                '-frame', '0', os.path.join(temp_dir, '%d.jpg')])

            image_paths = sorted(os.listdir(temp_dir), key=natural_sort_key)
            image_paths = (os.path.join(temp_dir, path) for path in image_paths)
        else:
            if not out_file:
                arg_parser.error('No output file specified, an output file must be specified '
                                 'when passing a directory to -i/--input.')
                # parser.error calls exit(2) immediately

            image_paths = (file for file in os.listdir(input_path) if
                           imghdr.what(os.path.join(input_path, file)) == 'jpeg')

            image_paths = sorted(image_paths, key=natural_sort_key)

            if len(image_paths) == 0:
                arg_parser.error('No jp2a compatible images found in directory "{dir}".'.format(dir=input_path))
                # parser.error calls exit(2) immediately

            image_paths = (os.path.join(input_path, path) for path in image_paths)

        source_file_path = os.path.join(temp_dir, 'program.c')

        with open(source_file_path, 'w') as source_file:

            frame_cvar_names = []

            source_file.write(C_HEADERS)

            for frame, image_path in enumerate(image_paths):

                cvar_name = 'frame_' + str(frame)

                frame_cvar_names.append(cvar_name)

                success = write_jp2a_cvar_into_file(environment=environment,
                                                    file=source_file,
                                                    var_name=cvar_name,
                                                    image_filename=image_path,
                                                    jp2a_args=jp2a_args)

                if not success:
                    return 1

            write_clock_gettime_impl(source_file)
            source_file.write('#define GIFTOA_FRAMES_INIT {' + ','.join(frame_cvar_names) + '}\n')
            source_file.write(get_framedelay_init_macro_define('GIFTOA_FRAMEDELAY_INIT', args))
            source_file.write(C_PROGRAM)

        compiler_output = GCNamedTempFile(mode='w+')

        compiler_rt_code = 0

        compiler_cmd = [compiler, source_file_path, '-o', out_file]

        try:
            # try with librealtime

            print("Compiling with -lrt (librealtime) ...",
                  file=compiler_output.file, flush=True)

            subprocess.check_call(
                compiler_cmd + ['-lcurses', '-lrt'],
                stderr=subprocess.STDOUT,
                stdout=compiler_output.file
            )

        except subprocess.CalledProcessError:
            # try without librealtime

            print("Compiling without -lrt (librealtime) ...",
                  file=compiler_output.file, flush=True)

            compiler_rt_code = subprocess.call(
                compiler_cmd + ['-lcurses'],
                stderr=subprocess.STDOUT,
                stdout=compiler_output.file
            )

        if compiler_rt_code:
            compiler_output.file.seek(0)
            shutil.copyfileobj(compiler_output.file, sys.stderr)
            sys.stderr.flush()
            return compiler_rt_code

        return 0


if __name__ == '__main__':
    sys.exit(main())
