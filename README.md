# MyAIGuide

Our aim is to create AI-based health coaches.<br/>

Here is the <a href='./data/raw/ParticipantData' target='_blank'>open-sourced data</a> gathered through <a href='https://youtu.be/mJe5T_oIfUM' target='_blank'>our web application</a>. 

We used <a href='https://medium.com/@oliviermirat/crowdsourcing-health-research-a-new-chance-for-patients-and-tech-people-8658ae298254' target='_blank'>crowdsourcing</a> to investigate the difficult yet very important problem faced by patients with patellofemoral pain syndrome and other chronic pain syndromes of <a href='https://www.painscience.com/articles/art-of-rest.php' target='_blank'>finding the right balance between rest and exercise</a>.

We are currently finishing up a first publication that presents the correlations we have found between exercise and pain and that lays out the groundwork for the creation of an AI in the future.<br/>

If you are interested in helping us finish our first publication, further analyze the data, improve the web application, or for any other information, please feel free to email us at: <br/>

olivier.mirat.om@gmail.com <br/>

You can read our previous analysis of the data here: <a href='./reports/README.md' target='_blank'>old analysis</a>, and see the scripts we've used <a href='./scripts/' target='_blank'>here</a>.<br/>

## Project Organization

```
├── AUTHORS.rst             <- List of developers and maintainers.
├── CHANGELOG.rst           <- Changelog to keep track of new features and fixes.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yaml        <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- Use `python setup.py develop` to install for development or
|                              or create a distribution with `python setup.py bdist_wheel`.
├── src
│   └── MyAIGuide           <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `py.test`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```