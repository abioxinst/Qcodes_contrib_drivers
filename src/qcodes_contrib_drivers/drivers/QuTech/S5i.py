from typing import Dict, Optional
from qcodes.instrument import Instrument
from qcodes.validators import Bool, Numbers

try:
    from spirack import S5i_module
except ImportError:
    raise ImportError(('The S5i_module class could not be found. '
                       'Try installing it using pip install spirack'))


class S5i(Instrument):
    """
    Qcodes driver for the S5i RF generator SPI-rack module.

    Args:
        name (str): name of the instrument.
        spi_rack (SPI_rack): instance of the SPI_rack class as defined in
            the spirack package. This class manages communication with the
            individual modules.
        module (int): module number as set on the hardware.
        frequency (float): RF frequency at startup, default is 41 MHz.
        enable_output (bool): Switch device output on or off, default is True.
        output_level (int): RF output level in dBm, default is 0 dBm.
    """

    def __init__(self, name, spi_rack, module, frequency=41e6,
                 enable_output=True, output_level=0, **kwargs):
        super().__init__(name, **kwargs)

        self.s5i = S5i_module(spi_rack, module, frequency=frequency,
                              enable_output=enable_output,
                              output_level=output_level)

        self.add_parameter('output_enabled',
                           label='RF output enabled',
                           initial_value=enable_output,
                           set_cmd=self.s5i.enable_output_soft,
                           vals=Bool(),
                           docstring='Switches output on/off')

        self.add_parameter('frequency_stepsize',
                           label='Frequency stepsize',
                           get_cmd=self._get_stepsize,
                           set_cmd=self.s5i.set_stepsize,
                           unit='Hz',
                           vals=Numbers(),
                           docstring='Set the optimal frequency stepsize for '
                                     'a minimal phase noise')

        self.add_parameter('frequency',
                           label='Frequency',
                           initial_value=frequency,
                           get_cmd=self._get_rf_frequency,
                           set_cmd=self.s5i.set_frequency,
                           unit='Hz',
                           vals=Numbers(40e6, 4e9),
                           docstring='Set RF frequency')

        self.add_parameter('power',
                           label='Output Power',
                           initial_value=output_level,
                           set_cmd=self.s5i.set_output_power,
                           unit='dBm',
                           vals=Numbers(-14, 20),
                           docstring='Set output power')

    def optimize_for_frequency(self) -> None:
        """
        This method finds the optimum stepsize for the set frequency.

        The stepsize affects the phase noise of the instrument. The smaller the
        stepsize, the greater is the phase noise. So this method sets the
        stepsize as large as possible for the current reference frequency.

        """
        stepsize = self.s5i.get_optimal_stepsize(self.s5i.rf_frequency)
        self.s5i.set_stepsize(stepsize)

    def _get_stepsize(self) -> float:
        return self.s5i.stepsize

    def _get_rf_frequency(self) -> float:
        return self.s5i.rf_frequency

    def get_idn(self) -> Dict[str, Optional[str]]:
        return dict(vendor='QuTech',
                    model='S5i',
                    serial='',
                    firmware='')
