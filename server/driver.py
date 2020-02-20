from data.preparer import load_youtube_dataset
from synthesizer.gll import ConceptWrapper, Label, ID, DELIMITER
from synthesizer.synthesizer import Synthesizer
from verifier.translator import make_lf
from verifier.modeler import Modeler
from verifier.util import print_instances


labels = Label(name="Youtube Comments Classification: Spam or Not Spam")
labels.add_label(lname="NON-SPAM")
labels.add_label(lname="SPAM")


df_train, df_dev, df_valid, df_test = load_youtube_dataset(delimiter=DELIMITER)


text_origins = ["check out my blog.", "http://ad.com", "please vote!!", "subscribe my channel", "great song!"]
text_labels = ["#check out### my blog.", "#http#link##://ad.com", "#please### vote!!", "#subscribe### my channel", "great #song###!"]
labels = [labels.to_int("SPAM"), labels.to_int("SPAM"), labels.to_int("SPAM"), labels.to_int("SPAM"), labels.to_int("NON-SPAM")]

all_concepts = ConceptWrapper()
all_concepts.add_element(name="my", elements=["my"])
all_concepts.add_element(name="subscribe", elements=["subscribe", "subsc"])
all_concepts.add_element(name="link", elements=["http", "https", "wwww", ".com"])
all_concepts.add_element(name="please", elements=["please", "plz"])


instances = []
for i in range(len(text_origins)):
    text_origin = text_origins[i]
    text_labeled = text_labels[i]
    label = labels[i]

    crnt_syn = Synthesizer(text_origin, text_labeled, label, DELIMITER, all_concepts.get_dict())
    crnt_instances = crnt_syn.run()

    instances.extend(crnt_instances[:1])

print_instances(instances)

lfs = []
for crnt_instance in instances:
    crnt_instance[ID] = instances.index(crnt_instance)
    lfs.append(make_lf(crnt_instance, all_concepts.get_dict()))


modeler = Modeler(df_train, df_dev, df_valid, df_test)
modeler.add_lfs(lfs)

modeler.apply_lfs()
print(modeler.analyze_lfs())

modeler.fit_label_model()
print(f"{'Label Model Accuracy:':<25} {modeler.get_label_model_acc() * 100:.1f}%")

test_acc, test_precision, test_recall, test_f1 = modeler.train()
print(f"Test Accuracy:  {test_acc * 100:.1f}%")
print(f"Test Precision: {test_precision * 100:.1f}%")
print(f"Test Recall:    {test_recall * 100:.1f}%")
print(f"Test F1:        {test_f1 * 100:.1f}%")


next_text = modeler.next_text()
print(next_text.values)
