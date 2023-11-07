import PySimpleGUI as sg
import threading
import numpy as np
from datetime import datetime
import time

class SmoothTransition:

    def __init__(self, connectedMFC):

        self.connectedMFC = connectedMFC

        self.layout = [
            sg.Frame("Transizione lineare", [[ sg.Column([
                [sg.Frame("MFC", [[sg.Column([], key="st:col")]])],
                [sg.Text("Durata [s]: "), sg.Input("30", key="st:duration")],
                [
                    sg.Button("Start", key="st:start"),
                    sg.Button("Abort", key="st:abort", disabled=True)],
                [sg.ProgressBar(100, orientation='h', size=(
                    40, 10), key='st:progress')],
            ]),
        ]] ) ]

        self.toUpdate = True
        self.running = False

    # def loop( self ):
    #     print("Loop thread")
    #     while True:
    #         event, values = self.window.read(timeout=100)

    #         if( event == 'sg:refresh' ):
    #             self.refreshMFC()

    #         print(event)

    def parse_events(self, event, values, window):

        if( event == "st:start" ):
            self.start_transition( window, values )
        
        if( event == "st:abort" ):
            self.running = False
            self.toUpdate = True

        pass

    def update_window( self, window ):
        if( self.toUpdate ):
            self.toUpdate = False

            window['st:abort'].update( disabled=not self.running )
            window['st:start'].update( disabled=self.running )
            window['st:progress'].update( current_count=self.i, max_value = self.steps )

    def addMFC(self, MFC, window):
        window.extend_layout(window['st:col'], [[
            sg.Text(f"{MFC.tag} ({MFC.gas}): from "),
            sg.Input(default_text=MFC.get_current_set_value(str=True), key=f"st:{MFC.ID}:from", size=7),
            sg.Text(" to "),
            sg.Input(default_text=MFC.get_current_set_value(str=True), key=f"st:{MFC.ID}:to", size=7),
        ]])

    def parse_value( value, MFC ):
        try:
            output = float( value )
            if (setpoint > MFC.max):
                setpoint = MFC.max
            if (setpoint < MFC.min):
                setpoint = MFC.min
            return output
        except ValueError:
            return MFC.min


    def start_transition(self, window, values):

        try:
            duration = int( values['st:duration'] )
        except ValueError:
            duration = 30
        window['st:duration'].update( duration )
        self.steps = duration

        self.ranges = []

        for MFC in self.connectedMFC:

            start = self.parse_value( values[f"st:{MFC.ID}:from"], MFC )
            window['st:{MFC.ID}:from'].update( f"{start:.2f}" )
            
            finish = self.parse_value( values[f"st:{MFC.ID}:to"], MFC )
            window['st:{MFC.ID}:to'].update( f"{finish:.2f}" )

            self.ranges[ MFC.ID ] = np.linspace( start, finish, self.steps )

        self.running = True
        self.thread = threading.Thread( target=self.transition )
        self.thread.start()

    def transition( self ):
        self.i = 0
        next_transition = datetime.now().timestamp()

        while self.running:
            self.toUpdate = True

            while( datetime.now().timestamp() < next_transition ):
                time.sleep( 0.05 )

            for MFC in self.connectedMFC:

                if( self.i > len( self.ranges[ MFC.ID ] ) ):
                    self.running = False
                    return
                
                MFC.set_current_set_value( self.ranges[ MFC.ID ][ self.i ] )

            self.i = self.i + 1
            next_transition = next_transition + 1

