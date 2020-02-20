# Řuler
 Data Programming by Demonstration for Text 
 
 <img align="middle" src=media/ruler_demo_gif.gif>
 
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

## <a name='Ruler'></a>How Does Řuler Apply DPBD?
We build on previous research on programming by demonstration and interactive learning to create a system where the user can annotate a few intelligently selected text examples, and the system will automatically suggest labeling functions to choose from. 

### By limiting the user's task to annotation and selection among suggested rules, **we allow fast exploration over the space of labeling functions.**

<img  src=https://media.giphy.com/media/XreQmk7ETCak0/giphy.gif>


The user also gets interactive feedback on how their rules perform. 


## <a name='Experiments'></a>Experimental Results: Comparing Ruler to other Methods of Generating Labeling Functions
We evaluate our framework together with two alternative models for creating labeling functions: manual ([Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff)), and natural-language based ([Babble Labble](https://hazyresearch.github.io/snorkel/blog/babble_labble.html)). We aim to understand the trade-offs afforded by each method.

We asked six participants to create labeling functions for two prevalent labeling tasks, spam detection and sentiment classification. For each task the participant was given 30 minutes and told to write as many functions as they considered necessary for the task.

In the exit surveys we inquired participants opinions about ease of use, expressivity, and ease of learning along with overall satisfaction with the tool.  While we have limited data, with two participants in each condition, participants rated Ruler highest in all subjective questions except expressivity by a small margin. Ruler is found to be almost as expressive as Snorkel (-0.08) and significantly more expressive than BabbleLabble (+2.58).

<img align="middle" src=media/QualitativeRatings.png>

Overall, participants found Ruler easy to use and ‘cognitively very simple’ (P6). Features such as ‘immediate visual feedback on how much a new rule increased/decreased the metrics’ (P6) leading to shorter iterations ‘encouraged \[participants] not to be hesitant about trying out stuff’(P5) and ‘create more labeling functions (and not be picky) and monitor how labeling functions interact and learn from those’ (P5). 

### Preliminary results suggest that the ease and speed afforded by Ruler does not incur a cost on the end model performance.

<img align="middle" src=media/classifier-performance.png>

While we were expecting Ruler to lead in terms of ease of use and learning, equalling expressivity of a rich programming language with many constructs while being perceived as much richer than natural language came as a bit of surprise. 

Initial results suggest that providing a simpler grammar with few constructs could achieve good results when considered in aggregates where learning of respective weights is left up to machine learning. As such, **users can focus on choosing the right generalization of observed instances, rather than on the implementation details** in a programming language, or on how to express it in natural language with potentially invisible rules of interpretation. 

## <a name='Use'></a>How to use the source code in this repo

The server runs on [Flask](https://flask.palletsprojects.com/en/1.1.x/) and can be found in `server/`. Follow the instructions in `server/README.md` to download the data and the necessary libraries.

The user interface is implemented in [React JavaScript Library](https://reactjs.org). The code and instructions can be found in `ui/`.


