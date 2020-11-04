# there are 20 pauds of data from STM32

import serial
import struct
import numpy as np
import pandas as pd

from ConfigReader import ConfigParameters

import os
import time
import datetime
from Specification import SPECIFICATION
# import matplotlib.pyplot as plt
# from os.path import join, basename


class MCU_STM32F7:
    
    def __init__(self):
        
        self.data_list_c1 = np.array([])
        self.data_list_c2 = np.array([])
        self.data_list_c3 = np.array([])
        self.time_list = np.array([])
        
        self.n_baud = 0
        self.amplify_ratio = 1 # actually has 5 or 12 Volts 9/16
        self.parameters = ConfigParameters('Config.ini')
        
        self.trigger_s = 's'.encode('ascii') # start
        self.trigger_p = 'p'.encode('ascii') # end
        self.sample_rate_ms = self.parameters.sample_rate # in ms
        self.itrs = int(1000/self.sample_rate_ms) # default : 1 sec.
        self.sample_rate_dict = SPECIFICATION.SAMPLE_RATE

        self.trigger_sample_rate = self.sample_rate_dict[str(self.sample_rate_ms)]

        
        self.sample_rate = 1020/(self.sample_rate_ms/1000)
        
        
    
    def connect_mcu(self):
        self.device = serial.Serial(self.parameters.comport, self.parameters.baudrate , timeout = 1)
        
        if self.device.isOpen():
            self.device.write(self.trigger_p)
            self.device.write(serial.to_bytes(self.trigger_sample_rate))
            self.device.write(self.trigger_s)
            print("Setting sampling rate works!")
    
    def disconnect_mcu(self):
        if self.device.isOpen():
            self.device.write(self.trigger_p)
            self.device.close()
            print("stm32 is turned off")
        else:
            pass
    
    
    
    def collect_aBaud_data(self):
        
        
        fmt = "<" + "h"*1020
        
        
        if self.device.isOpen():
            
            
            data = self.device.read(6144)
            channel_num1 = data[:2048][3]
            channel_num2 = data[2048:4096][3]
            channel_num3 = data[4096:6144][3]
            baud_sn1 = data[:2048][2]
            baud_sn2 = data[2048:4096][2]
            baud_sn3 = data[4096:6144][2]
            print("=> channel order {}, {}, {}".format(channel_num1, channel_num2, channel_num3))
            print("=> baud sn {}, {}, {}".format(baud_sn1, baud_sn2, baud_sn3))
            
            
            if not ((channel_num1 == 1 and channel_num2 == 2 and channel_num3 == 3) and (baud_sn1 == baud_sn2 == baud_sn3)):
                return False
            
            

            data1 = data[:2048][6:-2]
            data2 = data[2048:4096][6:-2]
            data3 = data[4096:6144][6:-2]
            
            
            try:
                
                aBaud_data1 = struct.unpack(fmt, data1)
                aBaud_data2 = struct.unpack(fmt, data2)
                aBaud_data3 = struct.unpack(fmt, data3)
                aBaud_data1 = self.linear_transform(aBaud_data1)
                aBaud_data2 = self.linear_transform(aBaud_data2)
                aBaud_data3 = self.linear_transform(aBaud_data3)
                
                
                self.data_list_c1 = np.append(self.data_list_c1, aBaud_data1)
                self.data_list_c2 = np.append(self.data_list_c2, aBaud_data2)
                self.data_list_c3 = np.append(self.data_list_c3, aBaud_data3)
                self.time_list = np.append(self.time_list, np.arange(self.n_baud*1020,(self.n_baud+1)*1020,1)/(self.sample_rate))
                
                self.n_baud += 1
                
            except:
                print("data length is zero")
            
            
            return True
                
        else:
            print("Fail to open device")
            return False
            
            
            
        

    
    def linear_transform(self, data):
        data = np.array(data)*self.parameters.voltage_factor*self.amplify_ratio/4095
        return data
    
    
    def change_itrs(self, target_time):
        self.itrs = int(target_time*1000/self.sample_rate_ms)
    

    def collect_long_data(self):
        self.reset_data()
        delay = self.sample_rate_ms + 1
        
        self.connect_mcu()
        
        count = 0
        while (count < self.itrs):
            time.sleep(delay/1000)
            check_bool = self.collect_aBaud_data()
            if not check_bool:
                self.disconnect_mcu()
                self.connect_mcu()
                continue
            else:
                count += 1
        
        
        self.disconnect_mcu()
        
    
    
    def reset_data(self):
        self.n_baud = 0
        self.data_list_c1 = np.array([])
        self.data_list_c2 = np.array([])
        self.data_list_c3 = np.array([])
        self.time_list = np.array([])
            
    
    def save_data(self, data_dir = './data/'):
        
        datetime_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_data')
        filename = data_dir + datetime_now + '.csv'
        
        try:
            os.makedirs(data_dir)
        except OSError:
            if not os.path.isdir(data_dir):
                raise
                
        time = self.time_list.reshape(-1,1)
        data1 = self.data_list_c1.reshape(-1,1)
        data2 = self.data_list_c2.reshape(-1,1)
        data3 = self.data_list_c3.reshape(-1,1)
        merge_data = np.hstack([time,data1,data2,data3])
        pd.DataFrame(merge_data,columns = ['time(sec.)','Channel-1(V)','Channel-2(V)','Channel-3(V)']).to_csv(filename, index = False)
        # np.savetxt(filename, merge_data, delimiter = ",")
        
        
        
        

if __name__ == "__main__":
     mcu = MCU_STM32F7()
     delta = 0
     delta_tot = 0
     delay = mcu.sample_rate_ms + 2
     itrs = 100
     # for i in range(itrs):
        # t_1 = time.time()
        # mcu.collect_aBaud_data(3)
        # t_2 = time.time()
        # time.sleep(delay/1000)
        # t_3 = time.time()
        # delta += (t_2 - t_1)
        # print(f'{i}: {t_2 - t_1}')
        # delta_tot += (t_3 - t_1)
        
     # print(f'ave. time cost = {delta/itrs} sec.')
     # print(f'total time cost = {delta_tot} sec.')
     # print('data len = ', len(mcu.time_list))
     # plt.plot(mcu.time_list, mcu.data_list)
     # plt.xlim([0,1])
     # plt.ylim([0,5])
     # plt.show()
    
    