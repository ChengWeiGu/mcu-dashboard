import numpy as np


class SPECIFICATION:
    SAMPLE_RATE = {
                    '0.68': [0x62,0x70,0x73,0x60,0xE3,0x16,0x00], # '0x16E360' = 1500kpbs = 1.5Mbps (0.68ms)
                    '0.75': [0x62,0x70,0x73,0x80,0xc0,0x14,0x00], # '0x14C080' = 1360kbps = 1.36Mbps (0.75ms) 
                    '1.0': [0x62,0x70,0x73,0x60,0x90,0x0F,0x00], # '0xF9060' = 1020kbps = 1.02Mbps (1ms)
                    '1.5': [0x62,0x70,0x73,0x10,0x68,0x0A,0x00], # '0xA6810' = 682kbps = 0.682 Mbps (1.495ms)
                    '2.0': [0x62,0x70,0x73,0x30,0xc8,0x07,0x00], # '0x7C830' = 510k = 0.51M (2 ms)
                    '5.0': [0x62,0x70,0x73,0xE0,0x1c,0x03,0x00], # '0x31CE0' = 204k = 0.204M (5 ms)
                    '8.0': [0x62,0x70,0x73,0x0c,0xF2,0x01,0x00], # '0x1F20C' = 127.5k (8ms)
                    '10.0': [0x62,0x70,0x73,0x70,0x8E,0x01,0x00], # '0x18E70' = 102k (10 ms)
                    '20.0': [0x62,0x70,0x73,0x38,0xc7,0x00,0x00], # '0xc738' = 51k (20 ms)
                    '30.0': [0x62,0x70,0x73,0xD0,0x84,0x00,0x00], # '0x84D0' = 34k (30 ms)
                    '40.0': [0x62,0x70,0x73,0x9C,0x63,0x00,0x00], # '0x639C' = 25.5k (40 ms)
                    '50.0': [0x62,0x70,0x73,0xB0,0x4F,0x00,0x00], # '0x4FB0' = 20.4k (50 ms)
                    '100.0': [0x62,0x70,0x73,0xD8,0x27,0x00,0x00], # '0x27D8' = 10.2k (100 ms)
                    '500.0':[0x62,0x70,0x73,0xF8,0x07,0x00,0x00] # '0x7F8' = 2.04 kHz = 2040 Hz (500ms)
                    }
                    
    CONTROLL_LIMIT = {
                      '3': [3*0.95,3*1.05], #[LCL, UCL]
                      '5': [5*0.95,5*1.05],
                      '12': [12*0.95,12*1.05]
                     }
                     
    TABLE_FORMAT = {
                    'columns' : ['Item', 'Maximum Voltage(V)', 'Minimum Voltage(V)', 'Full Deviation(V)', 'Average Voltage(V)', 'RMS', 'STDEV(V)', 'CV(%)', 'OutPercentage%(+ or - 5%)'],
                    'data':[{'Item': 'Channel-%d'%(i+1), 
                            'Maximum Voltage(V)': 'N.A.', 
                            'Minimum Voltage(V)':'N.A.', 
                            'Full Deviation(V)':'N.A.', 
                            'Average Voltage(V)':'N.A.', 
                            'RMS':'N.A.',
                            'STDEV(V)':'N.A.',
                            'CV(%)':'N.A.',
                            'OutPercentage%(+ or - 5%)':'N.A.'} for i in range(3)] #df.to_dict('records')
                    
                    }
                    
                    
    FIGURE_FORMAT ={
                    'title': 'Voltage Data',
                    'channel':[1,2,3],
                    'linecolor':['rgb(0,0,255)','rgb(0,204,204)','rgb(128,0,128)']
                    
                    }
                     
                     

if __name__ == "__main__":
    spec = SPECIFICATION.SAMPLE_RATE
    print(spec['10'])