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
        
        self.amplify_ratio = 1 # actually has 5 or 12 Volts 9/16
        self.parameters = ConfigParameters('Config.ini')
        
        self.trigger_s = 's'.encode('ascii') # start
        self.trigger_p = 'p'.encode('ascii') # end
        
        self.sample_rate_dict = SPECIFICATION.SAMPLE_RATE
        self.set_rs(10.0) #2021/02/04 update & default : 10ms
        

        
    def set_itrs(self):
        if self.sample_rate_ms >= 40:
            self.itrs = int(np.ceil(1000/self.sample_rate_ms)) # default : 1 sec. and changeable
            return True
        elif (self.sample_rate_ms < 40 and self.sample_rate_ms >= 10):
            self.itrs = int(np.ceil(300/self.sample_rate_ms)) # default: 0.3 sec. but unchangeable
            return False
        elif (self.sample_rate_ms < 10 and self.sample_rate_ms >= 2):
            self.itrs = int(np.ceil(100/self.sample_rate_ms)) # default: 0.1 sec. but unchangeable
            return False
        elif self.sample_rate_ms < 2:
            self.itrs = int(np.ceil(30/self.sample_rate_ms)) #default: 0.03 sec. but unchangeable
            return False
            
            
    # ;G1_1s+: 40ms(25.5kHz), 50ms(20.4kHz), 100ms(10.2kHz)
    # ;G2_0.3s: 10ms(102kHz), 20ms(51kHz), 30ms(34kHz)
    # ;G3_0.1s: 2ms(510kHz), 5ms(204kHz), 8ms(127.5kHz)
    # ;G4_0.03s: 0.68ms(1.5MHz), 0.75ms(1.36MHz), 1ms(1.02MHz), 1.5ms(682kHz)
    
        
    
    def connect_mcu(self):
        self.device = serial.Serial(self.parameters.comport, self.parameters.baudrate , timeout = 1)
        if self.device.isOpen():
            print("mcu is turned on")
        
    
    def disconnect_mcu(self):
        if self.device.isOpen():
            self.device.close()
            print("mcu is turned off")
        
    
    
    def set_rs(self, new_rs_in_ms):
        self.sample_rate_ms = new_rs_in_ms
        self.trigger_sample_rate = self.sample_rate_dict[str(self.sample_rate_ms)]
        self.sample_rate = 1020/(self.sample_rate_ms/1000)
        self.time_ctrl_enable = self.set_itrs() #12/3 update (>1s allowed)
        
        
        self.connect_mcu()
        if self.device.isOpen():
            self.device.write(self.trigger_p)
            self.device.write(serial.to_bytes(self.trigger_sample_rate))
            print("Setting sampling rate works!")
        self.disconnect_mcu()
    
    
    def collect_data(self):
    
        self.reset_data()
        data1 = b''
        data2 = b''
        data3 = b''
        self.connect_mcu()
        
        if self.device.isOpen():
        
            check_enable = True
            while check_enable:
                
                self.device.write(self.trigger_s)
                
                for n in range(self.itrs):
                
                    all_data = self.device.read(6144)
                    L = len(all_data)
                    print('total len = ',L)
                    if L < 6144:
                        print('length error')
                        check_enable = True
                        break
                    else:
                        channel_num1 = all_data[:2048][3]
                        channel_num2 = all_data[2048:4096][3]
                        channel_num3 = all_data[4096:6144][3]
                        baud_sn1 = all_data[:2048][2]
                        baud_sn2 = all_data[2048:4096][2]
                        baud_sn3 = all_data[4096:6144][2]
                        print("=> channel order {}, {}, {}".format(channel_num1, channel_num2, channel_num3))
                        print("=> baud sn {}, {}, {}".format(baud_sn1, baud_sn2, baud_sn3))
                        if (channel_num1 == 1 and channel_num2 == 2 and channel_num3 == 3) and (baud_sn1 == baud_sn2 == baud_sn3):
                            check_enable = False
                            data1 += all_data[:2048][6:-2]
                            data2 += all_data[2048:4096][6:-2]
                            data3 += all_data[4096:6144][6:-2]
                            print('append!')
                        else:
                            check_enable = True
                            data1 = b''
                            data2 = b''
                            data3 = b''
                            break
                            
                        
                self.device.write(self.trigger_p)
                
        self.disconnect_mcu()
        
        
        self.analyze_Baud_data(data1,data2,data3)
        
        
        
        print("finished!")
        
        
        
    def analyze_Baud_data(self, byte_data1, byte_data2, byte_data3):
        
        fmt = "<" + "h"*1020
        n_baud = int(len(byte_data1)/2040)
        
        n_time = 0
        for _ in range(n_baud):
            
            start = int(_*2040)
            end = int(start + 2040)
            aBaud_data1 = struct.unpack(fmt, byte_data1[start:end])
            aBaud_data2 = struct.unpack(fmt, byte_data2[start:end])
            aBaud_data3 = struct.unpack(fmt, byte_data3[start:end])
            
            aBaud_data1 = self.linear_transform(aBaud_data1)
            aBaud_data2 = self.linear_transform(aBaud_data2)
            aBaud_data3 = self.linear_transform(aBaud_data3)
            
            self.data_list_c1 = np.append(self.data_list_c1, aBaud_data1)
            self.data_list_c2 = np.append(self.data_list_c2, aBaud_data2)
            self.data_list_c3 = np.append(self.data_list_c3, aBaud_data3)
            self.time_list = np.append(self.time_list, np.arange(n_time*1020,(n_time+1)*1020,1)/(self.sample_rate))
    
            n_time += 1
             

    
    def linear_transform(self, data):
        data = np.array(data)*self.parameters.voltage_factor*self.amplify_ratio/4095
        return data
    
    
    def change_itrs(self, target_time): #only for fixed rs (group1 of rs)
        self.itrs = int(np.ceil(target_time*1000/self.sample_rate_ms))
    
    

    def reset_data(self):
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
        return filename
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
    
    