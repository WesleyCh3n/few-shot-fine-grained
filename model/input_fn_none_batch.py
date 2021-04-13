import os
import pathlib
import tensorflow as tf


def parse_filename(path):
    ds_root = pathlib.Path(path)
    filenames = list(ds_root.glob('*/*'))
    filenames = [str(path) for path in filenames]
    label_names = sorted(item.name for item in ds_root.glob('*/')
            if item.is_dir())
    label_to_index = dict((name, index) for index, name
            in enumerate(label_names))
    labels = [label_to_index[pathlib.Path(path).parent.name]
            for path in filenames]
    return filenames, labels, len(filenames)

def _parse_function(data, size):
    filename = data['img']
    image_string = tf.io.read_file(filename)
    image = tf.image.decode_jpeg(image_string, channels=3, dct_method='INTEGER_ACCURATE')
    image = tf.cast(image, tf.float32)
    image = ((image / 255.0)-0.5)*2.0
    image = tf.image.resize(image, size)
    data['img'] = image
    return data

def generate_dataset(f, l, params):
    parse_fn = lambda d: _parse_function(d, params["size"])
    dataset = tf.data.Dataset.from_tensor_slices({'img':f, 'label':l})
    dataset = dataset.map(parse_fn, num_parallel_calls=4)
    return dataset

def none_batch_dataset_pipeline(folder, params):
    ds_filenames, ds_labels, ds_counts = parse_filename(folder)
    ds = generate_dataset(ds_filenames, ds_labels, params)
    return ds, ds_counts