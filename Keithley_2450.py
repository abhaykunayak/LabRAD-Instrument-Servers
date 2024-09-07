# AFY servers
# Keithley K2400
# AM Potts 2022
# NOTE - ramp functions are crude and will crash without time delays
# should NOT! be used for use with other active servers

"""
### BEGIN NODE INFO
[info]
name = Keithley Server 2450
version = 1.1
description = 

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import setting
from labrad.gpib import GPIBManagedServer
from twisted.internet.defer import inlineCallbacks, returnValue
import time
import numpy as np


class K2450(GPIBManagedServer):
    name = 'K2450'  # Server name
    deviceName = 'KEITHLEY INSTRUMENTS MODEL 2450'  # Model string returned from *IDN?

   
    # ok
    @setting(111, volts='v', returns='v')
    def set_volts(self, c, volts, compl = 1e-6):
        dev = self.selectedDevice(c)
        yield dev.write(':SOUR:VOLT ' + str(volts))
        yield dev.write(':SOURce:VOLTage:ILIM ' + str(compl))
        voltage = yield dev.query(':MEAS:VOLT:DC?')
        voltage = (voltage.split(',')[0] )
        returnValue(float(voltage))
        #returnValue(voltage)

    # ok
    @setting(112, returns='v')
    def get_volts(self, c):
        dev = self.selectedDevice(c)
        yield dev.write(':OUTPUT ON')
        voltage = yield dev.query(':READ?')
        voltage = voltage[1:12]
        returnValue(voltage)
    
    # okay as long as you autorange 
    @setting(113, volts='v', returns='v')
    def set_v_meas_i(self, c, volts, compl = 1e-6, autorange = 0):
        dev = self.selectedDevice(c)
        yield dev.write('SOUR:VOLT ' + str(volts))
        yield dev.write(':OUTP ON')
        # not rigorously tested
        if (autorange == 1):
            yield dev.write(':SENSe:CURRent:RANGe:AUTO ON')
        else:
            yield dev.write(':SENSe:CURRent:RANGe:AUTO OFF')

        yield dev.write(':SOURce:VOLTage:ILIM ' + str(compl))
        current = yield dev.query('MEAS:CURR:DC?')
        current = (current.split(',')[0] )
        returnValue(float(current))
        returnValue(1.0)
    
    # ok
    @setting(116)
    def output_on(self, c):
        dev = self.selectedDevice(c)
        yield dev.write(':OUTP ON')     
        returnValue(1)
        
    # ok    
    @setting(117)
    def output_off(self, c):
        dev = self.selectedDevice(c)
        yield dev.write(':OUTP OFF')     
        returnValue(0)
    
    # ok
    @setting(118, returns = 'v')
    def read_v(self, c):
        dev = self.selectedDevice(c)
        data = yield dev.query('MEAS:CURR:DC?')   
        volts = (data.split(',')[0] )  
        returnValue( float(volts) )
    
    # ok  
    @setting(119, returns = 'v')
    def read_i(self, c):
        dev = self.selectedDevice(c)
        data = yield dev.query('MEAS:CURR:DC?')
        print(data)
        current = (data.split(',')[0] )   
        returnValue( float(current) )
    
    @setting(120, returns = 'v')
    def set_nplc_current(self, c, nplc):
        dev = self.selectedDevice(c)
        yield dev.write('SENS:CURR:NPLC %s' %( str(nplc) ) )
        returnValue( 1 )
        
        
    @setting(121, returns = 'v')
    def set_nplc_voltage(self, c, nplc):
        dev = self.selectedDevice(c)
        data = yield dev.write('SENS:VOLT:NPLC %s' %( str(nplc) ) )
        returnValue( data )
    
    
    # Hacky, but functional. Requires asynch sleep. From K2450 manual, pdf page 226
    @setting(122)
    def ramp_volt_SCPI(self,  c, start_num, stop_num, step_num, compl = 1e-6 ):  
        dev = self.selectedDevice(c)
        yield dev.write('*RST')
        yield dev.write(':TRACe:CLEar "defbuffer1"')
        yield dev.write(':OUTP OFF')
        yield dev.write(':SOUR:FUNC VOLT')   
        yield dev.write('SOUR:VOLT:ILIM ' + str(compl)) 
        yield dev.write(':SENS:FUNC "CURR"') 
        yield dev.write('SENS:CURR:RANG:AUTO ON')
        yield dev.write('SOUR:SWE:VOLT:LIN %s, %s, %s, 200e-3' %( str(start_num), str(stop_num), str(step_num) ) )   
        yield dev.write('INIT')
        yield dev.write('*WAI')
        time.sleep( 1  * float(step_num) )
        # proper way to fix this...
        # check the buffer size before dumping data (':TRAC:ACT?')
        # if the buffer has filled to appropriate level, then proceed
        # simple implementation has issues, needs to be fixed later

        data = yield dev.query('TRAC:DATA? 1, %s, "defbuffer1", SOUR, READ' %(step_num) )
        listData = data.split(',')
        currentStr = [listData[idx] for idx in range(1, len(listData), 2)]
        currentFloat = [float(x) for x in currentStr]
        returnValue( currentFloat )

    # Hacky, but functional. Requires asynch sleep. From K2450 manual, pdf page 226
    # see notes in ramp_volt_SCPI function
    @setting(123, returns = [])
    def ramp_current_SCPI(self,  c, start_num, stop_num, step_num, compl = 1 ):  
        dev = self.selectedDevice(c)
        yield dev.write('*RST')
        yield dev.write(':TRACe:CLEar "defbuffer1"')
        yield dev.write(':OUTP OFF')
        yield dev.write(':SOUR:FUNC CURR')  
        yield dev.write(':SENS:FUNC "VOLT"') 
        yield dev.write('SENS:VOLT:RANG:AUTO ON')
        yield dev.write('SOUR:CURR:VLIM ' + str(compl) )
        yield dev.write('SOUR:SWE:CURR:LIN %s, %s, %s, 200e-3' %( str(start_num), str(stop_num), str(step_num) ) )   
        yield dev.write('INIT')
        yield dev.write('*WAI')
        time.sleep( 1  * float(step_num) )
        data = yield dev.query('TRAC:DATA? 1, %s, "defbuffer1", SOUR, READ' %(step_num) )
        listData = data.split(',')
        voltStr = [listData[idx] for idx in range(1, len(listData), 2)]
        voltFloat = [float(x) for x in voltStr]
        
        returnValue( voltFloat )
     
    # disable autoranging, sets range manually, Ok
    @setting(124, returns = 'v')
    def set_i_read_range(self, c, value = 10e-6):
        dev = self.selectedDevice(c)
        yield dev.write('SENS:CURR:RANGe:AUTO ON')
        yield dev.write(':SENS:CURR:RANG %s' %( str(value) ) )   
        returnValue( 1 )  


    # enables autoranging. Ok
    @setting(125, returns = 'v')
    def autorange_enable(self, c):
        dev = self.selectedDevice(c)
        data = yield dev.write('SENS:CURR:RANGe:AUTO ON')
        returnValue( 1 )        
   
        
__server__ = K2450()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
