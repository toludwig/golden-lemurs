import tensorflow as tf
import numpy as np
from ..Logger import Logger
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN

BATCH_SIZE = 300
LEARNING_RATE = 0.00007
VALIDATION_DATA = 300
VALIDATION_EPOCHES = 100
CHECKPOINT_PATH = "./Gloved.ckpt"
TITLE = 'Muh net'
COMMENT = "preprocess, mid-deep, normal pooling, wide ffn"

def train(arg):
    with tf.Session() as session:
        saver = tf.train.Saver()
        # TODO: net = TEXTCNN()
