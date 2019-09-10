"""Support for I2C PCAL9535A chip."""

# Datasheet: https://www.nxp.com/docs/en/data-sheet/PCAL9535A.pdf

class PCAL9535A:
    """Represents the PCAL9535A device.

    The PCAL9535A is a low-voltage 16-bit General Purpose Input/Output (GPIO) expander.

    Methods
    -------
    get_output_configuration(port)
        Get open-drain or push-pull port configuration
    set_output_configuration(port, is_open_drain)
        Configure open-drain/push-pull port-wise
    get_pin(port, pin)
        Get an object representing the pin
    """
    _config_reg = {}
    _output_reg = {}
    _polarity_reg = {}
    _pullup_sel_reg = {}
    _pullup_enable_reg = {}
    _output_conf_reg = {}
    _drive_strength_reg = {}

    def __init__(self, i2c_busnum = 1, i2c_address = 0x20, caching = True):
        """Initialize the class.

        Parameters
        ----------
        i2c_busnum: int
            I2C bus number (default is 1)
        i2c_address: int
            I2C device address (default is 0x20). Three hardware pins (A0, A1, A2) select the fixed I2C-bus address and allow up to eight devices to share the same I2C-bus/SMBus. See Section 6.1 of the Datasheet
        caching: bool
            Allows caching of register values to speed up updates. Disable, if you want separate applications to control same device (default is True)
        """
        from smbus import SMBus

        self._dev = i2c_busnum, i2c_address
        self._bus = SMBus(i2c_busnum)
        self._i2c_address = i2c_address
        self._caching = caching
        if self._caching and (self._dev) not in PCAL9535A._config_reg:
            PCAL9535A._config_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x06),
                    1: self._bus.read_byte_data(self._i2c_address, 0x07),
                    }
            PCAL9535A._output_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x02),
                    1: self._bus.read_byte_data(self._i2c_address, 0x03),
                    }
            PCAL9535A._polarity_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x04),
                    1: self._bus.read_byte_data(self._i2c_address, 0x05),
                    }
            PCAL9535A._pullup_enable_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x46),
                    1: self._bus.read_byte_data(self._i2c_address, 0x47),
                    }
            PCAL9535A._pullup_sel_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x48),
                    1: self._bus.read_byte_data(self._i2c_address, 0x49),
                    }
            PCAL9535A._output_conf_reg[self._dev] = self._bus.read_byte_data(self._i2c_address, 0x4f)
            PCAL9535A._drive_strength_reg[self._dev] = {
                    0: self._bus.read_byte_data(self._i2c_address, 0x40),
                    1: self._bus.read_byte_data(self._i2c_address, 0x41),
                    2: self._bus.read_byte_data(self._i2c_address, 0x42),
                    3: self._bus.read_byte_data(self._i2c_address, 0x43),
                    }

    def get_output_configuration(self, port):
        """Get open-drain/push-pull port configuration
        
        Parameters
        ----------
        port: int
            The port number to read (0 or 1)

        Returns
        -------
        bool
            True means the I/O is open-drain (Q1 is disabled, Q2 is active)
            False means the I/O is push-pull (Q1 and Q2 are active, see Figure 6 of the Datasheet)
        """
        if port < 0 or port > 1:
            raise Exception("Invalid port number")

        PCAL9535A._output_conf_reg[self._dev] = self._bus.read_byte_data(self._i2c_address, 0x4f)

        return PCAL9535A._output_conf_reg[self._dev] & ((0x01) << port) != 0

    def set_output_configuration(self, port, is_open_drain):
        """Configure open-drain/push-pull port-wise.

        The output port configuration register selects port-wise push-pull or open-drain I/O stage. It is recommended to configure this setting (if needed) before changing the pins direction to output.
        
        Parameters
        ----------
        port: int
            The port number to configure (0 or 1)
        is_open_drain: bool
            True configures the I/O as open-drain (Q1 is disabled, Q2 is active)
            False configures the I/O as push-pull (Q1 and Q2 are active, see Figure 6 of the Datasheet)
            Power-up default: False
        """
        if port < 0 or port > 1:
            raise Exception("Invalid port number")

        if not self._caching:
            PCAL9535A._output_conf_reg[self._dev] = self._bus.read_byte_data(self._i2c_address, 0x4f)

        if is_up:
            PCAL9535A._output_conf_reg[self._dev] |= ((0x01) << port)
        else:
            PCAL9535A._output_conf_reg[self._dev] &= ~((0x01) << port)

        self._bus.write_byte_data(self._i2c_address, 0x4f,
                PCAL9535A._output_conf_reg[self._dev])

    def _get_direction(self, port, pin):
        """Returns whether the pin is input or output"""
        PCAL9535A._config_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x06 + port)

        return PCAL9535A._config_reg[self._dev][port] & ((0x01) << pin) != 0

    def _set_direction(self, port, pin, is_input):
        """Set pin to be input or output."""
        if not self._caching:
            PCAL9535A._config_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x06 + port)

        if is_input:
            if not PCAL9535A._config_reg[self._dev][port] & ((0x01) << pin):
                PCAL9535A._config_reg[self._dev][port] |= ((0x01) << pin)
                self._bus.write_byte_data(self._i2c_address, 0x06 + port,
                        PCAL9535A._config_reg[self._dev][port])
        else:
            if PCAL9535A._config_reg[self._dev][port] & ((0x01) << pin):
                #Pin was previously configured as input, switch it off before configuring as output
                self.set_level(port, pin, False)
                PCAL9535A._config_reg[self._dev][port] &= ~((0x01) << pin)
                self._bus.write_byte_data(self._i2c_address, 0x06 + port,
                        PCAL9535A._config_reg[self._dev][port])

    def _get_inverted(self, port, pin):
        """Get the polarity inversion settings."""
        PCAL9535A._polarity_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x04 + port)

        return PCAL9535A._polarity_reg[self._dev][port] & ((0x01) << pin) != 0

    def _set_inverted(self, port, pin, is_inverted):
        """Inverse the polarity of an input pin."""
        if not self._caching:
            PCAL9535A._polarity_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x04 + port)

        if is_inverted:
            PCAL9535A._polarity_reg[self._dev][port] |= ((0x01) << pin)
        else:
            PCAL9535A._polarity_reg[self._dev][port] &= ~((0x01) << pin)

        self._bus.write_byte_data(self._i2c_address, 0x04 + port,
                PCAL9535A._polarity_reg[self._dev][port])

    def _get_pullup_enable(self, port, pin):
        """Check whether pullup/pulldown resistors enabled for a pin."""
        PCAL9535A._pullup_enable_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x46 + port)

        return PCAL9535A._pullup_enable_reg[self._dev][port] & ((0x01) << pin) != 0

    def _set_pullup_enable(self, port, pin, is_enabled):
        """Enable or disable pullup/pulldown resistors for a pin."""
        if not self._caching:
            PCAL9535A._pullup_enable_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x46 + port)

        if is_enabled:
            PCAL9535A._pullup_enable_reg[self._dev][port] |= ((0x01) << pin)
        else:
            PCAL9535A._pullup_enable_reg[self._dev][port] &= ~((0x01) << pin)

        self._bus.write_byte_data(self._i2c_address, 0x46 + port,
                PCAL9535A._pullup_enable_reg[self._dev][port])

    def _get_pullup_sel(self, port, pin):
        """Get pullup/pulldown resistors for a pin."""
        PCAL9535A._pullup_sel_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x48 + port)

        return PCAL9535A._pullup_sel_reg[self._dev][port] & ((0x01) << pin) != 0

    def _set_pullup_sel(self, port, pin, is_up):
        """Configure pullup/pulldown resistors for a pin."""
        if not self._caching:
            PCAL9535A._pullup_sel_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x48 + port)

        if is_up:
            PCAL9535A._pullup_sel_reg[self._dev][port] |= ((0x01) << pin)
        else:
            PCAL9535A._pullup_sel_reg[self._dev][port] &= ~((0x01) << pin)

        self._bus.write_byte_data(self._i2c_address, 0x48 + port,
                PCAL9535A._pullup_sel_reg[self._dev][port])

    def _get_drive_strength(self, port, pin):
        """Get output drive strength for a pin."""
        PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4] = self._bus.read_byte_data(self._i2c_address, 0x40 + port*2 + pin//4)

        return (PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4] & ((level) << pin%4 * 2)) >> pin%4 * 2

    def _set_drive_strength(self, port, pin, level):
        """Configure output drive strength for a pin."""
        if level < 0 or level > 3:
            raise Exception("Invalid level")

        if not self._caching:
            PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4] = self._bus.read_byte_data(self._i2c_address, 0x40 + port*2 + pin//4)

        PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4] &= ~((0x11) << pin%4 * 2)
        PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4] |= ((level) << pin%4 * 2)

        self._bus.write_byte_data(self._i2c_address, 0x40 + port*2 + pin//4,
                PCAL9535A._drive_strength_reg[self._dev][port*2 + pin//4])

    def _set_level(self, port, pin, is_high):
        """Set the outgoing logic level of the pin."""
        if not self._caching:
            PCAL9535A._output_reg[self._dev][port] = self._bus.read_byte_data(self._i2c_address, 0x02 + port)

        if is_high:
            PCAL9535A._output_reg[self._dev][port] |= ((0x01) << pin)
        else:
            PCAL9535A._output_reg[self._dev][port] &= ~((0x01) << pin)

        self._bus.write_byte_data(self._i2c_address, 0x02 + port,
                PCAL9535A._output_reg[self._dev][port])

    def _get_level(self, port, pin):
        """Return the state of the pin"""
        # TODO: Test if output pins are read correctly, including inverse logic
        return self._bus.read_byte_data(self._i2c_address, 0x00 + port) & ((0x01) << pin) != 0

    class _pin:
        """Convenience proxy class representing one pin

        Properties
        ----------
        input: bool
            Read or set direction of the pin
            True: Input
            False: Output
            Power-up default: True
        level: bool
            Read or set the logic level of the pin
            True: High
            False: Low
            Power-up default: Determined by the externally applied logic level
        inverted: bool
            Read or set polarity inversion of an input pin
            True: Inverted
            False: Not inverted
            Power-up default: False
        pullup: int
            Read or set pull-up/pull-down resistors configuration for the pin
            0: Disabled
            1: Pull-down
            2: Pull-up
            Power-up default: 0
        drive_strength: int
            Read or set the output drive level of the GPIO
            0: 0.25x of the maximum drive capability of the I/O
            1: 0.50x of the maximum drive capability of the I/O
            2: 0.75x of the maximum drive capability of the I/O
            3: 1x of the maximum drive capability of the I/O
            Power-up default: 3
        """

        def __init__(self, pcal, port, pin):
            """Initialize the class.

            Parameters
            ----------
            pcal: PCAL9535A
                The device class
            port: int
                    The port number (0 or 1)
            pin: int
                The pin number (0 to 7, inclusive)
            """
            self._pcal = pcal
            self._port = port
            self._pin = pin

        @property
        def input(self):
            """Read the direction of the pin

            Returns
            -------
            bool
                True: Input
                False: Output
            """
            return self._pcal._get_direction(self._port, self._pin)

        @input.setter
        def input(self, is_input):
            """Set the direction of the pin

            Parameters
            ----------
            is_input: bool
                True: Input
                False: Output
                Power-up default: True
            """
            self._pcal._set_direction(self._port, self._pin, is_input)

        @property
        def level(self):
            """Read the logic level of the pin

            Returns
            -------
            bool
                True: High
                False: Low
            """
            return self._pcal._get_level(self._port, self._pin)

        @level.setter
        def level(self, is_high):
            """Set the logic level of the pin

            Parameters
            ----------
            is_high: bool
                True: High
                False: Low
                Power-up default: Determined by the externally applied logic level
            """
            self._pcal._set_level(self._port, self._pin, is_high)

        @property
        def inverted(self):
            """Read the polarity inversion of pins defined as inputs. The value has no effect on pins defined as outputs
            
            Returns
            -------
            bool
                True: The corresponding port pin’s polarity is inverted in the level property of this class
                False: The corresponding port pin’s polarity is retained
            """
            return self._pcal._get_inverted(self._port, self._pin)

        @inverted.setter
        def inverted(self, is_inverted):
            """Set the polarity inversion of pins defined as inputs. The method has no effect on pins defined as outputs

            Parameters
            ----------
            is_inversed: bool
                True: The corresponding port pin’s polarity is inverted in the level property of this class
                False: The corresponding port pin’s polarity is retained
                Power-up default: False
            """
            self._pcal._set_inverted(self._port, self._pin, is_inverted)

        @property
        def pullup(self):
            """Read the pull-up/pull-down resistors configuration for the pin. The value has no effect if the port is configured as open-drain

            Returns
            -------
            int
                0: Disabled
                1: Pull-down
                2: Pull-up
            """
            if self._pcal._get_pullup_enable(self._port, self._pin):
                return 0
            elif self._pcal._get_pullup_sel(self._port, self._pin):
                return 2
            else:
                return 1

        @pullup.setter
        def pullup(self, selector):
            """Set the pull-up/pull-down resistors configuration for the pin. The method has no effect if the port is configured as open-drain

            Parameters
            ----------
            selector: int
                0: Disconnect the pull-up/pull-down resistors from the I/O pin
                1: Select a 100 kOhm pull-down resistor for that I/O pin
                2: Select a 100 kOhm pull-up resistor for that I/O pin
                Power-up default: 0
            """
            self._pcal._set_pullup_enable(self._port, self._pin, selector != 0)
            if selector > 0:
                self._pcal._set_pullup_sel(self._port, self._pin, selector - 1 != 0)

        @property
        def drive_strength(self):
            """Read the output drive level configuration of the GPIO

            Returns
            -------
            int
                0: 0.25x of the maximum drive capability of the I/O
                1: 0.50x of the maximum drive capability of the I/O
                2: 0.75x of the maximum drive capability of the I/O
                3: 1x of the maximum drive capability of the I/O
            """
            return self._pcal._get_drive_strength(self._port, self._pin)

        @drive_strength.setter
        def drive_strength(self, level):
            """Set the output drive level of the GPIO

            Parameters
            ----------
            level: int
                0: 0.25x of the maximum drive capability of the I/O
                1: 0.50x of the maximum drive capability of the I/O
                2: 0.75x of the maximum drive capability of the I/O
                3: 1x of the maximum drive capability of the I/O
                Power-up default: 3
            """
            self._pcal._set_drive_strength(self._port, self._pin, level)
        
    def get_pin(self, port, pin):
        """Get an object representing the pin

        Parameters
        ----------
        port: int
            The port number (0 or 1)
        pin: int
            The pin number (0 to 7, inclusive)

        Returns
        -------
        _pin
            The object that allows configuring and reading the selected pin
        """
        if port < 0 or port > 1:
            raise Exception("Invalid port number")
        if pin < 0 or pin > 7:
            raise Exception("Invalid pin number")
        return _pin(self, port, pin)
