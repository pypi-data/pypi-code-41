from __future__ import print_function

import os
import sys
import functools

from twisted.python import usage, log
from twisted.internet import defer, reactor
from zope.interface import implementer
import txtorcon
import humanize

from carml import util


names = {
    # onion.debian.org
    '10years.debconf.org': 'b5tearqs4v4nvbup.onion',
    'appstream.debian.org': '5j7saze5byfqccf3.onion',
    'apt.buildd.debian.org': 'ito4xpoj3re4wctm.onion',
    'backports.debian.org': '6f6ejaiiixypfqaf.onion',
    'bits.debian.org': '4ypuji3wwrg5zoxm.onion',
    'blends.debian.org': 'bcwpy5wca456u7tz.onion',
    'bootstrap.debian.net': 'ihdhoeoovbtgutfm.onion',
    'cdimage-search.debian.org': '4zhlmuhqvjkvspwb.onion',
    'd-i.debian.org': 'f6syxyjdgzbeacry.onion',
    'debaday.debian.net': 'ammd7ytxcpeavif2.onion',
    'debconf0.debconf.org': 'ynr7muu3263jikep.onion',
    'debconf1.debconf.org': '4do6yq4iwstidagh.onion',
    'debconf16.debconf.org': '6nhxqcogfcwqzgnm.onion',
    'debconf2.debconf.org': 'ugw3zjsayleoamaz.onion',
    'debconf3.debconf.org': 'zdfsyv3rubuhpql3.onion',
    'debconf4.debconf.org': 'eeblrw5eh2is36az.onion',
    'debconf5.debconf.org': '3m2tlhjsoxws2akz.onion',
    'debconf6.debconf.org': 'gmi5gld3uk5ozvrv.onion',
    'debconf7.debconf.org': '465rf3c2oskkqc24.onion',
    'debdeltas.debian.net': 'vral2uljb3ndhhxr.onion',
    'debug.mirrors.debian.org': 'ktqxbqrhg5ai2c7f.onion',
    'dpl.debian.org': 'j73wbfpplklpixbh.onion',
    'dsa.debian.org': 'f7bphdxlqca3sevt.onion',
    'es.debconf.org': 'nwvk3svshonwqfjs.onion',
    'fr.debconf.org': 'ythg247lqkx2gpgx.onion',
    'ftp.debian.org': 'vwakviie2ienjx6t.onion',
    'ftp.ports.debian.org': 'nbybwh4atabu6xq3.onion',
    'incoming.debian.org': 'oscbw3h7wrfxqi4m.onion',
    'incoming.ports.debian.org': 'vyrxto4jsgoxvilf.onion',
    'lintian.debian.org': 'ohusanrieoxsxlmh.onion',
    'manpages.debian.org': 'pugljpwjhbiagkrn.onion',
    'metadata.ftp-master.debian.org': 'cmgvqnxjoiqthvrc.onion',
    'micronews.debian.org': 'n7jzk5wpel4tdog2.onion',
    'miniconf10.debconf.org': 'tpez4zz5a4civ6ew.onion',
    'mirror-master.debian.org': 'kyk55bof3hzdiwrm.onion',
    'mozilla.debian.net': 'fkbjngvraoici6k7.onion',
    'news.debian.net': 'tz4732fxpkehod36.onion',
    'onion.debian.org': '5nca3wxl33tzlzj5.onion',
    'people.debian.org': 'hd37oiauf5uoz7gg.onion',
    'planet.debian.org': 'gnvweaoe2xzjqldu.onion',
    'release.debian.org': '6nvqpgx7bih375fx.onion',
    'rtc.debian.org': 'ex4gh7cig5ssn2xm.onion',
    'security-team.debian.org': 'ynvs3km32u33agwq.onion',
    'security.debian.org': 'sgvtcaew4bxjd7ln.onion',
    'timeline.debian.net': 'qqvyib4j3fz66nuc.onion',
    'tracker.debian.org': '2qlvvvnhqyda2ahd.onion',
    'wnpp-by-tags.debian.net': 'gl3n4wtekbfaubye.onion',
    'www.debian.org': 'sejnfjrq6szgca7v.onion',
    'www.ports.debian.org': 'lljrzrimek6if67j.onion',

    # onion.torproject.org
    'archive.torproject.org': 'yjuwkcxlgo7f7o6s.onion',
    'atlas.testnet.torproject.org': '2d5quh2deowe4kpd.onion',
    'atlas.torproject.org': '52g5y5karruvc7bz.onion',
    'aus1.torproject.org': 'x3nelbld33llasqv.onion',
    'aus2.torproject.org': 'vijs2fmpd72nbqok.onion',
    'bridges.torproject.org': 'z5tfsnikzulwicxs.onion',
    'cloud.torproject.org': 'icxe4yp32mq6gm6n.onion',
    'collector.testnet.torproject.org': 'vhbbidwvzwhahsrg.onion',
    'collector.torproject.org': 'qigcb4g4xxbh5ho6.onion',
    'collector2.torproject.org': 'kkvj4mhsttfcrksj.onion',
    'compass.torproject.org': 'lwygejoa6fm26eef.onion',
    'consensus-health.torproject.org': 'tgnv2pssfumdedyw.onion',
    'crm.torproject.org': 'sgs4q3dzv74f723x.onion',
    'deb.torproject.org': 'sdscoq7snqtznauu.onion',
    'dist.torproject.org': 'rqef5a5mebgq46y5.onion',
    'donate.torproject.org': 'bjk3o77eebkax2ud.onion',
    'exonerator.torproject.org': 'zfu7x4fuagirknhb.onion',
    'extra.torproject.org': 'klbl4glo2btuwyok.onion',
    'gettor.torproject.org': 'tngjm3owsslo3wgo.onion',
    'git.torproject.org': 'dccbbv6cooddgcrq.onion',
    'gitweb.torproject.org': 'jqs44zhtxl2uo6gk.onion',
    'health.testnet.torproject.org': 'fr6scuhdp5dqvy7d.onion',
    'help.torproject.org': '54nujbl4qohb5qdp.onion',
    'jenkins.torproject.org': 'f7lqb5oicvsahone.onion',
    'media.torproject.org': 'n46o4uxsej2icp5l.onion',
    'metrics.torproject.org': 'rougmnvswfsmd4dq.onion',
    'munin.torproject.org': 'hhr6fex2giwmolct.onion',
    'nagios.torproject.org': 'kakxayzmcc3zeomu.onion',
    'nyx.torproject.org': 'ebxqgaz3dwywcoxl.onion',
    'onion.torproject.org': 'yz7lpwfhhzcdyc5y.onion',
    'onionoo.torproject.org': 'tgel7v4rpcllsrk2.onion',
    'onionperf.torproject.org': 'llhb3u5h3q66ha62.onion',
    'ooni.torproject.org': 'fqnqc7zix2wblwex.onion',
    'people.torproject.org': 'sbe5fi5cka5l3fqe.onion',
    'research.torproject.org': 'wcgqzqyfi7a6iu62.onion',
    'spec.torproject.org': 's2bweojt5vg52e5i.onion',
    'staging.crm.torproject.org': 'swnwd5bhvjk4dd5o.onion',
    'staging.donate.torproject.org': 'cvtwbn7mgxki7gvc.onion',
    'stem.torproject.org': 'vt5hknv6sblkgf22.onion',
    'tb-manual.torproject.org': 'dgvdmophvhunawds.onion',
    'test-data.tbb.torproject.org': 'fylvgu5r6gcdadeo.onion',
    'test.crm.torproject.org': 'abp7hndzgazze2wy.onion',
    'test.donate.torproject.org': 'p73stlm5nhogxw4w.onion',
    'testnet.torproject.org': 'bo7uextohjpuqvrh.onion',
    'trac.torproject.org': 'ea5faa5po25cf7fb.onion',
    'webstats.torproject.org': 'gbinixxw7gnsh5jr.onion',
    'www-staging.torproject.org': 'krkzagd5yo4bvypt.onion',
    'www.onion-router.net': 'hzmun3rnnxjhkyhg.onion',
    'www.torproject.org': 'expyuzz4wqqyqhjn.onion',
}

@implementer(txtorcon.IStreamAttacher)
class Attacher(object):

    def __init__(self, tor):
        self._tor = tor

    async def attach_stream(self, stream, circuits):
        try:
            remap = names[stream.target_host]
        except KeyError:
            remap = none

        if remap is not None and remap != stream.target_host:
            print("  {} becomes {}".format(stream.target_host, remap))
            cmd = 'REDIRECTSTREAM {} {}'.format(stream.id, remap)
            await self._tor.protocol.queue_command(cmd)
        return None  # ask Tor to attach the stream, always


async def run(reactor, cfg, tor):
    state = await tor.create_state()
    state.set_attacher(Attacher(tor), reactor)
    await defer.Deferred()
