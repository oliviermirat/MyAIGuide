# OM experiments
I've been experiencing muscle and joint pain since 2009. Since December 2015, I've been following:<br/>
<br/>
-the intensity of pain in different body regions<br/>
-the number of steps and calories I burn every day (with a fitness tracker called Basis Peak)<br/>
-the physical activities I do<br/>
-the time I spend on my computer (with a software called ManicTime)<br/>
-the number of key press and mouse clicks I make (with a software called WhatPulse)<br/>
-and more<br/>

Here's a summary for 2016:

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/OM/5_documentation/images/summary2016.png?raw=true "Per Day")

The aim is to try to figure out if the pain intensity is somehow correlated with the other variables (physical and daily activities). These other variables will be called environmental variables in the following. My intuition is that a correlation between symptoms and environmental variables does exist, however this correlation is unproven.<br/>
So far I've tried to make linear combinations of environmental variables and see how they correlate with symptoms.<br/>
Here's an example for the knees:

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/OM/5_documentation/images/knees2016.png?raw=true "Per Day")

So far, this analysis is inconclusive, but feel free to play with the data and don't hesitate to contact me if you have any questions.
<br/><br/>
<h3>To Do:</h3>
The code works well and the data is valid, but there are still a lot of improvements left to be made:

<h4>Data Extraction</h4>
-ManicTime doesn't only log the hours where a computer is on, off and locked, it also logs the application used. These logs should be taken into account (for example, I have an application that turns off the screen...).<br/>
-BasisPeak went out of business at the end of 2016. So since September of 2016, I also started using a FitBit. However, I haven't implemented the solution to extract my data from FitBit yet. And the data from Basis Peak and Fitbit will need to be normalized.<br/>
-Extract data from gps files: this could be useful to better quantify physical activities.<br/>
-There are many other variables I'm tracking manually (in spreadsheets) that would need to be extracted and added to the database.<br/>

<h4>Data Enhancement</h4>
A very small portion of the data from the basis peak has been lost due to various syncing issues. It's usually just a few hours of data here and there. The problems are around the following days:<br/>
-March 28<br/>
-April 21<br/>
-August 24<br/>
-October 11<br/>
-October 25<br/>
For now, this problem has been fixed by removing the physical activities performed on those days from the database. Ideally, some "basis peak data" should be cleverly added to the database on those days instead.

<h4>Data Analysis</h4>
-Prove or disprove a correlation between environmental variables and symptoms.<br/>
-If a correlation is found, implement an AI-based recommendation system regarding activities to do or avoid on a given day.

<h4>Pain Quantification</h4>
Because of its subjective nature, the quantification of pain is complex.
So far, I've estimated (every evening) an average pain intensity for each body region over the the 6 worst hours of the day, using the following scale:<br/>
<2         : almost imperceivable most of the time<br/>
2   to 2.9 : not too bad, but can still "feel" it<br/>
3   to 3.4 : uncomfortable (3.4 is seriously uncomfortable)<br/>
3.5 to 3.9 : very uncomfortable almost painfull<br/>
4.0 to 5.0 : painfull<br/>
greater than 5.0 : very painfull<br/>
<br/>
The adjective "uncomfortable" might not seem really "bad", but over long periods of time, it can actually be a pretty serious problem, limiting physical activities and other kind of activities.<br/><br/>
This quantification method has the advantage of being easy to implement, non-invasive (it takes 1 min per day), and fairly precise, but there are probably still ways of improving this quantification method.
