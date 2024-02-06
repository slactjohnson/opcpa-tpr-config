import yaml

from qtpy.QtWidgets import QGridLayout

from ophyd import EpicsSignal, EpicsSignalRO

from pydm import Display
from pydm.widgets import PyDMLabel, PyDMShellCommand, PyDMPushButton

class App(Display):

    def __init__(self, parent=None, args=None, macros=None):
        print('Start of __init__ for template launcher')
        print(f'args={args}, macros={macros}')

        # Read in config file
        cfg_file = "opcpa-tpr-config/neh_config.yaml" #TODO add argparse, make this an arg

        config = {}
        with open(cfg_file, 'r') as f:
            config = yaml.safe_load(f)
        self.config = config

        print(f'Loaded config {cfg_file}:')
        print(config)

        # Call super after handling args/macros but before doing pyqt stuff
        super().__init__(parent=parent, args=args, macros=macros)

        # Now it is safe to refer to self.ui and access your widget objects
        # It is too late to do any macros processing

        for laser in self.config['lasers']:
            self.setup_laser(laser)
            self.setup_configs(laser)

        print('End of __init__ for template launcher')

    def ui_filename(self):
        return 'opcpa-tpr-config.ui'
  
    def setup_configs(self, laser):
        grid = self.findChild(QGridLayout, f"{laser}_config_layout") 
        if grid is not None:
            las = self.config['lasers'][laser]
            for ncfg, cfg in enumerate(self.config[las]['configs']):
                button = PyDMPushButton(f'{laser}_{cfg}')
                rate = self.config[las]['configs'][cfg]['rate']
                button.setText(f'{rate}')
                row, col = divmod(ncfg, 4)
                row += 1 # Leave first row for title
                grid.addWidget(button, row, col)

    def configure_laser(self, laser, cfg):
        las_conf = self.config[laser]
        trig_conf = self.config[laser]['configs'][cfg]
        

    def setup_laser(self, laser):
        las = self.config['lasers'][laser]
        if las is not None:
            las_conf = self.config[las]
            child = self.findChild(PyDMLabel, '{laser}_desc')
            if child is not None:
                child.setText(las_conf['laser_desc'])
            tpr_prefix = las_conf['tpr_prefix']
            labels = ['DESC', 'RATE', 'RATEMODE', 'SEQCODE']
            for channel in las_conf['channels']:
                for label in labels:
                    child = self.findChild(PyDMLabel, f'{laser}_{channel}_{label}')
                    if child is not None:
                        if label == 'DESC':
                            val = las_conf['channels'][f'{channel}']['desc']
                            child.setText(val)
                        else:
                            tpr_ch = las_conf['channels'][f'{channel}']['ch']
                            child.set_channel(f'ca://{tpr_prefix}:{tpr_ch}_{label}')
        else:
            print("Laser {} not found!".format(laser))
