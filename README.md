# RULER: Data Programming by Demonstration for Text 
 
This repo contains the source code and the user evaluation data and analysis scripts for Ruler, a data programming by demonstration system for document labeling. Ruler synthesizes labeling functions based on your span-level annotations, allowing you to quickly and easily generate large amounts of training data.

<h3 align="center">
<img width=800px src=media/ruler_teaser.gif>
</h3>

**Check out our [demo video](https://drive.google.com/file/d/1iOQt81VDg9sCPcbrMWG8CR_8dOCfpKP5/view?usp=sharing) to see Ruler in action on a spam classification task, or [try it yourself](http://54.83.150.235:3000/) on a sentiment analysis task.**


1. [What is Ruler](#ruler)
2. [How to Run the Source Code in This Repo](#Use)
   - [Engine](#Engine)
   - [User Interface](#UI)
3. [Using Ruler: the Basics](#Basics)
4. [For Researchers](#research)
5. [Contact](#Contact)


## <a name='ruler'></a>What is Ruler?

The success of machine learning has dramatically increased the demand for high-quality labeled data---but this data is 
expensive to obtain, which inhibits broader utilization of machine learning models outside resource rich settings. 
That's where data programming [[1](https://arxiv.org/pdf/1605.07723.pdf), [2](https://arxiv.org/pdf/1711.10160.pdf)] 
comes in. Data programming aims to address the difficulty of collecting labeled data using a 
programmatic approach to weak supervision, where domain (subject-matter) experts are expected to provide functions
incorporating their domain knowledge to label a subset of a large training dataset. 

This approach has a few drawbacks, however. Many domain experts lack programming expertise, but it would still be useful to translate their knowledge into functions. For example, training models for the medical domain requires volumes of high-accuracy training data, but the medical experts' time is very valuable, limiting the amount of time they can spend labeling. Even for domain experts who are proficient programmers, it is often difficult to convert domain knowledge to a set of rules. 

The accessibility of writing labeling functions is a challenge for wider adoption of data programming. To address this challenge, we introduce a new framework, __Data Programming by Demonstration (DPBD)__, to synthesize labeling functions through user interactions.

<h3 align="center">
<img  align="center" width="900" src="media/overview.png" />
Overview of the data programming by demonstration (DPBD) framework. Straight lines indicate the flow of domain
knowledge, and dashed lines indicate the flow of data.
<br/>
</h3>

DPBD aims to move the burden of writing labeling functions to an intelligent synthesizer while enabling users to steer this synthesis. Ruler is an interactive tool that operationalizes data programming by demonstration for document text.

<h3 align="center">
<img width=800px src=media/ruler_teaser_wide.png>
</h3>

For example, consider a sentiment classification task. A labeling function might look something like this Python code:
```
def find_positive_adj(text):
    if "awesome" in text or "great" in text:
        return POSITIVE
    else:
        return NEGATIVE
```
Instead of formalizing this function as Python code, a user can use Ruler to annotate the words "awesome" and "great" to get the same function. This is the "demonstration" part of DPBD.  Ruler functions can also make use of word co-occurence, named entities, and more.

Once the user is satisfied with the functions they've created using Ruler, these functions are aggregated using [Snorkel](https://www.snorkel.org/), which denoises the resulting label model. With this model, the user can label as much training data as they would like, and use it to train a more sophisticated supervised model.


<h3 align="center">
By limiting users' task to simple annotation and selection from suggested rules, <br/>
we allow fast exploration over the space of labeling functions.
 <br/>
<img width=700px src=media/fast-exporation-thin.gif>
</h3>


**This allows users to focus on**

  :white_check_mark: choosing the right generalization of observed instances

  :white_check_mark: capturing the tail end of their data distribution

**and avoid worrying about**

  :x: implementation details in a programming language

  :x: how to express rules in natural language

  :x: how to formalize their intuition
  
  
# <a name='Use'></a>How to run the source code in this repo

Follow these instructions to run the system on your own, where you can plug in your own data and save the resulting labels, models, and annotations.

## <a name='Engine'></a>Engine

The server runs on [Flask](https://flask.palletsprojects.com/en/1.1.x/) and can be found in [`server/`](server/). 

### 1. Install Dependencies :wrench:

```shell
cd server
pip install -r requirements.txt
```


### 2. Run :runner:

```
python api/server.py
```

Now the engine is running. To use Ruler, you will need to run the UI as well, described below.

You can check out http://localhost:5000/api/ui to see the supported endpoints.
This will display a [Swagger UI](https://swagger.io/tools/swagger-ui/) page that allows you to interact directly with the API.


## <a name='UI'></a>User Interface


The user interface is implemented in [React JavaScript Library](https://reactjs.org). The code can be found in [`ui/`](ui/).

### 1. Install Node.js

[You can download node.js here.](https://nodejs.org/en/)

To confirm that you have node.js installed, run `node - v`

### 2. Run

```shell
cd ui
npm install 
npm start
```

By default, the app will make calls to `localhost:5000`, assuming that you have the server running on your machine. (See the [instructions above](#Engine)).

Once you have both of these running, navigate to `localhost:3000`.


# <a name='Basics'></a>Using Ruler: the Basics

Congrats, you've got Ruler running! 🎉

### Create/Load a Project

When you navigate to `localhost:3000`, you will be guided through the process of initializing your project.

1. Upload data. 
There is some example data under (server/datasets/spam_example/processed.csv)[server/datasets/spam_example/processed.csv]. 
You can also upload your own data here, just make sure it's a valid csv file, and your text column is labeled `text`.  If you have labels you want to use for development, these should be in a column named `labels`. Ruler will automatically split your data into training (the data you interactively label), development (the data your functions are evaluated on), and test/validation (to evaluate the end model).

2. Create/load a model. 
If you're iterating on a model you've previously saved, you can load it here. Otherwise, enter a name for your new model, and you will define the label classes in the next step.

3. Define Labels.
__WARNING__ your label classes need to match the data you've uploaded. If you're dataset has labels `{0: NON-SPAM, 1: SPAM}` then you need to add the labels in this order to make sure they're mapped correctly.
If you're loading a previous model, make sure these label classes match the dataset.

4. Continue to Project.
You should automatically be redirected to `localhost:3000/project` once your data is pre-processed.


Need some ideas? Try sentiment classification on this (Amazon Review dataset)[https://www.kaggle.com/bittlingmayer/amazonreviews].
Upload this dataset, create a new model, define the labels `NON-SPAM` and `SPAM`, and get labelling.


### Get Labeling

Now you're at `localhost:3000/project`, where the magic happens. 

<h3 align="center">
<img width=800px src=media/ruler_ui.png>
</h3>

__A/B__  Highlight parts of the text, add links between them, or create concepts to annotate the data. 

__C__ Once you select a label class, Ruler will automatically suggest functions for you. Select and submit the ones you like.

__D__ Your label model performance will update as you go, showing changes with each addition/deletion of a function.

__E__ If you want to evaluate a model trained on your generated labels, click the refresh icon in this panel. This will train a logistic regression model on bag of words features and report the performance. You should use this sparingly to avoid overfitting to the test set. Note that this is a very simplistic model which may not be suitable for evaluating labels for some tasks.

__F__ Here, you can inspect individual functions' performance, and deactivate them.

See our [demo video](https://drive.google.com/file/d/1iOQt81VDg9sCPcbrMWG8CR_8dOCfpKP5/view?usp=sharing) for some example interactions.

### Finished?

Save your model by clicking the icon on the top right. If you decide to iterate on it more later, you can load it on the create/load project page.



# <a name='research'></a>For Researchers

<a href=https://github.com/megagonlabs/ruler/tree/master/user_study>Here you can find the data from our user study</a>, along with <a href=https://github.com/megagonlabs/ruler/blob/master/user_study/ruler_user_study_figures.ipynb>the code to generate all of our figures and analysis</a>. 

Please see our [Findings of EMNLP'20 publication](media/Ruler_EMNLP2020.pdf) for details. 

# <a name='contact'></a>Contact
If you have any problems, please feel free to create a Github issue. 

For other inquiries, contact <sara@megagon.ai>.

