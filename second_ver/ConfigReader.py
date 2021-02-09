import numpy as np
import configparser


class ConfigParameters:
    
    def __init__(self, filename):
        self.config = configparser.ConfigParser()
        self.read_config(filename)
    

    def read_config(self, filename):
        self.config.read(filename)
        parameters = {}
        
        for mainkey in self.config.sections():
            for subkey in self.config[mainkey]:
                parameters.update({subkey:self.config[mainkey][subkey]})
                # print(subkey,':',self.config[mainkey][subkey])
        
        
        self.set_config(parameters)
        
    
    
    def set_config(self, parameters):
        # Setting
        self.comport = parameters['comport']
        self.baudrate = int(parameters['baudrate'])
        self.voltage_factor = float(parameters['voltage_factor'])
        self.web_port = int(parameters['web_port'])
        
        
        
        

if __name__ == "__main__":
    param = ConfigParameters('Config.ini')
    print(param.baudrate)
    
    