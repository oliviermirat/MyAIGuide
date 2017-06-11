# OM experiments
Since December 2015, I've been following:<br/>
<br/>
-the intensity of pain I feel in different regions of my body<br/>
-the number of steps and calories I burn every day (with a fitness tracker called Basis Peak)<br/>
-the physical activities I do<br/>
-the time I spend on my computer (with a software called ManicTime)<br/>
-the number of key press and mouse clicks I make (with a software called WhatPulse)<br/>
-and more<br/>

Here's a summary for 2016:

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/OM/5_documentation/images/summary2016.png?raw=true "Per Day")

The aim is to try to figure out if the pain intensity is somehow correlated with the other variables (physical and daily activities). These other variables will be called environmental variables in the following.<br/>
So far I've tried to make linear combinations of environmental variables and see how they correlate with symptoms.<br/>
Here's an example for the knees:

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/OM/5_documentation/images/knees2016.png?raw=truoe "Per Day")

So far, this analysis is inconclusive, but feel free to play with the data!<br/><br/>
Don't hesitate to contact me if you have any questions.
<br/><br/>
<h3>To Do:</h3>
The code works well and the data is valid, but there are still a lot of improvements left to be made:

<h4>Data Extraction</h4>
-ManicTime doesn't only log the hours where a computer is on, off and locked, it also logs the application used. These logs should be taken into account (for example, I have an application that turns off the screen...).<br/>
-BasisPeak went out of business at the end of 2016. So since September of 2016, I also started using a FitBit. However, I haven't implemented the solution to extract my data from FitBit yet. And the data from Basis Peak and Fitbit will need to be normalized.<br/>
-There are many other variables I'm tracking manually (in spreadsheets) that would need to be extracted and added to the database.<br/>

<h4>Data Enhancement</h4>
A very small portion of the data from the basis peak has been lost due to various syncing issues. It's usually just a few hours of data here and there, around the following days:<br/>
-March 28<br/>
-April 21<br/>
-August 24<br/>
-October 11<br/>
-October 25<br/>
For now, this problem has been fixed by removing the physical activities performed on those days from the database. Ideally, some "basis peak data" should be cleverly added to the database on those days instead.

<h4>Data Analysis</h4>
-Prove or disprove a correlation between environmental variables and symptoms.<br/>
-If a correlation is found, implement an AI-based recommendation system regarding activities to do or avoid on a given day.
