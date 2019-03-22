# OM experiments
I've been experiencing muscle and joint pain since 2009. Since December 2015, I've been following:<br/>
<br/>
-the intensity of pain in different body regions<br/>
-the number of steps and calories I burn every day (with a fitbit)<br/>
-the physical activities I do<br/>
-the time I spend on my computer (with a software called ManicTime)<br/>
-the number of key press and mouse clicks I make (with a software called WhatPulse)<br/>
-and more<br/>

The main objective is to create an algorithm that takes as an input the activities and pain intensities recorded up to a certain day and gives as an output a recommendation about what activities should be performed or avoided on that given day (to avoid having symptoms increase). The validity of this algorithm should be access by using the symptoms recorded for that day.

From personal experience it seems very likely that the intensity of symptoms and the activities performed are correlated. As shown below, simple visualizations of the data collected seems to confirm that hypothesis.

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/firstExperimentsAndCode/images/elbow.png?raw=true "Per Day")
Possible correlation between the number of clicks made on a computer (whatPulseT), various physical activities (surfing, swimming, climbing) and elbow pain.

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/firstExperimentsAndCode/images/foreheadEyes.png?raw=true "Per Day")
Possible correlation between the time spent on the computer (manicTimeT), the time spent doing various activities "stressing" the eyes and forehead and eyes pain.

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/firstExperimentsAndCode/images/handsFingers.png?raw=true "Per Day")
Possible correlation between the number of clicks made on a computer (whatPulseT), various sports (surfing, swimming, climbing) and hands and fingers pain.

![Alt text](https://github.com/oliviermirat/OptimizeUs/blob/master/firstExperimentsAndCode/images/knees.png?raw=true "Per Day")
Possible correlation between the number of steps taken, denivalation and knee pain.

For more details, you can also look at the <a href='OM_old2017experiments/README.md' target='_blank'>previous analysis performed for 2016 and 2017</a>
