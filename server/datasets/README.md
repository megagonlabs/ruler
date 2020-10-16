# Datasets
This folder is where you will upload the data you would like to use with Ruler.
You can place it directly in this folder, or you can upload a csv file via the UI-- either way it will end up here.

## Data Format
Data should be uploaded as a csv file, with a column named `text` denoting the text that you would like to classify/annotate.
To get the most out of Ruler, you should have a small labelled development set as well. 
This enables the interactive statistics that tell you how your functions are performing. This column should be named `label`.

For example, data for a spam classification task (`{0: HAM, 1: SPAM}`) might have this format:

| id | text                                         | label |
|----|----------------------------------------------|-------|
| 0  | Buy my sand pastries! They are mostly edible | 1     | 
| 1  | I love this video                            | 0     | 

## Example Data
 You can download a sample spam classification dataset [here](https://archive.ics.uci.edu/ml/datasets/YouTube+Spam+Collection).
 The provided description: "It is a public set of comments collected for spam research. It has five datasets composed by 1,956 real messages extracted from five videos that were among the 10 most viewed on the collection period."
 
 
