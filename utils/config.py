import os

class Config:
    def __init__(self):
        self.QXToken = os.getenv('QXToken', 'YOUR_IBM_TOKEN')
        self.SIMULATION = os.getenv('SIMULATION', 'False')
