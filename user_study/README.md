# <a name='Eval'></a>Evaluation of Ruler
We evaluated Ruler alongside manual data programming using [Snorkel](https://www.snorkel.org/). 

Although non-programmer domain experts are a target audience for this technology, we wanted our evaluation to show that the Ruler labeling language is expressive enough to create models comparable to manual data programming. 
We also wanted to understand the trade-offs afforded by each method in order to help programming-proficient users decide which  is best for their situation. 
In order to make these comparisons, we conducted a user study with 10 programming-proficient data scientists and measured their task performance accuracy in completing two labeling tasks using the two methods. 
In addition to task performance, we analyzed both accessibility and expressivity using the qualitative feedback elicited from participants. 

We asked participants to write  labeling functions for two prevalent labeling tasks: spam detection and sentiment classification. Each user completed both tasks using different methods, for a within-subjects experimental design. 
The pairing of task/tool, as well as the order in which tasks were completed, were counterbalanced. 
Each session included a 15 minute tutorial on the tool, followed by 30 minutes to create as many functions as they considered necessary for the goal of the task.

<h3> 
 The data from our user study is available in this folder, along with <a href=https://github.com/megagonlabs/ruler/blob/main/user_study/ruler_user_study_figures.ipynb>the code to generate all of the figures</a> included in our <a href=https://github.com/megagonlabs/ruler/blob/main/media/Ruler_EMNLP2020.pdf>Findings of EMNLP paper</a>. 
</h3>

All participants had significant programming experience (avg=12.1 years, std=6.5). 
Their experience with Python ranged from 2 to 10 years with an average of 5.2 years (std=2.8).  

We find that Ruler and Snorkel provide comparable model performances (see figure below). 
The logistic regression models trained on data produced by labeling models created using Ruler have slightly higher f1 (W=35, p=0.49, r=0.24 ), precision (W=30, p=0.85, r=0.08), and recall (W=25, p=0.85, r=0.08) scores on average. 
Conversely, accuracy is slightly higher (W=17, p=0.32, r=0.15) for Snorkel models on average than Ruler. 
However these differences are not statistically significant. 

<h3 align="center">
<img width=800px src=../media/quantitative.png>
<br />  Ruler and Snorkel provide comparable model performances
</h3>


Participants find Ruler to be significantly easier to use 
(W=34, p=0.03 < 0.05, r=0.72) than Snorkel. 
Similarly, they consider Ruler easier to learn (W=30, p=0.1, r=0.59) than Snorkel.  
On the other hand, as we expected, participants report Snorkel to be more expressive (W=0, p=0.05, r=0.70)  than  Ruler. 
However, our participants appear to consider accessibility (ease of use and ease of learning) to be more important criteria, rating Ruler higher (W=43, p=0.12, r=0.51) than Snorkel for overall satisfaction.  


<h3 align="center">
<img width=800px src=../media/qualitative.png>
<br/>Participants' subjective ratings on ease of use, expressivity, ease of learning and overall satisfaction, on a 5-point Likert scale. 
</h3>

Please see our [EMNLP'20 submission](https://github.com/megagonlabs/ruler/blob/main/media/Ruler_EMNLP2020.pdf) for more details. 
