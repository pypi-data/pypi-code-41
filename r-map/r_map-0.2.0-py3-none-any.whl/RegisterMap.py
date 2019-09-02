from .AddressedNode import AddressedNode
from math import ceil

def get_dimensions(start_address, reg_address, width):
    start_index = reg_address - start_address
    end_index = start_index + int(ceil(width/8))
    num_bytes = end_index - start_index
    return start_index, end_index, num_bytes

class RegisterMap(AddressedNode):

    @property
    def _block_dimensions(self):
        if hasattr(self, '__block_dimensions'):
            return self.__block_dimensions
        if len(self):
            regs = list(self)
            start_address = regs[0].address
            last_reg = regs[-1]
            highest_address = last_reg.address + int(ceil(last_reg.width/8))
            block_width = highest_address - start_address
            self._block_dimensions = (start_address, block_width)
            return start_address, block_width
        else:
            raise ValueError(f"Register map: {self.name} has no registers!")

    @_block_dimensions.setter
    def _block_dimensions(self, dimensions):
        self.__block_dimensions = dimensions

    def read(self):
        address, size = self._block_dimensions
        #assume bytes are returned and in little endian
        #if your system uses big endian, wrap the IO function accordingly!
        data = self._block_read_func(address, size)
        for r in self:
            start_index, end_index, num_bytes = get_dimensions(address, r.address, r.width)
            val = int.from_bytes(data[start_index:end_index], byteorder='little')
            r.value = val
        return data

    def write(self, data=None):
        address, size = self._block_dimensions
        if data is None:
            _data = bytearray(size)
        else:
            _data = data

        if len(self) == 0:
            raise ValueError(f"No registers found in {self}")

        if data is None:
            for r in self:
                start_index, end_index, num_bytes = get_dimensions(address,
                                                                   r.address,
                                                                   r.width)
                val_bytes = r.value.to_bytes(num_bytes, byteorder='little')
                _data[start_index:end_index] = val_bytes
        else:
            data_len = len(_data)
            for r in self:
                start_index, end_index, num_bytes = get_dimensions(address,
                                                                   r.address,
                                                                   r.width)
                if end_index > data_len + 1:
                    #user has supplied less bytes than the size of the block.
                    #It's a feature to support a partial block write
                    break
                val = int.from_bytes(_data[start_index:end_index], byteorder='little')
                r.value = val

        self._block_write_func(address, _data)

