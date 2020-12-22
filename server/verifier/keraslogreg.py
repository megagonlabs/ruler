"""END MODEL
To better evaluate the quality of our generated training data, 
we evaluate an end model trained on this data. 

Here, the end model is implemented as a logistic regression bag of words model. 
However, you can replace this with any model of your choosing, as long as it has
functions "fit" and "predict" with the specifications outlined below.
"""
import tensorflow as tf

from numpy.random import seed as np_seed
from random import seed as py_seed
from snorkel.utils import set_seed as snork_seed
from snorkel.utils import preds_to_probs
from sklearn.feature_extraction.text import CountVectorizer



def get_keras_logreg(input_dim, output_dim=2):
    """Create a simple logistic regression model (using keras)
    """
    model = tf.keras.Sequential()
    if output_dim == 1:
        loss = "binary_crossentropy"
        activation = tf.nn.sigmoid
    else:
        loss = "categorical_crossentropy"
        activation = tf.nn.softmax
    dense = tf.keras.layers.Dense(
        units=output_dim,
        input_dim=input_dim,
        activation=activation,
        kernel_regularizer=tf.keras.regularizers.l2(0.001),
    )
    model.add(dense)
    opt = tf.keras.optimizers.Adam(lr=0.01)
    model.compile(optimizer=opt, loss=loss, metrics=["accuracy"])

    return model



def get_keras_early_stopping(patience=10):
    """Create early stopping condition
    """
    return tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=10, verbose=1, restore_best_weights=True
    )


class KerasLogReg:
    """This logistic regression model is trained on the labels that Ruler generates, and then evaluated against a test set.
    This provides a more complete picture of the quality of the generated training data.

    Attributes:
        cardinality (int): Number of output classes
        keras_model (a Keras logistic regression model): Description
        vectorizer (CountVectorizer): Object with fit and transform functions, which transforms texts into vectors
    """
    
    def __init__(self, cardinality=2):
        """Summary
        
        Args:
            cardinality (int, optional): Number of output classes
        """
        # Set all random seeds
        snork_seed(123)
        tf.random.set_random_seed(123)
        np_seed(123)
        py_seed(123)
        self.cardinality = cardinality
        self.keras_model = None

    def fit(self, X_train, Y_train, X_valid, Y_valid):
        """Train the model using the given training and validation data.
        
        Args:
            X_train (list(str)): Training text examples, length n
            Y_train (matrix): Training labels, size n*m, where m is the cardinality
            X_valid (list(str)): Validation test examples, length p
            Y_valid (matrix): Validation labels, size p*m
        """
        if self.keras_model is None:
            self.vectorizer = CountVectorizer(ngram_range=(1, 2))
            self.vectorizer.fit(X_train)
        X_train = self.vectorizer.transform(X_train)
        X_valid = self.vectorizer.transform(X_valid)
        if self.keras_model is None:
            self.keras_model = get_keras_logreg(input_dim=X_train.shape[1], output_dim=self.cardinality)
        self.keras_model.fit(
            x=X_train,
            y=Y_train,
            validation_data=(X_valid, Y_valid),
            callbacks=[get_keras_early_stopping()],
            epochs=20,
            verbose=0,
        )

    def predict(self, X):
        """Predict probabilities that each sample in X belongs to each class.
        
        Args:
            X (list(str)): Texts to predict class, length n
        
        Returns:
            matrix: size n*m, where m is the cardinality of the model
        """
        X_v = self.vectorizer.transform(X)
        return self.keras_model.predict(x=X_v)

