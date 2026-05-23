from pathlib import Path
from typing import List, Self
import json


class ConfigBuilder:
    GRID_WIDTH = 86
    GRID_HEIGHT = 86
    NUMBER_OF_STEPS = 10001

    BASE_CONFIG=\
    {
        'ndim' : 2,
        'field_size' : [GRID_WIDTH,GRID_HEIGHT],
        'globals': {
            'init_chemokine': 100,
            'poop_factor': 0.7,
            'dissipation_factor': 0.99,
            'max_eat': 8,
            'lambda_chemokine': [[0,100], [0,100]]
        },
        'conf' : {
            'torus': [False, False],
            'seed': 1,
            'D': 0.15,
            'T' : 20,											# CPM temperature
                    
            # Adhesion parameters:
            'J': [[0,0], [0,0]] ,
            
            # VolumeConstraint parameters
            'LAMBDA_V' : [0,50],								# VolumeConstraint importance per cellkind
            'V' : [0,20],									    # Target volume of each cellkind

            'LAMBDA_ACT' : [0, 500],
            'MAX_ACT' : [0, 100],
            'ACT_MEAN' : 'geometric',

            'LAMBDA_P': [0,10],								# PerimeterConstraint importance per cellkind
            'P' : [0,50],										# Target perimeter of each cellkind
        },
        
            # Simulation setup and configuration
        'simsettings' : {
            # Cells on the grid
            'NRCELLS' : [1],								    # Number of cells to seed for all
            # non-background cellkinds.
            # Runtime etc
            'BURNIN' : 0,
            'RUNTIME' : NUMBER_OF_STEPS,
            'RUNTIME_BROWSER' : 100,#"Inf",
            'ACTCOLOR' : [True],
            
            # Visualization
            'zoom' : 4,										# zoom in on canvas with this factor.
            
            # Output images
            'SAVEIMG' : True,									# Should a png image of the grid be saved
            # during the simulation?
            'IMGFRAMERATE' : 1000,					        # If so, do this every <IMGFRAMERATE> MCS.
            'SAVEPATH' : "img",				                # ... And save the image in this folder.
            'EXPNAME' : "Chemotaxis",							# Used for the filename of output images.
            
            # Output stats etc
            'STATSOUT' : { 'browser': False, 'node': True }, 		# Should stats be computed?
            'LOGRATE' : 1  									# Output stats every <LOGRATE> MCS.
        }
    }

    def __init__(self) -> None:
        self.config = self.BASE_CONFIG
        self.config_folder = Path('./configs')
        self.config_name = Path('config.json')

    def with_burnin(self, burnin: int) -> Self:
        self.config['simsettings']['BURNIN'] = burnin
        return self

    def with_seed(self, seed: int) -> Self:
        self.config['conf']['seed'] = seed
        return self
    
    def with_D(self, D: int) -> Self:
        self.config['conf']['D'] = D
        return self
    
    def with_T(self, T: int) -> Self:
        self.config['conf']['T'] = T
        return self
    
    def with_lambda_act(self, lambda_act: List[int]) -> Self:
        self.config['conf']['LAMBDA_ACT'] = lambda_act
        return self
    
    def with_max_act(self, max_act: List[int]) -> Self:
        self.config['conf']['MAX_ACT'] = max_act
        return self
    
    def with_lambda_chemokine(self, lambda_chemokine: List[List[int]]) -> Self:
        '''
            lambda_ch: to configure the lambda for the chemokines. First entry for blue chemokines, second for red.
        '''
        self.config['globals']['lambda_chemokine'] = lambda_chemokine
        return self
    
    def with_init_chemokine(self, init_chemokine: int) -> Self:
        self.config['globals']['init_chemokine'] = init_chemokine
        return self
    
    def with_poop_factor(self, poop_factor: int) -> Self:
        self.config['globals']['poop_factor'] = poop_factor
        return self
    
    def with_dissipation_factor(self, dissipation_factor: int) -> Self:
        self.config['globals']['dissipation_factor'] = dissipation_factor
        return self
    
    def with_max_eat(self, max_eat: int) -> Self:
        self.config['globals']['max_eat'] = max_eat
        return self

    def with_runtime(self, runtime: int) -> Self:
        self.config['simsettings']['RUNTIME'] = runtime
        return self
    
    def with_imgframerate(self, framerate: int) -> Self:
        self.config['simsettings']['IMGFRAMERATE'] = framerate
        return self
    
    def with_savepath(self, savepath: str) -> Self:
        self.config['simsettings']['SAVEPATH'] = savepath
        return self
    
    def with_expname(self, expname: str) -> Self:
        self.config['simsettings']['EXPNAME'] = expname
        return self
    
    def with_lograte(self, lograte: int) -> Self:
        self.config['simsettings']['LOGRATE'] = lograte
        return self

    def with_config_name(self, config_name: Path) -> Self:
        self.config_name = config_name
        return self
    
    def build(self) -> dict:
        return self.config
    
    def build_and_save(self) -> None:
        self.config_folder.mkdir(exist_ok=True, parents=True)
        filepath = self.config_folder.joinpath(self.config_name)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f)


a = ConfigBuilder().with_runtime(1).build_and_save()