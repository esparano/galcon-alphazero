from keras.models import load_model

# THIS IS REQUIRED TO STOP TENSORFLOW FROM USING UP ALL GPU MEMORY
# otherwise the bot can't play against itself since the first one "steals" the GPU
# note: using nvidia-smi to debug GPU usage


def initialize():
    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto(
        gpu_options=tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
        # device_count = {'GPU': 1}
    )
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)
    set_session(session)


def getModel(modelFileName='gz_dev.model'):
    initialize()
    return load_model(modelFileName)
