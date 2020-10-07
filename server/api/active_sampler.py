from math import log

def next_text(modeler, dataset, subset_size=50):
    # Limit our search to the least seen examples
    # TODO it's a little hacky to use the dataframe underlying the dataset...
    min_seen = dataset.df["seen"].min()
    least_seen_examples = dataset.df[dataset.df["seen"]==min_seen]

    if ((len(least_seen_examples)==1) \
        or (len(modeler.get_lfs())==0)):
        # We have no labelling functions, or only one example hasn't been seen:
        res_idx = least_seen_examples.sample(1).index[0]
    else:
        modeler.fit(dataset)
        # Sample at most subset_size examples
        subset_size = min(subset_size, len(least_seen_examples))
        subset = least_seen_examples.sample(subset_size)

        probs = modeler.predict(subset)
        entropies = [entropy(x) for x in probs]
        subset = subset[entropies==max(entropies)]

        res_idx = subset.sample(1).index[0]
    dataset.df.at[res_idx, "seen"] += 1
    return {"text": dataset.df.at[res_idx, "text"], "id": int(res_idx)}

def entropy(prob_dist):
    #return(-(L_row_i==-1).sum())
    return(-sum([x*log(x) for x in prob_dist]))