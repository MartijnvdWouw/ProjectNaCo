from pathlib import Path
from typing import List, Self
import json
import subprocess

class JSExperimentPaths:
    BASE = Path('./exp1.js')
    SINGLE_CH = Path('./exp2.js')
    DOUBLE_CH = Path('./exp4.js')

class ConfigBuilder:
    GRID_WIDTH = 86
    GRID_HEIGHT = 86
    NUMBER_OF_STEPS = 6001

    BASE_CONFIG=\
    {
        'ndim' : 2,
        'field_size' : [GRID_WIDTH,GRID_HEIGHT],
        'globals': {
            'init_chemokine': 100,
            'poop_factor': 0.7,
            'dissipation_factor': 0.99,
            'max_eat': 8,
            'lambda_chemokine': [[0,100], [0,100]],
            'chemokine_stop_time': -1,
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
            'IMGFRAMERATE' : 100,					        # If so, do this every <IMGFRAMERATE> MCS.
            'SAVEPATH' : "img/base",				# ... And save the image in this folder.
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
    
    def with_chemokine_stop_time(self, time: int) -> Self:
        self.config['globals']['chemokine_stop_time'] = time
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
    
    def build_and_save(self) -> Self:
        self.config_folder.mkdir(exist_ok=True, parents=True)
        filepath = self.get_full_path()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f)

        return self

    def get_full_path(self) -> Path:
        return self.config_folder.joinpath(self.config_name)

class Experiment:
    def __init__(self):
        self.config_path = None
        self.js_path = None
        self.output_file = None
        self.process = None

    def with_config_path(self, config_path: Path) -> Self:
        self.config_path = config_path
        return self
    
    def with_js_path(self, js_path: Path) -> Self:
        self.js_path = js_path
        return self
    
    def with_output_file(self, output_file: Path) -> Self:
        self.output_file = output_file
        return self
    
    def validate(self) -> None:
        if (self.config_path is None) or (self.js_path is None) or (self.output_file is None):
            raise AssertionError("Not everything is correctly set. Nothing can be None!")
        
    def spawn(self) -> None:
        self.validate()

        self.process = subprocess.Popen(
            ['node', self.js_path.resolve(), self.config_path.resolve()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    def get_name(self) -> str:
        return self.output_file.name

class Pool:
    def __init__(self):
        self.experiments: List[Experiment] = []

    def add(self, experiment: Experiment) -> None:
        self.experiments.append(experiment)

    def spawn_all(self) -> None:
        for e in self.experiments:
            e.spawn()

    def await_all(self):
        for e in self.experiments:
            stdout, stderr = e.process.communicate()
            print(f"{e.get_name()} finished{'' if stderr == '' else ' with error ' + stderr}")
            
            e.output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(e.output_file, 'w', encoding='utf-8') as f:
                f.write(stdout)


# Example useage.
# 1. Use the configbuilder to change the values from the default config 
#    (Do not forget to call build_and_save() otherwise the config is not available to the js script)
# 2. Use experiment class to define the experiment
# 3. Add all experiments to a Pool object
# 4. pool.spawn_all() to start all experiments
# 5. pool.await_all() to capture all experiment data

def createBlueExp():
    pool = Pool()
    for seed in [1, 2, 3]:
        for eat in [6, 7, 8, 9, 10]:
            for lambda_ch in [50, 100, 150]:
                conf = ConfigBuilder().with_seed(seed).with_max_eat(eat).with_lambda_chemokine([[0, lambda_ch]]).with_savepath("img/blue")
                name = f"blue_s{seed}_e{eat}_l{lambda_ch}"
                conf = conf.with_config_name(Path(f"conf_{name}.json")).with_expname(name).build_and_save()
                experiment = Experiment().with_config_path(conf.get_full_path()).with_js_path(JSExperimentPaths.SINGLE_CH)
                experiment = experiment.with_output_file(Path(f"results/blue/exp_{name}.txt"))
                pool.add(experiment)

    return pool

def createRedExp():
    pool = Pool()
    for seed in [1, 2, 3]:
        for eat in [8]: #ervan uitgaande dat we dit kunnen fixen
            for lambda_ch in [100]: #ervan uitgaande dat we dit kunnen fixen
                for prod in [0.2, 0.4, 0.6, 0.8, 1]:
                    for diss in [0.985, 0.99, 0.995]:
                        for lambda_ch2 in [50, 100, 150]: # eventueel ook 75 en 125?

                            conf = ConfigBuilder().with_seed(seed).with_max_eat(eat).with_lambda_chemokine([[0, lambda_ch], [0, lambda_ch2]]).with_savepath("img/red")
                            name = f"red_s{seed}_e{eat}_l{lambda_ch}:{lambda_ch2}_p{prod}_d{diss}"
                            conf = conf.with_config_name(Path(f"conf_{name}.json")).with_expname(name).build_and_save()
                            experiment = Experiment().with_config_path(conf.get_full_path()).with_js_path(JSExperimentPaths.DOUBLE_CH)
                            experiment = experiment.with_output_file(Path(f"results/red/exp_{name}.txt"))
                            pool.add(experiment)

    return pool

# baseConf = ConfigBuilder().with_config_name(Path('base_config.json')).build_and_save()
# e2 = Experiment().with_config_path(baseConf.get_full_path()).with_js_path(JSExperimentPaths.SINGLE_CH).with_output_file(Path('aa.txt'))
# e4 = Experiment().with_config_path(baseConf.get_full_path()).with_js_path(JSExperimentPaths.DOUBLE_CH).with_output_file(Path('aa2.txt'))
 
base1Conf = ConfigBuilder().with_config_name(Path('base_config1.json')).with_seed(1).with_savepath("img/base/seed1").with_expname("Base").build_and_save()
base2Conf = ConfigBuilder().with_config_name(Path('base_config2.json')).with_seed(2).with_savepath("img/base/seed2").with_expname("Base").build_and_save()
base3Conf = ConfigBuilder().with_config_name(Path('base_config3.json')).with_seed(3).with_savepath("img/base/seed3").with_expname("Base").build_and_save()
#e4 = Experiment().with_config_path(baseConf.get_full_path()).with_js_path(JSExperimentPaths.SINGLE_CH).with_output_file(Path('aa.txt'))
#e5 = Experiment().with_config_path(baseConf.get_full_path()).with_js_path(JSExperimentPaths.DOUBLE_CH).with_output_file(Path('aa2.txt'))

e1 = Experiment().with_config_path(base1Conf.get_full_path()).with_js_path(JSExperimentPaths.BASE).with_output_file(Path('base1.txt'))
e2 = Experiment().with_config_path(base2Conf.get_full_path()).with_js_path(JSExperimentPaths.BASE).with_output_file(Path('base2.txt'))
e3 = Experiment().with_config_path(base3Conf.get_full_path()).with_js_path(JSExperimentPaths.BASE).with_output_file(Path('base3.txt'))

pool = Pool()
pool.add(e1)
pool.add(e2)
pool.add(e3)


# pool.spawn_all()
# pool.await_all()
# p = createBlueExp()
# p.spawn_all()
# p.await_all()
