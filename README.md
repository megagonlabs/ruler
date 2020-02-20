# Řuler
 Data Programming by Demonstration for Text 
 
 
This repo contains the source code for Ruler, a system that generates labeling functions from users' annotations of intelligently selected document examples (see our [KDD '20 submission]() for details). 

1. [Background](#Introduction)
   - [What is Data Programming by Demonstration? (DPBD)](#DPBD)
2. [Řuler](#Ruler)
   - [Experimental Results](#Experiments)
   - [Try it](#Webpage)
3. [How to use the source code in this repo?](#Use)
   - [Accessing the data](#Access)
   - [Using Ruler](#Run)


## <a name='Introduction'></a>

### <a name='DPBD'></a>What is Data Programming by Demonstration (DPBD)?
The success of machine learning has dramatically increased the demand for high-quality labeled data, as the models used in practice are predominantly supervised and performance depends largely on the quality of the training data.
However, this data is expensive to obtain, and limits the adoption of these technologies outside of resource-rich domains.

That's where data programming comes in: a domain expert writes functions (that might be noisy or conflicting), and they are combined and denoised. These denoised functions can then be applied to a large unlabeled dataset in a weak-supervision approach.

This method was pioneered by [Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff), which aggregates and de-noises sets of labeling functions. However, little is known about user experience in writing labeling functions or how to improve it.

## <a name='Ruler'></a>How Does Řuler Apply DPBD?
We build on previous research on programming by demonstration and interactive learning to create a system where the user can annotate a few intelligently selected text examples, and the system will automatically suggest labeling functions to choose from. 

By limiting the user's task to annotation and selection among suggested rules, **we allow fast exploration over the space of labeling functions.**

The user also gets interactive feedback on how their rules perform. 

<img align="middle" src=media/ruler_demo_gif.gif>

### <a name='Experiments'></a>Experimental Results
We evaluate our framework together with two alternative models for creating labeling functions: manual ([Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff)), and natural-language based ([Babble Labble](https://hazyresearch.github.io/snorkel/blog/babble_labble.html)). We aim to understand the trade-offs afforded by each method.

We asked six participants to create labeling functions for two prevalent labeling tasks, spam detection and sentiment classification. For each task the participant was given 30 minutes and told to write as many functions as they considered necessary for the task.

<img align="middle" src=media/QualitiativeRatings.png>
<img align="middle" src=media/classifier-performance.png>



