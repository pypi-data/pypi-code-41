import cv2
import random
import numpy as np
import tensorflow as tf
from qoalai.networks.inception_resnetv2 import *
from comdutils.file_utils import get_filenames


def conv_block(inputs, 
               filters, 
               kernel_size,
               is_training, 
               strides=(2,2), 
               padding='valid', 
               dropout_rate=0.15, 
               activation='relu'):

    conv = tf.layers.conv2d(inputs=inputs, 
                            filters=filters, 
                            kernel_size=kernel_size, 
                            strides=strides, 
                            padding=padding, 
                            activation=activation, 
                            trainable=is_training)
    conv = tf.layers.batch_normalization(inputs=conv, trainable=is_training)
    conv = tf.layers.dropout(inputs=conv, rate=dropout_rate)
    return conv


class DeepLab(InceptionV4ResnetV2):
    def __init__(self, num_classes, 
                       input_tensor = None,
                       input_shape = (None, 300, 300, 3),
                       model_path = None,
                       output_stride = 16,
                       learning_rate = 0.0001, 
                       is_training = True):
        """[summary]
        
        Arguments:
            num_classes {[type]} -- [description]
        
        Keyword Arguments:
            input_shape {tuple} -- [description] (default: {(None, 300, 300, 3)})
            base_architecture {str} -- [description] (default: {'resnet_v2_101'})
            output_stride {int} -- [description] (default: {16})
            learning_rate {float} -- [description] (default: {0.0001})
            is_training {bool} -- [description] (default: {True})
        """
        if input_tensor is None:
            self.input = tf.placeholder(shape=input_shape, dtype=tf.float32)
        else:
            self.input = input_tensor

        super(DeepLab, self).__init__(input_tensor=self.input, is_training = is_training) 
        self.target = tf.placeholder(shape=input_shape, dtype=tf.float32)
        self.input_width = input_shape[1]
        self.input_height = input_shape[2]
        self.learning_rate = learning_rate
                                              
        self.output = self.create_base_model(input=self.input)
        self.output = self.create_deeplab(self.output)

        if is_training:
            # ---------------------------------- #
            # calculate loss, using soft dice    #
            # ---------------------------------- #
            self.cost = self.soft_dice_loss(self.target, self.output)
            update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(update_ops):
                self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.cost)

        # ---------------------------------- #
        # tensorflow saver                   #
        # ---------------------------------- #
        #self.saver_partial = tf.train.Saver(var_list=self.base_vars)
        self.saver_all = tf.train.Saver()
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
         
        if model_path is not None:
            self.saver_all.restore(self.session, model_path)
            print ("-------------------------------------")
            print ("INFO: Read all model weight success")
            print ("-------------------------------------")

        
    def atrous_spatial_pyramid_pooling(self, inputs,
                                        output_stride):
        """Atrous Spatial Pyramid Pooling.
        Args:
            inputs: A tensor of size [batch, height, width, channels].
            output_stride: The ResNet unit's stride. Determines the rates for atrous convolution.
            the rates are (6, 12, 18) when the stride is 16, and doubled when 8.
            batch_norm_decay: The moving average decay when estimating layer activation
            statistics in batch normalization.
            is_training: A boolean denoting whether the input is for training.
            depth: The depth of the ResNet unit output.
        Returns:
            The atrous spatial pyramid pooling output.
        """
        with tf.variable_scope("aspp"):

            if output_stride not in [8, 16]:
                raise ValueError('output_stride must be either 8 or 16.')
            atrous_rates = [6, 12, 18]

            if output_stride == 8:
                atrous_rates = [2*rate for rate in atrous_rates]
            
            conv_1x1_1 = conv_block(inputs=inputs, 
                                    filters=128, 
                                    kernel_size=(1,1), 
                                    strides=(1,1), 
                                    is_training=self.is_training)
            
            input_depth = inputs.get_shape().as_list()[-1]
            kernel =  np.random.random((3, 3, input_depth, 128)).astype(np.float32)
            conv_3x3_1 = tf.nn.atrous_conv2d(value=inputs, 
                                             filters=kernel, 
                                             rate=atrous_rates[0], 
                                             padding='SAME', 
                                             name = 'atrous1')

            conv_3x3_2 = tf.nn.atrous_conv2d(value=inputs, 
                                             filters=kernel, 
                                             rate=atrous_rates[1], 
                                             padding='SAME',
                                             name = 'atrous2')

            conv_3x3_3 = tf.nn.atrous_conv2d(value=inputs, 
                                            filters=kernel,
                                            rate=atrous_rates[2], 
                                            padding='SAME', 
                                            name = 'atrous3')

            concat_1 = tf.concat([conv_1x1_1, conv_3x3_1, conv_3x3_2, conv_3x3_3], -1)

            conv_1x1_2 = conv_block(inputs=concat_1, 
                                    filters=128, 
                                    kernel_size=(1,1), 
                                    strides=(1,1), 
                                    is_training=self.is_training)

            upsample = tf.image.resize_bilinear(images=conv_1x1_2, size=(140,140))
            return upsample
          

    def create_deeplab(self, inputs):
        """[summary]
        
        Arguments:
            inputs {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        inputs = tf.image.resize_bilinear(images=inputs, size=(140,140))
        conv_1x1 = conv_block(inputs=inputs, 
                              filters=128, 
                              kernel_size=(1,1), 
                              strides=(1,1), 
                              is_training=self.is_training, 
                              padding='same')

        atrous_output = self.atrous_spatial_pyramid_pooling(inputs=inputs, 
                                                            output_stride=16)
        concat_1 = tf.concat([atrous_output, conv_1x1], -1)
        conv_3x3 = conv_block(inputs=concat_1, 
                              filters=3, 
                              kernel_size=(1,1), 
                              strides=(1,1), 
                              is_training=self.is_training, 
                              activation=None)
        upsample = tf.image.resize_bilinear(images=conv_3x3, size=(300,300))
        upsample = tf.nn.sigmoid(upsample)

        return upsample


    def soft_dice_loss(self, y_true, y_pred, epsilon=1e-6):
        """[summary]
        
        Arguments:
            y_true {[type]} -- [description]
            y_pred {[type]} -- [description]
        
        Keyword Arguments:
            epsilon {[type]} -- [description] (default: {1e-6})
        """ 
        numerator = tf.reduce_sum( y_pred * y_true)
        denominator = tf.reduce_sum(y_true)
        dice_loss = 1 - numerator / (denominator + epsilon)

        mse_loss = tf.reduce_mean(tf.square(y_true - y_pred))
        return 0.8 * dice_loss + 0.2 * mse_loss
        #return mse_loss


    def batch_generator(self, batch_size, dataset_path):
        """Train Generator
        
        Arguments:
            batch_size {integer} -- the size of the batch
            image_name_list {list of string} -- the list of image name
        """
        self.label_folder_path = dataset_path + "labels/"
        self.dataset_folder_path = dataset_path + "images/"
        self.dataset_file_list = get_filenames(self.dataset_folder_path)
        random.shuffle(self.dataset_file_list)
        
        print ("------------------------INFO IMAGES-------------------")
        print ("Image Folder: " + self.dataset_folder_path)
        print ("Number of Image: " + str(len(self.dataset_file_list)))
        print ("------------------------------------------------------")

        # Infinite loop.
        idx = 0
        while True:
            x_batch = []
            y_pred = []

            for i in range(batch_size):
                if idx >= len(self.dataset_file_list):
                    idx = 0
                
                try:
                    tmp_x = cv2.imread(self.dataset_folder_path + self.dataset_file_list[idx])
                    tmp_x = cv2.cvtColor(tmp_x, cv2.COLOR_BGR2RGB)
                    tmp_x = cv2.resize(tmp_x, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                    tmp_x = tmp_x.astype(np.float32) / 255.
                    tmp_y = cv2.imread(self.label_folder_path + self.dataset_file_list[idx])
                    tmp_y = cv2.cvtColor(tmp_y, cv2.COLOR_BGR2RGB)
                    tmp_y = cv2.resize(tmp_y, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                    tmp_y = tmp_y.astype(np.float32) / 255.
                    x_batch.append(tmp_x)
                    y_pred.append(tmp_y)
                except Exception as e:
                    print ("-----------------------------------------------------------------------------")
                    print ('>>> WARNING: fail handling ' +  self.dataset_file_list[idx], e)
                    print ("-----------------------------------------------------------------------------")

                idx += 1
            yield (np.array(x_batch), np.array(y_pred))


    def optimize(self, subdivisions,
                iterations, 
                best_loss, 
                train_batch, 
                val_batch, 
                save_path):
        """[summary]
        
        Arguments:
            subdivisions {[type]} -- [description]
            iterations {[type]} -- [description]
            best_loss {[type]} -- [description]
            train_batch {[type]} -- [description]
            val_batch {[type]} -- [description]
            save_path {[type]} -- [description]
        """
        
        self.train_losses = []
        self.val_losses = []
        best_loss = best_loss

        for i in range(iterations):
            sign = '-'

            tmp_losses = []
            for j in range(subdivisions):
                # ------------------------- #
                # feed train data           #
                # ------------------------- #
                input_image, target_image = next(train_batch)
                feed_dict = {}
                feed_dict[self.input] = input_image
                feed_dict[self.target] = target_image
                self.session.run(self.optimizer, feed_dict)
                loss = self.session.run(self.cost, feed_dict)
                tmp_losses.append(loss)
                print ("> Train sub", j, 'loss : ', loss)
                
            # ------------------------- #
            # feed validation data      #
            # ------------------------- #
            input_image, target_image = next(val_batch)
            feed_dict = {}
            feed_dict[self.input] = input_image
            feed_dict[self.target] = target_image
            loss = self.session.run(self.cost, feed_dict)

            # ------------------------- #
            # append loss val           #
            # ------------------------- #
            self.val_losses.append(loss)
            train_loss = sum(tmp_losses)/(len(tmp_losses)+0.0001)
            self.train_losses.append(train_loss)
            
            if loss < best_loss:
                best_loss = loss
                sign = '***************'
                self.saver_all.save(self.session, save_path)
                
            print ("> iteration", i, 'train loss: ', train_loss, 'val loss: ', loss, sign)