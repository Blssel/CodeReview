#coding:utf-8

"""根据Kaiming He等人的Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun 
Deep Residual Learning for Image Recognition. arXiv:1512.03385所搭建的
ResNet50 为v1版，源代码来自GitHub tensorflow开源项目，由谷歌官方搭建，
源码地址为：https://github.com/tensorflow/models/blob/master/official/resnet/resnet_model.py

由Zhiyu Yin在学习过程中注释为中文，且仅作为学习使用。
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

_BATCH_NORM_DECAY = 0.997
_BATCH_NORM_EPSILON = 1e-5
DEFAULT_VERSION = 2
DEFAULT_DTYPE = tf.float32
CASTABLE_TYPES = (tf.float16,)
ALLOWED_TYPES = (DEFAULT_DTYPE,) + CASTABLE_TYPES

################################################################################
# 为建立resnet的方便而编写的函数:padding后的conv 以及padding方法本身
################################################################################

def conv2d_fixed_padding(inputs, filters, kernel_size, strides, data_format):
  """由于ResNet的feature map长宽维度需要在同一个残差快中保持一致，所以需要通过padding来维持(padding大小由kernel size决定 如果是1*1的kernel，且stride为1 则无需padding)"""
  if strides > 1:
    inputs = fixed_padding(inputs, kernel_size, data_format)  # 做必要的padding

  return tf.layers.conv2d(
      inputs=inputs, filters=filters, kernel_size=kernel_size, strides=strides,
      padding=('SAME' if strides == 1 else 'VALID'), use_bias=False,
      kernel_initializer=tf.variance_scaling_initializer(),
      data_format=data_format)  # filters参数指卷积核的数量

def fixed_padding(inputs, kernel_size, data_format):
  """
  参数:
    inputs: A tensor of size [batch, channels, height_in, width_in] or [batch, height_in, width_in, channels] depending on data_format.
    kernel_size:一个整数，表示卷积核尺寸 
    data_format: 'channels_last' 或 'channels_first')
  返回:
    返回一个tensor，如果kernel_size == 1（默认stride都是1），则原封不动地（intact），否则kernel_size > 1的话返回padding后的tensor
  """
  pad_total = kernel_size - 1  # 正常kernel_size都是奇数
  pad_beg = pad_total // 2 # 地板除
  pad_end = pad_total - pad_beg

  if data_format == 'channels_first':
    padded_inputs = tf.pad(inputs, [[0, 0], [0, 0],[pad_beg, pad_end], [pad_beg, pad_end]])
  else:
    padded_inputs = tf.pad(inputs, [[0, 0], [pad_beg, pad_end],[pad_beg, pad_end], [0, 0]])
  return padded_inputs

################################################################################
# 定义ResNet的 block 计算（所谓block指的就是一个完整的残差块计算）
################################################################################
def _building_block_v1(inputs, filters, training, projection_shortcut, strides, data_format):

def _building_block_v2(inputs, filters, training, projection_shortcut, strides, data_format):

def _bottleneck_block_v1(inputs, filters, training, projection_shortcut, strides, data_format):
  """
  指的是He等人第一篇ResNet论文中的ResNet50结构
  """
  shortcut = inputs # 备份恒等映射的值
  
  # 如果维度不一致，需要做一个映射
  if projection_shortcut is not None:
    shortcut = projection_shortcut(inputs)
    shortcut = batch_norm(inputs=shortcut, training=training, data_format=data_format) # BN！！！！！！！！！

  # 第一个卷积
  inputs = conv2d_fixed_padding(inputs=inputs, filters=filters, kernel_size=1, strides=1, data_format=data_format)
  inputs = batch_norm(inputs, training, data_format)
  inputs = tf.nn.relu(inputs)

  # 第二个卷积
  inputs = conv2d_fixed_padding(inputs=inputs, filters=filters, kernel_size=3, strides=strides, data_format=data_format)
  inputs = batch_norm(inputs, training, data_format)
  inputs = tf.nn.relu(inputs)

  # 第三个卷积
  inputs = conv2d_fixed_padding(inputs=inputs, filters=4 * filters, kernel_size=1, strides=1, data_format=data_format) #注意此处filters参数的值
  inputs = batch_norm(inputs, training, data_format)

  # 加上短连接的值 并激活
  inputs += shortcut
  inputs = tf.nn.relu(inputs)
 
  return inputs

def _bottleneck_block_v2(inputs, filters, training, projection_shortcut, strides, data_format):

 

def block_layer(inputs, filters, bottleneck, block_fn, blocks, strides,training, name, data_format):
  # Bottleneck blocks end with 4x the number of filters as they start with
  filters_out = filters * 4 if bottleneck else filters
  # 短连接映射  主要参数是filters 用以调整通道数
  def projection_shortcut(inputs):
    return conv2d_fixed_padding(inputs=inputs, filters=filters_out, kernel_size=1, strides=strides, data_format=data_format)

  # 重复堆叠多次同样的残差块 (注意：每个block layer中的第一个block，即第一个残差块才需要做短连接映射)
  inputs = block_fn(inputs, filters, training, projection_shortcut, strides, data_format)
  for _ in range(1, blocks): #注意从1开始
    inputs = block_fn(inputs, filters, training, None, 1, data_format) # block_fn才是block_layer的计算函数

  return tf.identity(inputs, name)
  
################################################################################
# 定义ResNet模型类
################################################################################
class Model(object):
  def __init__(self,resnet_size, bottleneck, num_classes, num_filters,
               kernel_size,
               conv_stride, first_pool_size, first_pool_stride,
               second_pool_size, second_pool_stride, block_sizes, block_strides,
               final_size, version=DEFAULT_VERSION, data_format=None,
               dtype=DEFAULT_DTYPE):
    self.resnet_size = resnet_size # ResNet的size？？？？，整型

    if not data_format:   # 输入数据格式，channels_first还是channels_last。
      data_format = ('channels_first' if tf.test.is_built_with_cuda() else 'channels_last') #注意此处没有self，即此为检查更正用户输入的作用 此处括号为语法需要（可以不加）。 注意：此种操作使得data_format参数不受用户影响。如果用cuda的话，则改为channels_first，否则不用，因为cuda在channels_first时可以大幅提升性能

    self.resnet_version = version # 1或2选择使用resnet_v1 还是resnet_v2 （两者主要差别是BN层的位置）
    if version not in (1, 2):
      raise ValueError('Resnet version should be 1 or 2. See README for citations.')

    # 决定选用哪种残差块（共4中可选）
    self.bottleneck = bottleneck
    if bottleneck:
      if version == 1:
        self.block_fn = _bottleneck_block_v1
      else:
        self.block_fn = _bottleneck_block_v2
    else:
      if version == 1:
        self.block_fn = _building_block_v1
      else:
        self.block_fn = _building_block_v2
    
    if dtype not in ALLOWED_TYPES:  # 数据类型，一律使用float32型（指定这个参数的好处是起到提醒作用）
      raise ValueError('dtype must be one of: {}'.format(ALLOWED_TYPES))

    self.data_format = data_format  #默认是None，在实例化类之前程序会自动选择一个，此处可以选择人为覆盖?????
    self.num_classes = num_classes
    self.num_filters = num_filters  #????
    self.kernel_size = kernel_size  
    self.conv_stride = conv_stride
    self.first_pool_size = first_pool_size
    self.first_pool_stride = first_pool_stride
    self.second_pool_size = second_pool_size
    self.second_pool_stride = second_pool_stride
    self.block_sizes = block_sizes
    self.block_strides = block_strides  # 跨越的层数？？？？？？
    self.final_size = final_size   #????? 
    self.dtype = dtype



  # 可以用来生成一个variable  具体的是利用getter 然后根据需要转换类型   还不是很明确？？？？？？
  def _custom_dtype_getter(self, getter, name, shape=None, dtype=DEFAULT_DTYPE,*args, **kwargs):  # getter相当于tf.get_variable
    if dtype in CASTABLE_TYPES:
      var = getter(name, shape, tf.float32, *args, **kwargs)
      return tf.cast(var, dtype=dtype, name=name + '_cast')
    else:
      return getter(name, shape, dtype, *args, **kwargs)
   
  def _model_variable_scope(self):
    return tf.variable_scope('resnet_model', custom_getter=self._custom_dtype_getter)  #在该上下文中的变量都？？？？？




 
  def __call__(self, inputs, training):  # 模型的输入为inputs和training
    """
    参数:
      inputs: 一个Tensor 表示一个batch的输入图片
      training: boolean型，代表是否采用训练模式，因为训练和测试有少部分位置的代码不一致
    返回:
      分类预测结果一个logits Tensor，shape为[<batch_size>, self.num_classes].
    """
    with self._model_variable_scope():
      # 如果是channels_first 则将输入调整一下，这样在GPU上可以巨幅提升性能（因为默认python读入的图片都是channels_last的，所以input是channels_last的）
      if self.data_format == 'channels_first':  
        inputs = tf.transpose(inputs, [0, 3, 1, 2])  # 转置为channels_last
      
      # 第一个卷积层
      inputs = conv2d_fixed_padding(inputs=inputs, filters=self.num_filters, kernel_size=self.kernel_size, strides=self.conv_stride, data_format=self.data_format)
      inputs = tf.identity(inputs, 'initial_conv') # 返回一个一模一样的tensor 但是不同于直接用等号赋值，该方式会在计算图中形成一个op，而直接赋值不会

      # 池化层
      if self.first_pool_size:
        inputs = tf.layers.max_pooling2d(inputs=inputs, pool_size=self.first_pool_size, strides=self.first_pool_stride, padding='SAME', data_format=self.data_format)
        inputs = tf.identity(inputs, 'initial_max_pool')

      for i, num_blocks in enumerate(self.block_sizes):
        num_filters = self.num_filters * (2**i)   # num_filters指代第一个卷积层使用的filter数量(64)
        inputs = block_layer(inputs=inputs, filters=num_filters, bottleneck=self.bottleneck, block_fn=self.block_fn, blocks=num_blocks, strides=self.block_strides[i], training=training, name='block_layer{}'.format(i + 1), data_format=self.data_format) # 表示一个conv_x的结构，其中block_fn指一个building block的计算方法(依据不同版本而不同)
      
      inputs = batch_norm(inputs, training, self.data_format)
      inputs = tf.nn.relu(inputs)


      # 平均池化
      axes = [2, 3] if self.data_format == 'channels_first' else [1, 2]
      inputs = tf.reduce_mean(inputs, axes, keepdims=True)
      inputs = tf.identity(inputs, 'final_reduce_mean')

      inputs = tf.reshape(inputs, [-1, self.final_size])
      inputs = tf.layers.dense(inputs=inputs, units=self.num_classes)
      inputs = tf.identity(inputs, 'final_dense')
      return inputs


