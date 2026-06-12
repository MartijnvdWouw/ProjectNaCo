# Setup

This project uses the artistoo implementation as provided in this repository. To install its dependencies do the following (from the project root):

1. `cd artistoo-master`
2. `npm install .`
3. `cd ..`

Furthermore we use the latest version of python (which can be found [here](https://www.python.org/downloads/release/python-3146/)).

Assuming that the `python` command is bound to version 3.14 (you can check this with `python -V`) do the following (from the root of the project!) to install all dependencies: 

1. create a virtual environment: `python -m venv venv`
2. activate the environment: `./venv\Scripts\Activate.ps1` for windows or `source venv/bin/activate` for unix.
3. install dependencies: `python -m pip install -r requirements.txt`

You should be all setup now to run or analyse experiments!

# Run our experiments
To run our experiments, go to `runner.py` and at the bottom change `pool = createRedExp()` to

1. `pool = createBaseExp()` for our baseline experiments
2. `pool = createBlueExp()` for our chemotaxis experiments
3. leave unchanged (`pool = createRedExp()`) for our paracrine signalling experiments
4. `pool = createForceExp()` for our experiments with extra force in the chemotaxis model
5. `pool = createSplitExp()` for one of our experiments with no paracrine signalling after time t. (note that you can change this function for the other experiments).

note that these experiments can take a while.

Afterwards (while in a the virtual environment) run `runner.py` (i.e. `python runner.py`)

# Run own experiments
You can find a script to define and run experiments in `runner.py`. If you want to define your own experiments we highly suggest using this script.

To create an experiment, first we have to create a config:

1. first remove the bottom few lines (a comment indicates what to remove) to avoid clashes with other experiments.
2. add `conf = ConfigBuilder()`
3. change parameters to your liking e.g.:

    `conf = conf.with_seed(2).with_runtime(1000)`

    note that if you change the image save path, make sure to manually create the directory!
4. call build and save: `conf = conf.build_and_save()`

Define the experiment:

1. `exp = Experiment().with_config_path(conf.get_full_path()).with_output_file(Path("./out.txt")).with_js_path(JSExperimentPaths.BASE)`
2. feel free to change the parameters for `with_output_file` and `with_js_path`. Note that the latter defines which experimental setup is used. Either the baseline, chemotaxis or paracrine signalling.

Create the pool manager:

1. `pool = Pool()`
2. add experiments: `pool.add(exp)`
3. spawn processes: `pool.spawn_all()`
4. await processes: `pool.await_all()`

combined it will look something like:

```
conf = ConfigBuilder().with_seed(2).with_runtime(1000).build_and_save()

exp = Experiment().with_config_path(conf.get_full_path()).with_output_file(Path("./out.txt")).with_js_path(JSExperimentPaths.BASE)
pool = Pool()
pool.add(exp)

pool.spawn_all()
pool.await_all()
```

Afterwards (while in a the virtual environment) run `runner.py` (i.e. `python runner.py`)

# Analysis
To use our analysis script please change the following line in the `main` function: `r = read_all_results_group(group(Path("results/blue")))`.

Make sure that it points to the results folder obtained while running your experiments. That might mean that you have to move the .txt output file of your experiment into a temporary directory to be able to use this. e.g. if your output file is located at `./output.txt` move it to a folder `./temp/output.txt`. If you are analysing our experiments changing it to:

1. `r = read_all_results_group(group(Path("results/base")))` will analyse the baseline
2. `r = read_all_results_group(group(Path("results/blue")))` (leave unchanged) will analyse the chemotaxis model
3. `r = read_all_results_group(group(Path("results/red")))` will analyse the paracrine signalling model.
4. `r = read_all_results_group(group(Path("results/force")))` will analyse the chemotaxis experiments with extra force.
5. Note that for the experiments where paracrine signalling is disabled after some time t, analysis was done based on [these](./img/split/) images

# Navigation to our results

## Images
1. [baseline](./img/base/) for the images of all baseline runs
2. [chemotaxis](./img/blue/) for the images of all chemotaxis runs
3. [paracrine signalling](./img/red/) for the images of all paracrine signalling runs
4. [force](./img/force/) for the images of the chemotaxis runs with increased force
5. [split](./img/split/) for the images of the runs where after time t, paracrine signalling was disabled

For all of the above: the file name denotes what configuration settings were used.

## Output files
1. [baseline](./results/base/) for the outputs of all baseline runs
2. [chemotaxis](./results/blue/) for the outputs of all chemotaxis runs
3. [paracrine signalling](./results/red/) for the outputs of all paracrine signalling runs
4. [force](./results/force/) for the outputs of the chemotaxis runs with increased force
5. [split](./results/split/) for the outputs of the runs where after time t, paracrine signalling was disabled

For all of the above: the file name denotes what configuration settings were used.

## Configurations
see [configs](./configs/) for all used configurations.

## Js
If you are interested in the javascript implementations:

1. [baseline](./exp1.js) for the baseline experiments
2. [chemotaxis](./exp2.js) for the chemotaxis experiments
3. [paracrine signalling](./exp4.js) for the paracrine signalling experiments.

Note that these files can not be run individually without passing the path to a configuration manually!

for example: `node ./exp1.js "./configs/config.json"` if there is a config located at `./configs/config.json` should work, but it is best to use `runner.py`.