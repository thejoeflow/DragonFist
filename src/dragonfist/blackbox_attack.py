import keras

from attacks import back_to_black
from data import DataSet
from ensembles.stacking import Stacking
from model import Claw
from processing import ImageProcessParams
from skimage import filters
import transformations as tr


def main():
    dataset = DataSet.load_from_keras(keras.datasets.fashion_mnist, dtype='float32')

    # claw = Claw(dataset, auto_train=True, plot_images=0, epochs=3)
    # claw = Claw(dataset, ImageProcessParams(filters.gaussian, {'sigma': 1.5}), auto_train=True, epochs=3)
    # results = back_to_black(claw, dataset)

    ensemble = build_ensemble(dataset)
    results = back_to_black(ensemble, dataset)

    print('Accuracy of target black-box on legitimate test examples: ' + str(results.get('bbox_acc_legit')))
    print('Accuracy of substitute model on legitimate test examples: ' + str(results.get('sub_acc_legit')))
    print('Accuracy of substitute model on adversarial images generated by substitute: ' + str(results.get('sub_acc_adv')))
    print('Accuracy of target black-box on adversarial images generated by substitute: ' + str(results.get('bbox_acc_adv')))


def build_ensemble(dataset):

    claw1 = Claw(dataset, auto_train=True, retrain=False, epochs=3)

    claw2 = Claw(dataset, ImageProcessParams(filters.gaussian, {'sigma': 1.5}), auto_train=True, epochs=3)

    claw3 = Claw(dataset, ImageProcessParams(filters.sobel, {}, tr.compat2d, {'zca_whitening': True}), auto_train=True, epochs=3)

    ensemble = Stacking(claw1, claw2, claw3)

    x = dataset.train_images
    y = dataset.train_labels

    ensemble.fit(x=x, y=y)
    return ensemble

main()