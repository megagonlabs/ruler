import tensorflow as tf


def get_keras_logreg(input_dim, output_dim=2):
    # set all random seeds
    import tensorflow as tf
    from numpy.random import seed as np_seed
    from random import seed as py_seed
    from snorkel.utils import set_seed as snork_seed
    snork_seed(123)
    tf.random.set_seed(123)
    np_seed(123)
    py_seed(123)

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
    return tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=10, verbose=1, restore_best_weights=True
    )


def print_instances(instances):
    for instance in instances:
        print(instance)

