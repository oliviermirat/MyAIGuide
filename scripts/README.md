# Analyzing data

First you will need to download the confidential data. To do that, navigate to the folder data/external/ and type: <br/>
git clone https://github.com/oliviermirat/myaiguideconfidentialdata<br/>
This will download the folder myaiguideconfidentialdata into the folder data/external/<br/>
Note that this is a private repo, so you will need special permission to access it.<br/><br/>

Then, before you start analyzing the data, you will need to generate preprocessed data. You can generate this preprocessed data for each participant by launching the scripts: 1_createDataFrameParticipant_\*.py. This preprocessed data will be saved inside the folder data/preprocessed/.<br/><br/>

Once the preprocessed data has been generated, you can start analyzing data. The scripts 2_participant\*PlotData\*.py show how to plot this preprocessed data.<br/><br/>

The script 3_gatherMostImportantPreprocessedDataParticipant1.py further preprocesses the data of Participant 1 and saves that further preprocessed data into the folder data/preprocessed/. The script 4_plotMostImportantDataParticipant1.py then plots this further preprocessed data, and the script 5_exploreDataParticipant1.py plots the graphs shown at the beginning of the <a href='../reports/README.md' target='_blank'>first analysis</a>.<br/><br/>

Finally, the notebook 4_vectorAutoRegressionParticipant1.ipynb was used for the <a href="../reports/vectorAutoregressionAnalysisForParticipant1.pdf" target="_blank">VAR analysis</a>.
