import os
import requests
import select
import subprocess
import sys
import time
from imp import reload
from invoke import run, task, Program, Collection
from random import randint


@task
def ulous(ctx, run_for=10, second_per_frame=0.15):
    run_for = int(run_for)
    second_per_frame = float(second_per_frame)

    frames = [
        '\n\n        ⊂_ヽ\n          ＼＼ Λ＿ Λ\n            ＼(ಠ_ಠ )\n              >   ⌒ヽ\n       '
        '      /    へ＼''\n            /   /   ＼＼\n            ﾚ  ノ     ヽ_つ\n            / /\n '
        '          / /|\n          ( ( ヽ\n          | | 、＼\n          | 丿 ＼ ⌒)\n          ||    '
        ') /\n         ノ )   Lﾉ\n        (_／\n        ',
        '\n         ,⌒\n         |ヽ\n         ＼＼Λ ＿Λ\n          ＼( ಠ_ಠ)\n            >  ヽ\n    '
        '        /  へ＼\n           (   | ＼＼\n           ﾚ  ノ (_`/\n           ,/ /\n          //'
        ' /\n        ( ( |\n         、| |、\n          | 丿`⌒)\n          || ) /\n         ノ )Lﾉ\n'
        '        (_／\n        ',
        '\n\n\n            Λ ＿Λ\n            ( ಠ_ಠ)\n  _.._______,   ヽ._______.._\n `==.-------\  '
        '  /-------.==`\n            |   |\n            | . |\n            \   /\n            |  |'
        '\n           (    )\n          / | | ＼\n         ( |  | 丿\n          ||  ||\n        _/ )'
        '  ( \_\n       (_,/    \,_)\n    ',
        '\n\n                     .`,,\n            Λ ＿Λ    //`\n            ( ಠ_ಠ) //\n          '
        '  ,   ヽ./\n           / /  |/\n          //|   |\n        //  |   |\n      ⊂_ヽ  (    ＼\n'
        '            | ＼  ＼\n           (  / ＼ ＼\n           / |    /  )\n          | )    / /\n'
        '          ||    ( \_\n          ( \_   \,_)\n           \,_)\n        ',
        '\n\n\n             Λ＿ Λ\n            (    )\n  _.._______,   ヽ._______.._\n `==.-------\ '
        '   /-------.==`\n            |   |\n            |   |\n            \   /\n            |   '
        '|\n            ( Y )\n           / | | ＼\n          ( |  | 丿\n           ||  ||\n        '
        ' _/ )  ( \_\n        (_,/    \,_)\n    ',
    ]

    def print_frame(frame, padding=20, second_per_frame=second_per_frame):
        time.sleep(second_per_frame)
        os.system('clear')
        print(' ' * padding + frame.replace('\n', '\n' + ' ' * padding))

    os.system('clear')
    for x in range(0, int(run_for * (1 / second_per_frame) / len(frames))):
        for y in range(0, len(frames)):
            print_frame(frames[y], padding=((x * 5) + y), second_per_frame=second_per_frame)


def sonos_connect():
    import soco
    SONOS_ID = 'UptickHQ'

    found_ip = False
    for i in range(0, 10):
        sonoses = list(soco.discover())
        for sonos in sonoses:
            if sonos.player_name == SONOS_ID:
                found_ip = sonos.ip_address
                break
        if found_ip:
            break
        time.sleep(1)
    else:
        print('Unable to find sonos!')
        return None
    return soco.SoCo(found_ip)


@task
def sonos_play(ctx, uri, volume=30):
    sonos = sonos_connect()
    sonos.volume = int(volume)
    # if it is a full uri, use it
    if uri.startswith('http'):
        sonos.play_uri(uri)
    else:
        sonos.play_uri(f'x-sonos-spotify:spotify%3atrack%3a{uri}?sid=12&flags=8224&sn=3')


@task
def chris(ctx, keyword=None, volume=30):
    if not keyword:
        print('Please pass a keyword')
        sys.exit()

    sound_engine = 'http://www.myinstants.com'

    print('Searching ...')
    search_query = '{}/search/?name={}'.format(sound_engine, keyword)
    search_result = requests.get(search_query).content.decode('utf-8')
    results = []
    while 'onmousedown="play(' in search_result:
        download_url, search_result = search_result.split('onmousedown="play(', 1)[1].split(')', 1)
        results.append(sound_engine + download_url.strip("'"))

    print('Found {} results. Randomising ...'.format(len(results)))
    index = randint(0, len(results) - 1)
    download_url = results[index]

    print('Playing {}/{} {}'.format(index, len(results), download_url))
    sonos_play(ctx, download_url, volume)


@task
def standup(ctx):
    sonos_play(ctx, '1nw8lTaFu9kphHRNy67lXa')


@task
def teatime(ctx):
    sonos_play(ctx, '6p4eSqQXm38l6piroTh20d')


@task
def amazing(ctx):
    sonos_play(ctx, '1s16lVXTAFSS4Nm3Ygd1Qu')


@task
def volume(ctx, value=None):
    sonos = sonos_connect()
    if value is None:
        print(sonos.volume)
    else:
        sonos.volume = int(value)


@task
def quiet(ctx):
    volume(ctx, value=10)


@task
def shutup(ctx):
    volume(ctx, value=0)


@task
def shut_the_forever_up(ctx):
    while True:
        time.sleep(0.1)
        try:
            shutup(ctx)
        except Exception:
            time.sleep(1)


@task
def karaoke(ctx):
    import time
    import sys

    from PyLyrics.functions import PyLyrics

    if sys.version_info < (3, 0):
        # ensure that encoding is utf-8
        reload(sys)
        sys.setdefaultencoding("utf-8")

    sonos = sonos_connect()

    stop = False
    while True:

        track = sonos.get_current_track_info()
        time.sleep(1)

        if not track['title']:
            print('Nothing playing')
            continue

        try:
            lyrics = PyLyrics.getLyrics(track['artist'], track['title']).split('\n')
        except Exception:
            lyrics = ['No lyrics found on lyrics.wikia.com', ]

            try:
                albums = PyLyrics.getAlbums(singer=track['artist'])
                for album in albums:
                    lyrics.append('[{} ({})]'.format(album.name, album.year))
                    tracks = PyLyrics.getTracks(album)
                    for song in tracks:
                        lyrics.append('    - {}'.format(song.name))
            except Exception:
                pass

        # estimate position
        duration = track['duration'].split(':')
        duration = float(duration[0]) * 60 * 60 + float(duration[1]) * 60 + float(duration[2])
        position = track['position'].split(':')
        position = float(position[0]) * 60 * 60 + float(position[1]) * 60 + float(position[2])

        percent = position / duration
        location = int(round(percent * len(lyrics), 0))

        def print_timer(seconds):
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return "%d:%02d:%02d" % (h, m, s)

        # find speed
        while location < len(lyrics):
            os.system('clear')
            separator = '-' * 60
            combine_lyrics = [
                ('> ' if i == location else '  ') +
                row for i, row in enumerate(lyrics)
            ]
            print(
                '\n'.join([
                    ' {artist}',
                    '{separator}',
                    ' {title}',
                    '{separator}',
                ] + combine_lyrics + [
                    '{separator}',
                    ' {current_timer} / {duration}',
                    '{separator}',
                    'Press ENTER to exit',
                ]).format(
                    separator=separator,
                    current_timer=print_timer(position),
                    **track
                )
            )
            # refresh display in a second
            time.sleep(1)
            position += 1

            # recalculate location
            percent = position / duration
            location = int(round(percent * len(lyrics), 0))

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    raw_input()
                except NameError:
                    input()
                stop = True
                break
        if stop:
            break


@task
def doom(ctx, install_vnc=True):
    """ pw:1234 Runs Doom with mosters representing docker containers
    Download a VNC Viewer and connect on localhost:5900 pw: 1234
    @exa
        inv fun.doom
        inv fun.doom install_vnc=False
    """
    # download VNC Viewer if user doesn't have it
    if not(os.path.exists("var/fun/")):
        run('mkdir var/fun/')
    if (sys.platform == 'linux2'):
        if not(os.path.exists("var/fun/VNC-Viewer-6.0.1-Linux-x64")) and install_vnc:
            print("You don't have VNC, installing VNC Viewer for Linux...")
            URL = 'https://www.realvnc.com/download/file/viewer.files/VNC-Viewer-6.0.1-Linux-x64.gz'
            run('curl -o var/fun/VNC-Viewer-6.0.1-Linux-x64.gz ' + URL)
            run('gzip -vd var/fun/VNC-Viewer-6.0.1-Linux-x64.gz')
            run('chmod +x var/fun/VNC-Viewer-6.0.1-Linux-x64')

    if not (os.path.exists("var/fun/dockerdoomd")):
        if not (os.path.exists("var/fun/dockerdoomd.tar.gz")):
            print("You don't have DockerDoom... installing DockerDoom")
            # then the exec and the tar don't exist so download the tar
            URL = 'https://gideonred.com/bins/dockerdoomd.tar.gz'
            run('curl -o var/fun/dockerdoomd.tar.gz ' + URL)
        # the tar exists so extract it
        run('tar -xvzf var/fun/dockerdoomd.tar.gz -C var/fun/')

    build_containers = 'for i in {1..2} ; do docker run -d -t ubuntu:14.04; done'
    run(build_containers)
    perms = 'chmod +x var/fun/dockerdoomd'  # make it executable
    run(perms)

    run('parallel --ungroup ::: "sleep 6; ./var/fun/VNC-Viewer-6.0.1-Linux-x64 localhost:5900" "./var/fun/dockerdoomd"')


@task
def doge(ctx, big_doge=False):
    """ Your favourite shiba inu.
    @examples
        inv fun.doge
        inv fun.doge --big-doge
    """

    doge = """
        :::::::::::::::::::::::::::::/::::::::::::::::::::
        ::::::::::/os+:::::::::::::+sdo:::::::::::::::::::
        ::::::::::s+syho::::::::::ossds:::::::::::::::::::
        :::::::::+o++ossyo+++++oshysyho:::::::::::::::::::
        :::::::::+o+:-+o+ssyhhhhyyhhddho/:::::::::::::::::
        ::::::::::ss+.-ooyhhhhhyyyyhmmddddy+::::::::::::::
        :::::::::+y+oooyhhhyyhdddhsyddyshmmdo:::::::::::::
        ::::::::/hs+shhhhhhyy+oshhhhdd/.omNNm/::::::::::::
        ::::::::+hsshhhddddh+..+-shdmddhhdNMNs::::::::::::
        ::::::::+hyhddmmmmmmdhyyhhdmmdyssshNNm/:::::::::::
        :::::::/hhhhddmmmmmmmmmmmddmmy.```-NNNs:::::::::::
        :::::::hhhyyhddddmmmmmmmmddddy/```:hNNy:::::::::::
        ::::::odhyyyhdddddddddddhssyyo:.`./dNNs:::::::::::
        ::::::yhyssyyhddddddddhdhs+++//::ohmNm/:::::::::::
        ::::::hyysssyyhhddddddhhhhhhhhhhddmmNy::::::::::::
        :::::+dhyysssyyhhddddddhhhhhhddddmmmmd::::::::::::
        :::::odddhhyyyhhdhdhhhhhhhhhhhdddddmmm/:::::::::::
        :::::+ddddddddddddddddhhyyyyyyhhddmmNNo:::::::::::
        :::::/hddmmmmmmdddddddddhhhyyhhddmmmNNs:::::::::::
        :::::/yhdmmmmmmddmddddddddhhhhhddmmmmmy:::::::::::
        ::::::yyhddmmmmmmmdddddddhhhhhhddddmmNm/::::::::::
        ::::::ssyhdddmmmmdddddddddddhhhhhddmmNNh::::::::::
        ::::::ysyddmmdddddddddddddhhhhhhhddmmNNms:::::::::
        ::::::ssydmmdddddhhhdhhhhhhhhhhhdddddddmm+::::::::
        ::::::+sydmmddddhhdhhhhhhhhhhhhhhhhhdddmmd::::::::
        :::::::yyhddddhhhhhhhhhdhhhhhhhdddddmmmmmmo:::::::
        :::::::syhhhhhhhhhyhdddmmmmmddddhddmmmmmmms:::::::
        :::::::+yhhhhhddhhhhdddmmNNNNNNmddmmmmmmNmo:::::::
        ::::::::yhhyyhdhhhyyhhddhydmmmNmmdmmmmdhy+::::::::
        ::::::::/syhhhhhyhhsydho/ys++yyddhso+/::::::::::::
        :::::::::/+syyysssosmdhh+///oys+::::::::::::::::::
        :::::::::::::::::::+s++:::::/:::::::::::::::::::::
        ::::::::::::::::::::::::::::::::::::::::::::::::::
    """

    if big_doge:
        doge = """
            ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            :::::::::::::::::::::::::::::::::::::::::::::/oo/:::::::::::::::::::::::::::::::
            :::::::::::::::::+syso/:::::::::::::::::::::sshdy:::::::::::::::::::::::::::::::
            ::::::::::::::::+s+ssyds::::::::::::::::::/ysshdh:::::::::::::::::::::::::::::::
            :::::::::::::::/y++osyyhho/::::::::::::::oyssshdh:::::::::::::::::::::::::::::::
            :::::::::::::::oo++ooossshho+/://///++oshhysssyhy:::::::::::::::::::::::::::::::
            :::::::::::::::ooo+///+oo+syhyhyyyhhhhhhhhhhhhyyh/::::::::::::::::::::::::::::::
            :::::::::::::::oooo:..:+so/+osyyhhhhhyyyyyhhdddddhyo/:::::::::::::::::::::::::::
            :::::::::::::::/yos+-../oo+oyyhhhhyhhyyyysyhdmmmddddhhs+::::::::::::::::::::::::
            ::::::::::::::::yoos+:../syhhhhyyyhhhhhhyysydmmmmddmmmmmh+::::::::::::::::::::::
            :::::::::::::::ohsoosoosyhhhhhhyyyhdddddhysyydddhysydmmmmdo:::::::::::::::::::::
            ::::::::::::::ody++osyhddhhhhyyyyhhhhhdddhyyhhhd/--/ymNNNmd/::::::::::::::::::::
            ::::::::::::::hhs++syhhhhhhhhhyys/--/+oyyhhddddds--:ymNMMNms::::::::::::::::::::
            ::::::::::::::dhyssyhhhhhhhdhhhy/.``.s--+shdmmmdddhyhdmNMMNd/:::::::::::::::::::
            ::::::::::::::hyyyyhhddddddmmmdddy+//++oyyddmmmmmmdmmmNNNNNNo:::::::::::::::::::
            :::::::::::::/hhhhhddmmmmddmmmmmdhhhhhddhdddmmmdyo+++osdNNNNd/::::::::::::::::::
            ::::::::::::/hhhhhdddmmmmmmmmmmmddmmmmmmdddmmmmo.``````:NNNNmo::::::::::::::::::
            :::::::::::/hdhhyyhdddddmmmmmmmmmmmmmmmmmddmmmdo.`  ```:dNNNNy::::::::::::::::::
            :::::::::::sdhhhyyyhhdddddddmmmmmmmmmmmmddddddhy+-````./ymmNNh::::::::::::::::::
            ::::::::::/dhhyyyyyyhdddddddddddddddddddhhhhhhys+-....-/ymNNNh::::::::::::::::::
            ::::::::::sdhhyyyyyyhdddmmmdddddddhdddhs+oosyys+-`````-ommNNNs::::::::::::::::::
            ::::::::::dhhyyysyyyyhdddddddddddddhhddhs+::::.-----:+ydmNNNd:::::::::::::::::::
            :::::::::/dhyyssssyyyyhhdddddddddddhhhddhhyyyysyysssyddmmNNN+:::::::::::::::::::
            :::::::::ohyyyssossyyyyhhhdddmmdddddhhhhhhhhhhhdddddmmmmmmNN+:::::::::::::::::::
            :::::::::hhhyyyssooosyyyhhhddddddddddhhhhhhhhhhddddddmmmmmmNo:::::::::::::::::::
            :::::::::dddhhhhyssssyyhhhhddhhddddddhhhhhhhhhhhdddddddddmmNy:::::::::::::::::::
            :::::::::mdddddhhhyyyyyhhhdhhddhhhyhhhhhhhhhhhddddddddddmmmmm:::::::::::::::::::
            :::::::::mddddddddddhhhhhhdhdddhdhhyyyyyyyyyyhhyyhhddddmmmmNN+::::::::::::::::::
            :::::::::hdddddmmmmmmmddddddddddhddddhhyyyyyyyyyyhddddmmmNNNNs::::::::::::::::::
            :::::::::shddmmmmmmmmmmmmdddhdddddddddhhhhhyyyhhhhhddmmmmNNNmy::::::::::::::::::
            :::::::::shhdddmmmmmmmmmdddddddddddddddddhhhhhhhhddddmmmmNNmmh::::::::::::::::::
            :::::::::oyhhddmmmmmmmmmdddmmddddddddhdddhhyhhhyhddddmmmmmmmmh::::::::::::::::::
            :::::::::+syyhdddmmmmmmmmmmmddddddddddddhdhhhhhhhddddddmmmNNNm+:::::::::::::::::
            :::::::::+syyyhhhddmmmmmmmmmmdhdddddddddddddhhhhhddddddmmmNNNNd:::::::::::::::::
            :::::::::+sssyyhdddddmmmmmmdddddddddddddddhdddhhhhhhdddmmmNNNNNs::::::::::::::::
            :::::::::+sssyhdddddddddddddddmdddddddddddddhhhhhhhhhdddmmmNNNNm+:::::::::::::::
            :::::::::+ssyyddmmmmmddddddddddddddddddddhhhhhhhhhhhdddddmmmNNmmd/::::::::::::::
            :::::::::/yssyhdmmmmdddddddddhhhddddhhhhhhhhhhhhhhhdddddddmmmmmmmh/:::::::::::::
            ::::::::::sssyhdmmmddddddddhhddhhhhhhhhhhhhhhhhhhhhhhddhdddhddddmmy:::::::::::::
            ::::::::::+ssyhdmmmmddddddhhddhhhhhhhhhhhhhhhhhhhhhhhhyyhhhdddmmdmm+::::::::::::
            :::::::::::sssyddmdddddhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhddddmmmmmmmmmy::::::::::::
            :::::::::::ossyhddddhhhhhhhhhhhhhhhddddddhhhhhhhdddddddddmmmmmmmmmmd/:::::::::::
            :::::::::::oyyyhhhhhhhhhhyyhhyyhhddddmmmmmmmddhhdddhhdddmmmmmmmmmmmd/:::::::::::
            :::::::::::/yyhhhhhhhhhdhhhhhyhhhddddmNNNNNNNNNmmddddddmmmmmmmmmmmmm/:::::::::::
            ::::::::::::syhhhhhhhhdddhhhyhhhdddddmmmmmNNNNNNNNmmddmmmmmmmmmNNNms::::::::::::
            ::::::::::::+yyhhhhyhhhddhhhyyhhddddddmdydmmNNmNNNmmmmmmmmmmmmmmdh+:::::::::::::
            :::::::::::::syyyyyyhhhddhhhhhyyyyyhdhsosyhdhsdddmmmmdhdmmdhyo+//:::::::::::::::
            ::::::::::::::+yyhhhhdhhhhyyhhyssdddyo-/yyo/:/syyydddhoo+/::::::::::::::::::::::
            :::::::::::::::+syyhhhhhyyyyssosdNmddy+:++/:/+oyyhs+/:::::::::::::::::::::::::::
            :::::::::::::::::/+++ooooo++++oyddhdshy+:-+:/syo+/::::::::::::::::::::::::::::::
            :::::::::::::::::::::::::::::::sy+oo/.---::::/::::::::::::::::::::::::::::::::::
            ::::::::::::::::::::::::::::::::/:::////::::::::::::::::::::::::::::::::::::::::
            ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        """

    print(doge)


@task
def rick(ctx):
    """ Get rick rolled
    @examples
        inv fun.rick
    """
    script = "curl -s -L http://bit.ly/10hA8iC | bash"
    print("Downloading ~5MB Please Wait")
    subprocess.call(script, shell=True)

program = Program(namespace=Collection.from_module('fun'), version='1.0.0')
