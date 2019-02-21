from keras.datasets import cifar10
from muses.cifar10_helpers import load_data

__all__ = ('DATA',)

DATA = load_data(
    '/home/artur/bbrepos/muses/examples/datasets/all',
    num_train_samples=1056
)[:2]

# DATA = cifar10.load_data()  # change to correct data

# import ipdb; ipdb.set_trace()
