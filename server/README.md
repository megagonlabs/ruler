# IDEA2
Interactive Data Exploration for Automated Annotation


## Installation

### Download the repo and create runtime environment

```
git clone https://github.com/rit-git/IDEA2.git .
cd IDEA2
pip install -r requirements.txt
```

### Download the data

Download the files [here](https://www.kaggle.com/goneee/youtube-spam-classifiedcomments) and place them under `data/`.
There should be five files.

## Run



```
python api/server.py
```

Open your browser, and got to http://localhost:5000/api/ui

This will display a [Swagger UI](https://swagger.io/tools/swagger-ui/) page that allows you to interact directly with the API.



