# IDEA2
Interactive Data Exploration for Automated Annotation


## Installation

### Download the repo and create runtime environment

```
git clone https://github.com/rit-git/IDEA2.git .
cd IDEA2
pip install -r requirements.txt
```


## Run



### Start
```
python api/server.py
```

Open your browser, and got to http://localhost:5000/

There are 2 datasets in the repo that you can try--
 - Amazon Reviews: sentiment classification on 1 star and 5 star product reviews
 - Youtube comments: spam classification

To change datasets, edit `python api/server.py` on line 28, and set `MODE = "Amazon"` or `MODE="Youtube"`
