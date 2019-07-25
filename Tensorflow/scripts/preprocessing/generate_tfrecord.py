from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf
import sys
parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
parentdir = os.path.abspath(os.path.join(parentdir, '..'))

sys.path.append(parentdir + '/models/research/')

from PIL import Image
from object_detection.utils import dataset_util
#from object_detection.utils import label_map_util

#from object_detection.utils import visualization_utils as vis_util
from collections import namedtuple, OrderedDict

flags = tf.app.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
flags.DEFINE_string('label0', '', 'Name of class label')
flags.DEFINE_string('label1', '', 'Name of class label')
flags.DEFINE_string('label2', '', 'Name of class label')
flags.DEFINE_string('label3', '', 'Name of class label')
flags.DEFINE_string('label4', '', 'Name of class label')
flags.DEFINE_string('label5', '', 'Name of class label')
flags.DEFINE_string('label6', '', 'Name of class label')
flags.DEFINE_string('label7', '', 'Name of class label')
# if your image has more labels input them as
# flags.DEFINE_string('label0', '', 'Name of class[0] label')
# flags.DEFINE_string('label1', '', 'Name of class[1] label')
# and so on.
flags.DEFINE_string('img_path', '', 'Path to images')
FLAGS = flags.FLAGS


# TO-DO replace this with label map
# for multiple labels add more else if statements
def class_text_to_int(row_label):
    print(row_label)
    #if row_label == FLAGS.label:  # 'ship':
    #    return 1
    # comment upper if statement and uncomment these statements for multiple labelling
    if row_label == FLAGS.label0:
     return 1
    elif row_label == FLAGS.label1:
     return 2
    elif row_label == FLAGS.label2:
     return 3
    elif row_label == FLAGS.label3:
     return 4
    elif row_label == FLAGS.label4:
     return 5
    elif row_label == FLAGS.label5:
     return 6
    elif row_label == FLAGS.label6:
     return 7
    elif row_label == FLAGS.label7:
     return 8
    else:
     None


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    # check if the image format is matching with your images.
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), FLAGS.img_path)
    examples = pd.read_csv(FLAGS.csv_input, engine='python')
    grouped = split(examples, 'filename')
    for group in grouped:
        print(group)
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print('Successfully created the TFRecords: {}'.format(output_path))


if __name__ == '__main__':
    tf.app.run()