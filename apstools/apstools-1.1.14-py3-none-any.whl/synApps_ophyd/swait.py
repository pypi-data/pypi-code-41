
"""
Ophyd support for the EPICS synApps swait record

EXAMPLES:;

    import apstools.synApps
    calcs = apstools.synApps.UserCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    apstools.synApps.setup_random_number_swait(calc1)

    apstools.synApps.setup_incrementer_swait(calcs.calc2)
    
    calc1.reset()


.. autosummary::
   
    ~SwaitRecord 
    ~UserCalcsDevice
    ~setup_random_number_swait 
    ~setup_gaussian_swait
    ~setup_lorentzian_swait 
    ~setup_incrementer_swait

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor

from .. import utils as APS_utils

__all__ = """
    SwaitRecord 
    UserCalcsDevice
    setup_random_number_swait 
    setup_gaussian_swait
    setup_lorentzian_swait 
    setup_incrementer_swait
	""".split()


class SwaitRecordChannel(Device):
    """channel of a synApps swait record: A-L"""

    value = FC(EpicsSignal, '{self.prefix}.{self._ch_letter}')
    input_pv = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}N')
    input_trigger = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}P')
    hints = {'fields': ['value',]}
    read_attrs = ['value', ]
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.value.put(0)
        self.input_pv.put("")
        self.input_trigger.put("Yes")


def _swait_channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (SwaitRecordChannel, '', {'letter': chan})
    return defn


class SwaitRecord(Device):
    """
    synApps swait record: used as $(P):userCalc$(N)

    .. autosummary::
       
        ~reset

    """
    desc = Cpt(EpicsSignal, '.DESC')
    scan = Cpt(EpicsSignal, '.SCAN')
    calc = Cpt(EpicsSignal, '.CALC')
    val = Cpt(EpicsSignalRO, '.VAL')
    prec = Cpt(EpicsSignal, '.PREC')
    process = Cpt(EpicsSignal, '.PROC')
    oevt = Cpt(EpicsSignal, '.OEVT')
    outn = Cpt(EpicsSignal, '.OUTN')
    odly = Cpt(EpicsSignal, '.ODLY')
    doln = Cpt(EpicsSignal, '.DOLN')
    dold = Cpt(EpicsSignal, '.DOLD')
    dopt = Cpt(EpicsSignal, '.DOPT')
    oopt = Cpt(EpicsSignal, '.OOPT')
    flnk = Cpt(EpicsSignal, '.FLNK')

    hints = {'fields': APS_utils.itemizer("channels.%s","A B C D E F G H I J K L".split())}
    read_attrs = APS_utils.itemizer("channels.%s","A B C D E F G H I J K L".split())
    
    channels = DDC(
        _swait_channels(
            "A B C D E F G H I J K L".split()
        )
    )
    
    def reset(self):
        """set all fields to default values"""
        self.desc.put(self.desc.pvname.split(".")[0])
        self.scan.put("Passive")
        self.calc.put("0")
        self.prec.put("5")
        self.dold.put(0)
        self.doln.put("")
        self.dopt.put("Use VAL")
        self.flnk.put("0")
        self.odly.put(0)
        self.oopt.put("Every Time")
        self.outn.put("")
        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, SwaitRecordChannel):
                channel.reset()
        self.hints = {'fields': ["channels.%s" % c for c in "A B C D E F G H I J K L".split()]}
        self.read_attrs = ["channels.%s" % c for c in "A B C D E F G H I J K L".split()]
        self.read_attrs.append('val')


class UserCalcsDevice(Device):
    """
    synApps XXX IOC setup of userCalcs: $(P):userCalc$(N)

    .. autosummary::
       
        ~reset

    """

    enable = Cpt(EpicsSignal, 'userCalcEnable')
    calc1 = Cpt(SwaitRecord, 'userCalc1')
    calc2 = Cpt(SwaitRecord, 'userCalc2')
    calc3 = Cpt(SwaitRecord, 'userCalc3')
    calc4 = Cpt(SwaitRecord, 'userCalc4')
    calc5 = Cpt(SwaitRecord, 'userCalc5')
    calc6 = Cpt(SwaitRecord, 'userCalc6')
    calc7 = Cpt(SwaitRecord, 'userCalc7')
    calc8 = Cpt(SwaitRecord, 'userCalc8')
    calc9 = Cpt(SwaitRecord, 'userCalc9')
    calc10 = Cpt(SwaitRecord, 'userCalc10')

    def reset(self):
        """set all fields to default values"""
        self.calc1.reset()
        self.calc2.reset()
        self.calc3.reset()
        self.calc4.reset()
        self.calc5.reset()
        self.calc6.reset()
        self.calc7.reset()
        self.calc8.reset()
        self.calc9.reset()
        self.calc10.reset()
        self.read_attrs = ["calc%d" % (c+1) for c in range(10)]


def setup_random_number_swait(swait, **kw):
    """setup swait record to generate random numbers"""
    swait.reset()
    swait.scan.put("Passive")
    swait.calc.put("RNDM")
    swait.scan.put(".1 second")
    swait.desc.put("uniform random numbers")

    swait.hints = {"fields": ['val',]}
    swait.read_attrs = ['val',]


def _setup_peak_swait_(calc, desc, swait, motor, center=0, width=1, scale=1, noise=0.05):
    """internal: setup that is common to both Gaussian and Lorentzian swaits"""
    # consider a noisy background, as well (needs a couple calcs)
    assert(isinstance(motor, EpicsMotor))
    assert(width > 0)
    assert(0.0 <= noise <= 1.0)
    swait.reset()
    swait.scan.put("Passive")
    swait.channels.A.input_pv.put(motor.user_readback.pvname)
    swait.channels.B.value.put(center)
    swait.channels.C.value.put(width)
    swait.channels.D.value.put(scale)
    swait.channels.E.value.put(noise)
    swait.calc.put(calc)
    swait.scan.put("I/O Intr")
    swait.desc.put(desc)

    swait.hints = {"fields": ['val',]}
    swait.read_attrs = ['val',]


def setup_gaussian_swait(swait, motor, center=0, width=1, scale=1, noise=0.05):
    """setup swait for noisy Gaussian"""
    _setup_peak_swait_(
        "D*(0.95+E*RNDM)/exp(((A-b)/c)^2)",
        "noisy Gaussian curve", 
        swait, 
        motor, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def setup_lorentzian_swait(swait, motor, center=0, width=1, scale=1, noise=0.05):
    """setup swait record for noisy Lorentzian"""
    _setup_peak_swait_(
        "D*(0.95+E*RNDM)/(1+((A-b)/c)^2)", 
        "noisy Lorentzian curve", 
        swait, 
        motor, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def setup_incrementer_swait(swait, scan=None, limit=100000):
    """setup swait record as an incrementer"""
    # consider a noisy background, as well (needs a couple calcs)
    scan = scan or ".1 second"
    swait.reset()
    swait.scan.put("Passive")
    pvname = swait.val.pvname.split(".")[0]
    swait.channels.A.input_pv.put(pvname)
    swait.channels.B.value.put(limit)
    swait.calc.put("(A+1) % B")
    swait.scan.put(scan)
    swait.desc.put("incrementer")

    swait.hints = {"fields": ['val',]}
    swait.read_attrs = ['val',]
