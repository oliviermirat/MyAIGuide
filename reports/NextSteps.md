<H1 CLASS="western" style="text-align:center;">MyAIGuide: Data analysis next steps</H1>

<br/><br/>

<H2 CLASS="western">Abstract</H2>
For patients suffering from patellofemoral pain syndrome, finding the right balance between rest and exercise is a difficult yet very important problem. In order to help patients optimize their recovery and/or pain management, we aim to create personalized AI recommendations systems to help them make better choices regarding the amount of rest and exercise they get. We will also investigate the role played by other factors such as stress levels, mood or sleep and give recommendations about those factors as well.
More generally, this project is a first step towards the creation of personal health recommendations systems based on AI to help patients with any kind of disease.

<br/><br/>

<H2 CLASS="western">Introduction</H2>

<H4 CLASS="western">MyAIGuide's website</H4>
The MyAiGuide website (myaiguide.com) was created in 2017 with the aim of collecting data about pain and exercise from patients with patellofemoral pain syndrome. The MyAIGuide web application now also allows users to collect data about their stress levels, mood, sleep, and an unrestricted amount of other variables; enabling the exploration of other forms of chronic pain going forward. The data collected through this website as well as some personal health data collected by the founder of the website is being open-sourced: https://github.com/oliviermirat/MyAiGuide.

<H4 CLASS="western">Recent Work</H4>
A Correlaid team has already been working on this project from March 2020 until October 2020. The team created scripts to extract data from raw data files, to clean the data and to store it in a convenient data structure. The team also started to analyze the data and a report of this initial analysis is available here: https://github.com/oliviermirat/MyAIGuide/blob/master/reports/README.md . We now want to go a step further in the analysis and we aim to explore the feasibility of creating health recommendation systems (“AI coaches”) to help chronic pain patients in their daily lives.

<H4 CLASS="western">Data available</H4>
Data is currently available for ~10 participants, ranging from three weeks worth of data up to 4 years worth of data.

<br/><br/>

<H2 CLASS="western">Overall aim</H2>
<p>
The aim of this project is to create a model that can, for a given Participant, take as an input all of the data recorded up to the day n (excluding the pain levels) and predict, for the day n, one of the following pieces of information:<br/>
- the pain levels<br/>
- whether or not the subject’s pain levels will go above a certain “acceptable threshold”<br/>
- if the pain level decreases, increases or stays the same.<br/><br/>
If we don’t manage to create a system that gives daily recommendations, we will investigate the feasibility of creating a system that would give weekly recommendations.
</p>

<br/><br/>

<H2 CLASS="western">General ideas</H2>
<H4 CLASS="western">Data preparation and feature engineering</H4>
In order to create this model, different approaches will need to be considered, and potentially combined. One difficulty will be to find the best set of “engineered” parameters to feed to the model. Indeed, feeding raw data to the model will most likely lead to suboptimal results, whereas finding clever ways of deriving “engineered” parameters from the raw data will most likely lead to better results. Using the intuition of participants regarding what most influences their pain could serve as a starting point to find the best set of parameters.
We will also need to find a good way of dealing with scales, noise and missing values.

<H4 CLASS="western">Model choice</H4>
Another difficulty will be to find the best model. We’ve already started working with Vector Autoregression and we plan to push that approach further. Machine learning algorithms should definitely be tested too, with LSTM and RNN being prime candidates. Other options that might fit better the underlying biological mechanisms could also be considered. For instance, we could try to build a model composed of two distinct sub-models. The first sub-model would represent the current “trauma” that a body region (eg. knees) is in: this model would take as inputs factors related to physical activity and other sources of stress on that body region. The second model would represent how much of that “trauma” actually converts to perceived pain in the brain. This second model could take many different parameters as inputs, such as the presence of pain in other body regions, stress levels, general mood, sleep, etc…

<H4 CLASS="western">Communicating with participants</H4>
Finally, we have the ability to get in touch and talk with the people who recorded the data (and one of them is the founder of the project). Therefore, if and when the model outputs predictions that do not correspond to reality, we would have the option to contact participants and ask if there’s anything that happened around that time that could explain the discrepancy (this could be for instance: if the participant forgot to wear his tracker at that time, if the participant was going to a very good/bad time at that time, if the participant moved to another city/country around that time, etc…). This could lead to new insights regarding whether or not new parameters should be tracked going forward, and if so which ones.

<br/><br/>

<H2 CLASS="western">Practical next steps ideas overview:</H2>

<H4 CLASS="western">Creating individualized models first</H4>
In the future, it would be great to use the data of multiple participants to generate a prediction model for a single participant. However, as a first step, it would probably be best to create a model for a participant based only on the data of that participant.

<H4 CLASS="western">How to split the training and testing dataset?</H4>
An important question is going to be how to split the data into training and testing datasets. The safest most conservative method would be to use all of the data recorded up to the day n (excluding the pain levels) and predict pain levels for the day n (this means that predictions could start only after a few days).<br/>
But alternative options could also be considered if appropriate: for example, one idea could be to use all of the data recorded up to the day n as well as all the data recorded after the day n + X (X being a very large number, for example maybe 90 (which would be 3 months)).

<H4 CLASS="western">Continuous training</H4>
Another important question will be how to update the model over time. The most precise (but also time consuming option) would be to retrain the model for every new day. If that's too time consuming, the alternative would be to find a tradeoff between retraining often and model accuracy.<br/>
Another question will be how to best use the training data to train the model: indeed if trying to do a prediction in 2019, the data collected in 2018 might be more relevant than the data collected in 2016. This should probably be taken into account when training models.

<H4 CLASS="western">Normalizing variables over long periods of time</H4>
As seen for example on the figure of the <a href='README.md' target='_blank'>first analysis</a>, pain levels for Participant1 in 2016 were much higher than in, for example, 2018. It will thus be necessary to find a way of normalizing pain levels across time, for the data of 2016 to be used to train a model that will then be used to predict pain levels for the data of 2018. Although not as obvious, the same kind of issue probably also exists for the stress variable, and a solution will be needed for that as well.<br/>

<H4 CLASS="western">Which participant should we first focus on?</H4>
Participants 1, 2 and 8 have the most data, we should therefore first try to create 3 individualized models for those 3 participants (one for each participant). We can look into the data of other participants afterwards.

<H5 CLASS="western">Participant 1</H5>
For this participant, it seems like the stressors related to the knee pain provide the most accurate representation of the stress applied on a body part (better than the stressor related to fingerHandArm pain and foreheadEye pain). It could therefore be a good idea to focus more on the knee pain than on the fingerHandArm pain and foreheadEye pain first.

<H5 CLASS="western">Participant 2</H5>
This participant has less sources of data than Participant 1, but we should take steps similar to those of Participant 1 to build a model for this participant.

<H5 CLASS="western">Participant 8</H5>
The cause of pain for this participant might be more related to psychological factors.

<H5 CLASS="western">Participant 3, 4, 5, 6, 7, 9</H5>
Much less data is available for these participants. It would thus probably be best to focus on Participant 1, 2 and 8 first to try to generate hypotheses about the accuracy of the models that can be generated. Afterwards, we could look at the data of participants 3, 4, 5, 6, 7, 9 to see if we can see signs that models with accuracies similar to previous ones could be generated for those participants.

<H4 CLASS="western">Conclusion</H4>
The best practical first steps will most likely be to focus on building personalized prediction models for Participant 1, 2 and 8. It will most likely also be crutical to focus on finding the best set of engineered parameters to feed to the model. Once a good set of engineered features has been found, we can then try to choose the most relevant ML algorithm.
