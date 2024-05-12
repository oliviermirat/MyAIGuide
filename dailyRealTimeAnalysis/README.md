# Summary of previous results + First body region loading prototype app

## Previous results
### Strain and pain correlations

In our first <a href='https://www.researchgate.net/publication/368539250_Big_personal_data_points_to_physical_strain_causing_pain_in_the_short_and_long_term_in_some_chronic_pain_patients' target='_blank'>February 2023 ResearchGate paper</a> we showed correlations between exercise and knee pain in much finer detail than what had been previously reported by others. To do so, we used big data (at the patient level) collected in 3 patients with chronic knee pain on a daily basis for several years. 

![alt text](https://myaiguide.org/image/figure1.svg "Figure1")

Using several successive filters (including a rolling mean filter), we showed that exercise increases seemed to always precede pain increases but that as shown in the figure above, the delay between exercise peaks and pain peaks could vary. These long delays might be explained by periods of exercise “build-ups” that only impact pain levels later on. These long delays also illustrate the difficulty for chronic pain patients to “choose” the amount of exercise they should do, as the indication to slow down exercising in terms of pain increase can often occur later on, when it's already too late.

### Fast strain increases associated with poor outcomes

In a <a href='https://www.researchgate.net/publication/376042881_Creating_personalized_digital_health_coaches_to_help_chronic_knee_pain_patients_find_the_right_exercise_dosage_a_proof_of_concept_study' target='_blank'>second study</a>, we showed that if defining “warning signs” as time points when exercise increased faster than a predefined threshold, then the longer it has been since a warning sign occurred, the higher the likelihood that pain will not go into big increases (see figure below).

![alt text](https://myaiguide.org/image/figure2.svg "Figure2")

This shows how stagnant or slowly increasing strain will typically result in better outcomes (less pain) than fast increasing strain.

### Need to build a strain guidance app

We thus conclude from our two previous studies as well as from our literature review in the introduction of our first ResearchGate paper that overuse chronic pain patients should generally aim for slowly increasing levels of physical strain. But given the difficulty associated with this pursuit, we also conclude that building an app to help keep track of physical strain levels is needed.

## Exercise loading prototype apps summary

### First attempt to build strain guidance app: myaiguide web app

My first implementation on <a href='https://myaiguide.org/' target='_blank'>MyAIGuide</a> was easy to use but didn't differentiate the different body regions (and API integrations often break). See <a href='https://www.youtube.com/watch?v=72q0mqrBkV4' target='_blank'>Youtube video</a> of this first implementation.

### Second attempt to build strain guidance app: prototype desktop app

Given the technical complexity and time required to build a mobile app, I decided to start by building a desktop prototype version of this app that could only be used by experienced Python programmers. The advantage of building such a desktop app is that it was much easier and faster to build than a mobile app and it could allow for easy prototyping / experimenting with various different visualization methods. The implementation is available on <a href='https://github.com/oliviermirat/MyAIGuide/tree/master/dailyRealTimeAnalysis' target='_blank'>Github</a>. So far, as far as I know, I am the only person to have used the app, I've used it for experimentation purposes for about four months now at the time of this writing (May 2024).

#### How the prototype desktop app works

WhatPulse and ManicTime data (computer usage data) must be exported from those two software for each new day for which the user wants to visualize data. Then by launching the scripts provided in the dailyRealTimeAnalysis folder, data from Garmin is retrieved and stored in a local database. The scripts will then plot graphs similar to the one shown below.

![alt text](https://myaiguide.org/image/armsPrototypeApp.svg "armsPrototypeApp")

As seen in the example plot above, the various stressors involved in the pain of a particular body region (the arms in the example above) are shown along with the linear combination of those stressors and the pain. This allows the user to visualize how the overall strain applied to a particular body region (the linear combination of stressors) is evolving over time. It thus allows the user to make sure that the strain isn't increasing too fast, and also that it isn't decreasing either.

#### Subjective experience

From a purely subjective point of view, I have found this prototype app to be very useful and maybe even a bit addictive.

Indeed, the app often helps me make better decisions: for instance, I often wonder if I should go do a specific physical exercise or not, and if I see on the app that I've loaded a body region involved in that physical exercise a lot in the last few days, I will now more confidently skip that physical exercise on that given day. Inversely, if I feel some pain in that body region but the app shows me that I haven't loaded that body region a lot in the past few days, I will now more confidently still engage in that physical exercise despite having a bit of pain (oftentimes, the physical exercise will then actually attenuate the pain). As an analogy, using this app feels a bit similar to using a weather forecast app when planning outdoor activities: if I see that it's likely to rain all week-end, I will be much more likely to go exercise outside on friday evening, whereas if I see that the weather will be great all week-end, I will be more likely to save my energy on friday evening. I never rely entirely on the weather forecast to make decisions, but I often take it into account in my decision making process, at least to some degree: and this is pretty much the same way I've been using my body loading quantification app in the past few months.

Furthermore, I really enjoy being able to access hard data to know the amount of strain I'm putting on various body locations over time. I indeed feel like it helps me visualize my progress over time which provides me with a sense of clarity and gives me more confidence in my daily choices.

#### Quantitative point of view

From a more quantitative point of view, we can also see that since I started using the strain guidance app (towards the end of December 2023), the strain I put on different body regions has become less variable, as shown in the three graphs associated with the three different body regions shown below.

![alt text](https://myaiguide.org/image/befAftJan24KneesFig.svg "befAftJan24KneesFig")

![alt text](https://myaiguide.org/image/befAftJan24ArmsFig.svg "befAftJan24ArmsFig")

![alt text](https://myaiguide.org/image/befAftJan24EyesFig.svg "befAftJan24EyesFig")

The decrease in strain variation observed above was obtained only by checking the prototype app every 4 days on average, it is possible that an even bigger decrease in variability could be observed if the prototype app was being checked every day, or possibly even several times per day.

#### Current limitations

The current version nevertheless does have a few limitations: 
- it takes about five minutes to sync all the data and access the visualization and I would ideally prefer to check the app a few times a day; so a better mobile app would be much more convenient
- although already very useful, the quantification of exercise loading of the different body region is still quite primitive and it would be really great to create some more accurate quantifications

#### Conclusion

Both from a subjective and objective point of view, the following observations, even if collected from only one individual, are nevertheless also strongly in favor of the development of the strain guidance mobile app.
