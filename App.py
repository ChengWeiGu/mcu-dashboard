# ref: https://pythonprogramming.net/live-graphs-data-visualization-application-dash-python-tutorial/

import dash
import numpy as np
import time
import io
import base64
import pandas as pd

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_table

import plotly.graph_objs as go


from MCU import MCU_STM32F7
from Specification import SPECIFICATION


class WaveFormApp:
    
    def __init__(self):
        
        
        self.mcu = MCU_STM32F7()
        self.start_button_clicks = 0
        self.upload_button_clicks = 0
        # self.app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], title = 'Data Collector')
        self.app = dash.Dash(__name__, title = 'WaveForm Analyzer')
        self.app.css.append_css({"external_url": 'mycss.css'})
        
        
        self.controll_limit_dict = SPECIFICATION.CONTROLL_LIMIT
        self.data_table_fmt = SPECIFICATION.TABLE_FORMAT
        self.fig_color_fmt = SPECIFICATION.FIGURE_FORMAT
        self.LCL, self.UCL = self.controll_limit_dict['3'] #default 3.0 V
        
        self.web_port = self.mcu.parameters.web_port
        self.web_host = '127.0.0.1'
        
        self.app.layout = html.Div([ 
            
            html.H1(id = 'Program-Name',children='WaveForm Analyzer', style={'font-wmaxDataPts': 'bold'}), #style = {'text-align':'center', 'font-size':16, 'transform':"rotate(0deg)"} 
            html.Hr(),
            
            html.Div(className = 'row',
                    style = {"margin-left": "10px", "margin-top": "10px"},
                    children = [
                        html.Div(className = 'three columns',
                                children = [dcc.RadioItems(id = 'mode-items', 
                                                            options = [{'label':'Real Mode', 'value':'rm'},
                                                                       {'label':'File Mode', 'value':'fm'}
                                                                       ],
                                                                       value = 'rm',
                                                                       labelStyle={'display': 'inline-block'}
                                                            )
                                ], style={'float': 'left', "margin-left": "20px"}),
                                
                        
                        html.Div(className = 'three columns',
                                children = [
                                        html.Div(className = 'five columns', children = "Voltage Selection: ",id='dropdown-label', style={'font-size':16}),
                        
                                        html.Div(className = 'four columns',
                                                children = [
                                                            dcc.Dropdown(id='dropdown-voltage',
                                                                        options=[
                                                                            {'label': '3.0V', 'value': 3},
                                                                            {'label': '5.0V', 'value': 5},
                                                                            {'label': '12.0V', 'value': 12}
                                                                        ],
                                                                        value=3,
                                                                        clearable=False
                                                                        )
                                                        ],
                                                style = {'width':'30%', 'height':'30px', 'display':'inline-block', 'float': 'left', "margin-left": "5px"},
                                        )
                                
                                ]),
                        
                        
                        html.Div(className = 'three columns',
                                children = [
                                        html.Div(className = 'four columns', children = "Time Scale: ",id='timescale-label', style={'font-size':16}),
                                        html.Div(className = 'three columns',
                                                children = [
                                                        daq.NumericInput(id='numeric-input',
                                                                 value=1,
                                                                 size = 60,
                                                                 label = '(s)',
                                                                 labelPosition  = 'right',
                                                                 min = 1,
                                                                 max = 5)
                                            ], style = {'width':'30%', 'height':'30px', 'display':'inline-block', 'float': 'left', "margin-left": "5px"})
                                ]),
                                
                    ]),
            
            
            
            html.Div(className='row',
                    style = {"margin-top": "50px"},
                    children = [
                        
                        html.Div(children = [
                            dbc.Button('Start', id = 'start-button', n_clicks = 0,style = {'float': 'left', "margin-left": "60px"}),
                            dbc.Spinner(html.Div(id="loading-output", children = ""),fullscreen=True),
                            # html.Button('Start', id = 'start-button', n_clicks = 0,style = {'float': 'left', "margin-left": "60px"}),
                            dcc.Upload(id = 'data-upload', children = [html.Button('Upload File', id = 'upload-button', n_clicks = 0, style = {'float': 'left', "margin-left": "20px"})]),
                            dcc.Input(id = "filename-input", type = "text", placeholder="Upload a file; Select File Mode at first", style = {'width':'20%', 'float': 'left', "margin-left": "20px"}, disabled = False)
                        ])
                        
                    ]),

            
            html.Div(className='row',
                     style = {"margin-top": "20px"},
                     children = [
                        dcc.Graph(id='live-graph', figure = {
                                                            'data' : [
                                                                go.Scatter(
                                                                x = [],
                                                                y = [],
                                                                mode = "lines",
                                                                name = "Data"
                                                                )
                                                            ],
                                                            
                                                            'layout' : go.Layout(
                                                                title = self.fig_color_fmt['title'],
                                                                xaxis = {'title': 'Time(ms)', 'gridcolor': 'rgb(255,255,255)'},
                                                                yaxis = {'title': 'Voltage (V)', 'gridcolor': 'rgb(255,255,255)'},
                                                                plot_bgcolor = 'rgb(200,200,200)'
                                                                )
                                                            }
                                                        ),
                                                        
                ]),
            html.Div(className='row',
                     children = [
                        dash_table.DataTable(
                                                id='data-table',
                                                columns=[{"name": n, "id": n} for n in self.data_table_fmt['columns']],
                                                data=self.data_table_fmt['data'],
                                                style_cell = {'font_family': 'Arial','font_size': '14px', 'text_align': 'center'},
                                                style_header={'backgroundColor': 'white','fontWeight': 'bold'}
                                            )
                    ], style={"margin-top": "50px", 'margin': 'auto', 'textAlign': 'center','width':'85%'}),
            
        ])
        
        
        
        
        @self.app.callback(
              [Output('live-graph', 'figure'),
              Output('data-table', 'data'),
              Output('loading-output', 'children')],
              [Input('start-button', 'n_clicks'),
              Input('dropdown-voltage','value'),
              Input('mode-items','value'),
              Input('numeric-input','value')])
        def plot_diagram(n_clicks, dropdown_value, mode_value, numeric_value):
            
            self.mcu.amplify_ratio = dropdown_value/3.0
            self.LCL, self.UCL = self.controll_limit_dict[str(dropdown_value)]
            self.mcu.change_itrs(target_time = numeric_value)
            
            
            layout = go.Layout(
                                title = self.fig_color_fmt['title'],
                                xaxis = {'title': 'Time(ms)', 'gridcolor': 'rgb(255,255,255)'},
                                yaxis = {'title': 'Voltage (V)', 'gridcolor': 'rgb(255,255,255)'},
                                plot_bgcolor = 'rgb(200,200,200)'
                                )
            
            fig_data_list = []
            output_table_data = []
            
            
            if self.start_button_clicks < n_clicks:
                
                self.start_button_clicks = n_clicks
                
                if mode_value == 'rm':
                    self.mcu.collect_long_data() ###
                    self.mcu.save_data()
                
                
                x = self.mcu.time_list
                for c_num, y_arr in enumerate([self.mcu.data_list_c1, self.mcu.data_list_c2, self.mcu.data_list_c3], 1):
                    
                    approx_num = 4
                    
                    if not np.isnan(y_arr[0]):
                        max_val = np.around(y_arr.max(), decimals = approx_num)
                        min_val = np.around(y_arr.min(), decimals = approx_num)
                        FD_val = np.around(y_arr.max()-y_arr.min(), decimals = approx_num)
                        ave_val = np.around(y_arr.mean(), decimals = approx_num)
                        rms_val = np.around(np.sqrt((y_arr**2).sum()/len(y_arr)), decimals = approx_num)
                        std_val = np.around(np.sqrt(((y_arr-ave_val)**2).sum()/len(y_arr)), decimals = approx_num)
                        cv_percentage = np.around(std_val/ave_val*100, decimals = approx_num)
                        outPercentage = np.around(np.sum((y_arr > self.UCL)|(y_arr < self.LCL))/len(y_arr)*100, decimals = approx_num)
                    else:
                        max_val = 'N.A.'
                        min_val = 'N.A.'
                        FD_val = 'N.A.'
                        ave_val = 'N.A.'
                        rms_val = 'N.A.'
                        std_val = 'N.A.'
                        cv_percentage = 'N.A.'
                        outPercentage = 'N.A.'
                    
                    data = go.Scatter(
                            x=x,
                            y=y_arr,
                            name='Channel-%d'%c_num,
                            mode= 'lines',
                            marker = dict(color = self.fig_color_fmt['linecolor'][c_num-1])
                            )
                    
                    
                    fig_data_list += [data]
                    
                    output_table_data += [{'Item': 'Channel-%d'%c_num, 
                                            'Maximum Voltage(V)': max_val, 
                                            'Minimum Voltage(V)':min_val, 
                                            'Full Deviation(V)':FD_val, 
                                            'Average Voltage(V)':ave_val, 
                                            'RMS':rms_val,
                                            'STDEV(V)':std_val,
                                            'CV(%)':cv_percentage,
                                            'OutPercentage%(+ or - 5%)':outPercentage
                                            }]
                    
                    
                
                data_UCL = go.Scatter(
                    x = [0,np.max(x)],
                    y = [self.UCL, self.UCL],
                    mode = "lines",
                    name = "UCL({:.2f}V)".format(self.UCL),
                    marker = dict(color = 'rgb(255,0,0)'),
                    line = dict(dash = 'dash')
                    )
                    
                data_LCL = go.Scatter(
                        x = [0,np.max(x)],
                        y = [self.LCL, self.LCL],
                        mode = "lines",
                        name = "LCL({:.2f}V)".format(self.LCL),
                        marker = dict(color = 'rgb(0,255,0)'),
                        line = dict(dash = 'dash')
                        )
                
                fig_data_list += [data_UCL , data_LCL]
                        
                output_fig = {'data': fig_data_list,'layout' : layout}
                
            else:
                       
                data = go.Scatter(
                    x = [],
                    y = [],
                    mode = "lines",
                    name = "Data"
                    )
            
            
                output_fig = {'data': [data],'layout' : layout}
                output_table_data = self.data_table_fmt['data']
            
            
            return output_fig, output_table_data, ""
        
        
        @self.app.callback(
              Output('filename-input', 'value'),
              [Input('data-upload', 'filename'),
              Input('data-upload', 'contents'),
              Input('mode-items','value')])
        def plot_diagram_by_upload(filename, contents, mode_value):
            
            # columns = ['time(sec.)','C1_voltage(V)','C1_voltage(V)','C1_voltage(V)']
            if contents != None and mode_value == 'fm':
                try:
                    content_type, content_string = contents.split(',')
                    decoded = base64.b64decode(content_string)
                    
                    if 'csv' in filename:
                        # Assume that the user uploaded a CSV or TXT file
                        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    elif 'xls' in filename:
                        # Assume that the user uploaded an excel file
                        df = pd.read_excel(io.BytesIO(decoded))
                    elif 'txt' or 'tsv' in filename:
                        # Assume that the user upl, delimiter = r'\s+'oaded an excel file
                        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
                    
                    
                    # self.mcu.reset_data()
                    self.mcu.time_list = df.iloc[:,0].values
                    self.mcu.data_list_c1 = df.iloc[:,1].values
                    self.mcu.data_list_c2 = df.iloc[:,2].values
                    self.mcu.data_list_c3 = df.iloc[:,3].values

                    return filename
                    
                except Exception as e:
                    print(e)
                    return 'There was an error processing this file.'
            else:
                return ""
        
        
        
        
        

if __name__ == '__main__':
    
    waveformapp = WaveFormApp()
    waveformapp.app.run_server(port = waveformapp.web_port, host = waveformapp.web_host)
    
    