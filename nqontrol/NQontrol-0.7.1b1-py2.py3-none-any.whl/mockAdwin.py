from time import time
from nqontrol import settings
import logging as log
import numpy as np
from scipy import signal
from nqontrol.servo import _convertStepsize2Frequency, _convertVolt2Int
from nqontrol import general


class MockADwin():
    def __init__(self, DeviceNo=0):
        self.DeviceNo = DeviceNo
        self._par = [0] * 80
        self._fpar = [0] * 80
        self._running = [0] * 10
        self._data_double = [[]] * 200
        self._data_long = [[]] * 200
        self.ADwindir = 'mock'
        self._boot_time = time()
        self._last_read = 0
        self._n_last = 0

        self._data_long[4 - 1] = [0] * 8
        self._data_long[6 - 1] = [0] * 8
        self._data_long[7 - 1] = [0] * 8
        self._data_long[settings.DATA_LOCK - 1] = [0] * (8 * 5)
        self.Set_Par(7, 3000)

    def Boot(self, file):
        self._boot_time = time()

    def Workload(self):
        return 42

    def Process_Status(self, no):
        return self._running[no - 1]

    def Load_Process(self, process):
        pass

    def Start_Process(self, no):
        self._running[no - 1] = 1

    def Set_FPar(self, index, par):
        self._fpar[index - 1] = float(par)

    def Set_Par(self, index, par):
        if index == 3 and par != 0:
            self._last_read = time()
        self._par[index - 1] = int(par)

    def Get_Par(self, index):
        self._par_special_functions()
        return self._par[index - 1]

    def Get_FPar(self, index):
        self._fpar_special_functions()
        return self._fpar[index - 1]

    def GetData_Double(self, DataNo, Startindex, Count):
        return self._data_double[DataNo - 1][Startindex - 1:Startindex + Count - 1]

    def SetData_Double(self, Data, DataNo, Startindex, Count):
        self._data_double[DataNo - 1][Startindex - 1:Startindex + Count - 1] = Data

    def GetData_Long(self, DataNo, Startindex, Count):
        self._data_long_special_functions(DataNo)
        return self._data_long[DataNo - 1][Startindex - 1:Startindex - 1 + Count]

    def _data_long_special_functions(self, no):
        if no == 4:
            for i in range(1, 9):
                if self._isRamp():
                    out = np.random.randint(0, 2**16)
                else:
                    out = 2**15
                self.SetData_Long([out], 4, i, 1)

    def SetData_Long(self, Data, DataNo, Startindex, Count):
        self._data_long[DataNo - 1][Startindex - 1:Startindex + Count - 1] = Data

    def Fifo_Full(self, index):
        diff = time() - self._last_read
        fifoStepsize = self.Get_Par(6)
        n = int(diff * settings.SAMPLING_RATE / fifoStepsize)
        n = n + self._n_last
        if n > settings.FIFO_BUFFER_SIZE:
            n = settings.FIFO_BUFFER_SIZE
        self._n_last = n
        return int(n)

    def _rampChannel(self):
        return self.Get_Par(4)

    def _isRamp(self):
        channel = self._rampChannel()
        if channel == 0:
            return False
        control = self.Get_Par(3)
        if control & 15 == channel:
            return True
        else:
            return False

    def _readSwitches(self, channel):
        c = self.Get_Par(10 + channel)
        # read control bits
        auxSw = general.readBit(c, 9)
        snapSw = general.readBit(c, 3)
        offsetSw = general.readBit(c, 2)
        outputSw = general.readBit(c, 1)
        inputSw = general.readBit(c, 0)
        return inputSw, offsetSw, auxSw, outputSw, snapSw

    def _constructOutput(self, amount, input, aux):
        channel = self.Get_Par(4)
        inputSw, offsetSw, auxSw, outputSw, snapSw = self._readSwitches(channel)

        # lock simulation
        data = self._data_long[7]
        lockoffset = data[(channel - 1) * 5 + 4]
        if data[(channel - 1) * 5] == 1:
            output = np.full(amount, lockoffset).astype(int)
        else:
            output = np.full(amount, 0x8000).astype(int)
        if not outputSw:
            return output
        if inputSw:
            output = input
        if offsetSw:
            offset = self.GetData_Double(2, channel + 8, 1)
            output = output + offset
        gain = self.GetData_Double(2, channel, 1)
        output = (output - 0x8000) * gain + 0x8000
        if snapSw:
            output = np.full(amount, 0x8000).astype(int)
        if auxSw:
            output = output + (aux - 0x8000)

        # Limit the output to 16bit
        output[output > 0xffff] = 0xffff
        output[output < 0] = 0

        return output

    def GetFifo_Double(self, index, amount):
        assert (index == 3), 'Index has to be 3.'

        amount = int(amount)
        # is ramp enabled
        isRamp = self._isRamp()
        # Creating random data
        input = np.random.normal(0x8000, 10, size=amount).astype(int)
        aux = np.random.normal(0x8000, 10, size=amount).astype(int)

        # if ramp has been set the output will just be the ramp signal
        if not isRamp:
            output = self._constructOutput(amount, input, aux)
        else:
            # construct the ramp signal
            rampPar = self.Get_Par(3)

            def extract_value(par, offset=0):
                shifted = np.right_shift(par, offset)
                return np.bitwise_and(shifted, 0xff)
            # first extracting the stepsize, then converting to frequency
            frequency = _convertStepsize2Frequency(extract_value(rampPar, 8))
            amplitude = self.Get_FPar(1) * 10
            lin = np.linspace(0, 1, amount)
            output = amplitude * signal.sawtooth(2 * np.pi * frequency * lin, 0.5)
            output = _convertVolt2Int(output) + 0x8000
        # concatenating bits
        crunch = np.left_shift(input, 32)
        crunch = np.add(crunch, np.left_shift(aux, 16))
        crunch = np.add(crunch, output)
        # setting last readout time to current
        self._last_read = time()
        self._n_last = self._n_last - amount
        return crunch

    def Get_Processdelay(self, index):
        return 1e9 / settings.SAMPLING_RATE

    def _par_special_functions(self):
        self._par[0] = time() - self._boot_time  # Timestamp
        self._par[1] = 0  # Resetting trigger

        # snapping emulation
        aux = 0x8000
        for servo in range(1, 9):
            control = self._par[9 + servo]
            snap_enabled = control & 8

            if snap_enabled:
                snap_config = self.GetData_Long(7, servo, 1)[0]
                snap_value = aux - (snap_config & 0xffff)
                if (snap_config & 0x10000) > 0:
                    snap_value *= -1
                if snap_value <= 0:
                    control = general.clearBit(control, 3)  # disable snapSw
                    control = general.setBit(control, 1)  # enable outputSw
                    self._par[9 + servo] = control
                    self._par[2] &= ~(15)  # stop the ramp

        # locking emulation
        aux = 0x8000
        data = self._data_long[7]
        for servo in range(1, 9):
            indexoffset = (servo - 1) * 5
            state = (data[indexoffset] & 0x3)
            relock = (data[indexoffset] & 0x4)
            threshold = (data[indexoffset + 1] & 0xffff)
            greater = general.readBit(data[indexoffset + 1], 16)
            start = data[indexoffset + 2]

            control = self._par[9 + servo]

            if state == 0:
                data[indexoffset + 4] = 0

            if state == 2:
                if greater and (aux < threshold * .9):
                    if relock:
                        data[indexoffset] = 1 + relock
                    else:
                        data[indexoffset] = 0 + relock
                elif (not greater) and (aux > threshold * 0.9):
                    if relock:
                        data[indexoffset] = 1 + relock
                    else:
                        data[indexoffset] = 0 + relock

            if state == 1:
                if (greater and aux > threshold) or ((aux < threshold) and not greater):
                    data[indexoffset] = 2 + relock
                    control = general.setBit(control, 0)  # enable input
                    control = general.setBit(control, 1)  # enable output
                else:
                    data[indexoffset + 4] = start
                    control = general.clearBit(control, 0)  # input
                    control = general.clearBit(control, 1)  # output
            self._par[9 + servo] = control
            self._data_long[7] = data

    def _fpar_special_functions(self):
        pass
