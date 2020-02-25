# [ŘULER](http://18.223.190.82:3000/): Data Programming by Demonstration for Text 
 
 See our [demo video](https://drive.google.com/file/d/1Z3b8wyTKoUX4b5jC8CJM9-DWuF87MwLE/view?usp=sharing) or [try it yourself](http://18.223.190.82:3000/).
 
 <img src=media/ruler_demo_gif.gif>
 
 
This repo contains the source code for Ruler, a system that generates labeling functions from users' annotations of intelligently selected document examples (see our [KDD'20 submission](Ruler-KDD2020-Submission.pdf) for details). 


1. [What is Data Programming by Demonstration? (DPBD)](#DPBD)
2. [Řuler: DPBD for Text](#Ruler)
3. [Experimental Results: Comparing Ruler to other Methods of Generating Labeling Functions](#Experiments)
4. [How to use the source code in this repo](#Use)
   - [Engine](#Engine)
   - [User Interface](#UI)


## <a name='DPBD'></a>What is Data Programming by Demonstration (DPBD)?

The success of machine learning has dramatically increased the demand for high-quality labeled data-- but this data is expensive to obtain, which limits the adoption of these technologies outside of resource-rich domains.

That's where data programming comes in: a domain expert writes functions (that might be noisy or conflicting), and they are combined and denoised. These denoised functions can then be applied to a large unlabeled dataset in a weak-supervision approach.

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

We wanted to understand the trade-offs of different models for creating labeling functions, so we conducted a user study.  Řuler was compared to manual ([Snorkel](https://towardsdatascience.com/introducing-snorkel-27e4b0e6ecff)), and natural-language based ([BabbleLabble](https://hazyresearch.github.io/snorkel/blog/babble_labble.html)) creation of functions. 

We asked six participants to create labeling functions for two prevalent labeling tasks, spam detection and sentiment classification. For each task the participant was given 30 minutes and told to write as many functions as they considered necessary for the task.  In the exit surveys we inquired participants opinions about ease of use, expressivity, and ease of learning along with overall satisfaction with the tool.  

Although we have limited data, participants rated Řuler highest in all subjective questions except expressivity by a small margin. Řuler is found to be almost as expressive as Snorkel (-0.08) and significantly more expressive than BabbleLabble (+2.58).

<img align="middle" src=media/QualitativeRatings.png>

Overall, participants found Řuler easy to use and "cognitively very simple." Features such as "immediate visual feedback on how much a new rule increased/decreased the metrics" leading to shorter iterations "encouraged \[participants] not to be hesitant about trying out stuff" and to "create more labeling functions (and not be picky) and monitor how labeling functions interact and learn from those."

### Importantly, the ease and speed afforded by Řuler does not incur a cost on the end model performance. 

<img src=media/classifier-perfm.png>

While we were expecting Řuler to lead in terms of ease of use and learning, equalling expressivity of a rich programming language with many constructs while being perceived as much richer than natural language came as a bit of surprise. 
Initial results suggest that providing a simpler grammar with few constructs could achieve good results for most tasks. 

**This allows users to focus on**

  :white_check_mark: choosing the right generalization of observed instances

  :white_check_mark: capturing the tail end of their data distribution

**and avoid worrying about**

  :x: implementation details in a programming language

  :x: how to express rules in natural language

  :x: how to formalize their intuition


# <a name='Use'></a>How to use the source code in this repo

Follow these instructions to run the system on your own, where you can plug in your own data and save the resulting labels, models, and annotations.

## <a name='Engine'></a>Engine

The server runs on [Flask](https://flask.palletsprojects.com/en/1.1.x/) and can be found in [`server/`](server/). 

### 1. Install Dependencies :wrench:

```shell
cd server
pip install -r requirements.txt
```

### 2. Upload Data :memo:

To run the Youtube Spam Classification task shown in the demo, download the data files [here](https://www.kaggle.com/goneee/youtube-spam-classifiedcomments) and place them under `data/`.
There should be five files.

 __Want to use Another Dataset?__ 

 Open `server/api/idea2.py`. 
 You'll want to replace `load_youtube_dataset` with your own function. 
 The return value of this function should be 4 [pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) (training, development, validation, and test sets).  
 
 Your dataframes must have:
  - A `label` column: an integer value describing which class the example belongs to. (The training dataframe doesn't need this column).
  - A `text` column: the text to be annotated.
  - A unique [index](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Index.html?highlight=index#pandas.Index). You can use the `[reset_index](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html)` function to do this.
 
For an example, see `server/data/preparer.py`.

In `server/api/idea2.py`, you should also change the variables `MODE` and `USER` to something descriptive. This will dictate the directory where your models are saved, should you choose to save them.

### 3. Run :runner:

```
python api/server.py
```

Open your browser, and got to http://localhost:5000/api/ui

This will display a [Swagger UI](https://swagger.io/tools/swagger-ui/) page that allows you to interact directly with the API.

### 4. Save Your Model (Optional) :floppy_disk:

Via Ruler UI: 

Click the save button in the top right corner.


Via the API :

Submit a post request to `http://localhost:5000/save`. 


The snorkel model, concepts, labelling function history, and interaction history will all be in the directory `<USER>/<MODE>`.
By default this is `guest/Youtube`.


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

#### For more information on how to use the tool, see our [demo video](https://drive.google.com/file/d/1Z3b8wyTKoUX4b5jC8CJM9-DWuF87MwLE/view?usp=sharing).
