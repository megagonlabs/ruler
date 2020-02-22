# [ŘULER](http://18.223.190.82:3000/)
 #### Data Programming by Demonstration for Text 
 
 See our [demo video](https://drive.google.com/file/d/1Z3b8wyTKoUX4b5jC8CJM9-DWuF87MwLE/view?usp=sharing) or [try it yourself](http://18.223.190.82:3000/).
 
 <img src=media/ruler_demo_gif.gif>
 
 
This repo contains the source code for Ruler, a system that generates labeling functions from users' annotations of intelligently selected document examples (see our [KDD '20 submission]() for details). 


1. [What is Data Programming by Demonstration? (DPBD)](#DPBD)
2. [Řuler: DPBD for Text](#Ruler)
3. [Experimental Results: Comparing Ruler to other Methods of Generating Labeling Functions](#Experiments)
4. [How to use the source code in this repo](#Use)



## <a name='DPBD'></a>What is Data Programming by Demonstration (DPBD)?
The success of machine learning has dramatically increased the demand for high-quality labeled data, as the models used in practice are predominantly supervised and performance depends largely on the quality of the training data.
However, this data is expensive to obtain, and limits the adoption of these technologies outside of resource-rich domains.

That's where data programming comes in: a domain expert writes functions (that might be noisy or conflicting), and they are combined and denoised. These denoised functions can then be applied to a large unlabeled dataset in a weak-supervision approach.

This method was pioneered by [Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff), which aggregates and de-noises sets of labeling functions. However, little is known about user experience in writing labeling functions or how to improve it.

Inspired by work in programming by demonstration and in interactive learning, *__Data Programming by Demonstration__* means that instead of writing labeling functions, the user can label a few examples to demonstrate what those functions should do.

## <a name='Ruler'></a>How Does Řuler Apply DPBD?
Given a few intelligently selected text samples, the user can annotate some spans or relationships, and the system will automatically suggest labeling functions to choose from. The user also gets interactive feedback about how their labels are performing.

<h3 align="center">
By limiting the user's task to annotation and selection among suggested rules, <br/>
we allow fast exploration over the space of labeling functions.
 <br/>
<img width=800px src=media/fast-exploration.gif>
</h3>


## <a name='Experiments'></a>Experimental Results 
#### Comparing Ruler to other Methods of Generating Labeling Functions

We wanted to understand the trade-offs of different models for creating labeling functions, so we conducted a user study.  Ruler was compared to manual ([Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff)), and natural-language based ([Babble Labble](https://hazyresearch.github.io/snorkel/blog/babble_labble.html)) creation of functions. 

We asked six participants to create labeling functions for two prevalent labeling tasks, spam detection and sentiment classification. For each task the participant was given 30 minutes and told to write as many functions as they considered necessary for the task.  In the exit surveys we inquired participants opinions about ease of use, expressivity, and ease of learning along with overall satisfaction with the tool.  

Although we have limited data, participants rated Ruler highest in all subjective questions except expressivity by a small margin. Ruler is found to be almost as expressive as Snorkel (-0.08) and significantly more expressive than BabbleLabble (+2.58).

<img align="middle" src=media/QualitativeRatings.png>

Overall, participants found Ruler easy to use and ‘cognitively very simple’. Features such as ‘immediate visual feedback on how much a new rule increased/decreased the metrics’ leading to shorter iterations ‘encouraged \[participants] not to be hesitant about trying out stuff’ and to ‘create more labeling functions (and not be picky) and monitor how labeling functions interact and learn from those’. 

### Importantly, the ease and speed afforded by Ruler does not incur a cost on the end model performance. 

<img src=media/classifier-performance.png>

While we were expecting Ruler to lead in terms of ease of use and learning, equalling expressivity of a rich programming language with many constructs while being perceived as much richer than natural language came as a bit of surprise. 
Initial results suggest that providing a simpler grammar with few constructs could achieve good results for most tasks. 

**This allows users to focus on**

  :white_check_mark: choosing the right generalization of observed instances

  :white_check_mark: capturing the tail end of their data distribution

**and avoid worrying about**

  :x: implementation details in a programming language

  :x: how to express rules in natural language

  :x: how to formalize their intuition


## <a name='Use'></a>How to use the source code in this repo

The server runs on [Flask](https://flask.palletsprojects.com/en/1.1.x/) and can be found in [`server/`](server/). Follow the instructions in `server/README.md` to download the data and the necessary libraries.

The user interface is implemented in [React JavaScript Library](https://reactjs.org). The code and instructions can be found in [`ui/`](ui/).

Once you have both of these running, navigate to `localhost:3000`.

For more information on how to use the tool, see our [demo video](https://drive.google.com/file/d/1Z3b8wyTKoUX4b5jC8CJM9-DWuF87MwLE/view?usp=sharing).
