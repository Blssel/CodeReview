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

import collections
import tensorflow as tf

slim = tf.contrib.slim


class Block(collections.namedtuple('Block',['scope','unit_fn','args'])):
  """Block类，用来存放每一个Block的卷积指标
  该类没有具体地方法，采用继承的方式
  比如：Block('block1',botlleneck,[(256,64,1),(256,64,1),(256,64,2)])
  代表block1这个block由3个残差块组成：①scope为block1
                                      ②采用bottleneck方式
                                      ③第一个残差块的通道数为64,64,256，且中间层的步长为1
                                       第二个残差块的通道数为64,64,256，且中间层的步长为1
                                       第三个残差块的通道数为64,64,256，且中间层的步长为2
  """

def subsample(inputs, factor, scope=None):
  """使用1×1的核做降采样（采用max pooling方式）
  其中factor指采样因子，也就是步长！！如果为1，则相当于什么也不做
  """
  if factor == 1:
    return inputs
  else:
    return slim.max_pool2d(inputs, [1, 1], stride=factor, scope=scope)

def conv2d_same(inputs, num_outputs, kernel_size, stride, rate=1, scope=None):
  """
  卷积 保证卷积前后spatial尺寸不变
  """
  if stride == 1:
    return slim.conv2d(inputs, num_outputs, kernel_size, stride=1, rate=rate, padding='SAME', scope=scope)
  else:
    kernel_size_effective = kernel_size + (kernel_size - 1) * (rate - 1)
    pad_total = kernel_size_effective - 1
    pad_beg = pad_total // 2
    pad_end = pad_total - pad_beg
    inputs = tf.pad(inputs,[[0, 0], [pad_beg, pad_end], [pad_beg, pad_end], [0, 0]])
    return slim.conv2d(inputs, num_outputs, kernel_size, stride=stride, rate=rate, padding='VALID', scope=scope)


def stack_blocks_dense(net, blocks, output_stride=None, store_non_strided_activations=False, outputs_collections=None):
  """

  """
  # The current_stride variable keeps track of the effective stride of the
  # activations. This allows us to invoke atrous convolution whenever applying
  # the next residual unit would result in the activations having stride larger
  # than the target output_stride.
  current_stride = 1

  # The atrous convolution rate parameter.
  rate = 1

  for block in blocks:
    with tf.variable_scope(block.scope, 'block', [net]) as sc:
      block_stride = 1
      for i, unit in enumerate(block.args):
        if store_non_strided_activations and i == len(block.args) - 1:
          # Move stride from the block's last unit to the end of the block.
          block_stride = unit.get('stride', 1)
          unit = dict(unit, stride=1)

        with tf.variable_scope('unit_%d' % (i + 1), values=[net]):
          # If we have reached the target output_stride, then we need to employ
          # atrous convolution with stride=1 and multiply the atrous rate by the
          # current unit's stride for use in subsequent layers.
          if output_stride is not None and current_stride == output_stride:
            net = block.unit_fn(net, rate=rate, **dict(unit, stride=1))
            rate *= unit.get('stride', 1)

          else:
            net = block.unit_fn(net, rate=1, **unit)
            current_stride *= unit.get('stride', 1)
            if output_stride is not None and current_stride > output_stride:
              raise ValueError('The target output_stride cannot be reached.')
  # Collect activations at the block's end before performing subsampling.
      net = slim.utils.collect_named_outputs(outputs_collections, sc.name, net)

      # Subsampling of the block's output activations.
      if output_stride is not None and current_stride == output_stride:
        rate *= block_stride
      else:
        net = subsample(net, block_stride)
        current_stride *= block_stride
        if output_stride is not None and current_stride > output_stride:
          raise ValueError('The target output_stride cannot be reached.')

  if output_stride is not None and current_stride != output_stride:
    raise ValueError('The target output_stride cannot be reached.')

  return net


def bottleneck(inputs,
               depth,
               depth_bottleneck,
               stride,
               rate=1,
               outputs_collections=None,
               scope=None,
               use_bounded_activations=False):

  with tf.variable_scope(scope, 'bottleneck_v1', [inputs]) as sc:
    depth_in = utils.last_dimension(inputs.get_shape(), min_rank=4)
    if depth == depth_in:
      shortcut = resnet_utils.subsample(inputs, stride, 'shortcut')
    else:
      shortcut = layers.conv2d(
          inputs,
          depth, [1, 1],
          stride=stride,
          activation_fn=None,
          scope='shortcut')

    residual = layers.conv2d(
        inputs, depth_bottleneck, [1, 1], stride=1, scope='conv1')
    residual = resnet_utils.conv2d_same(
        residual, depth_bottleneck, 3, stride, rate=rate, scope='conv2')
    residual = layers.conv2d(
        residual, depth, [1, 1], stride=1, activation_fn=None, scope='conv3')

    output = nn_ops.relu(shortcut + residual)

    return utils.collect_named_outputs(outputs_collections, sc.name, output)











def resnet_v1(inputs,
              blocks,
              num_classes=None,
              is_training=True,
              global_pool=True,
              output_stride=None,
              include_root_block=True,
              spatial_squeeze=True,
              store_non_strided_activations=False,
              reuse=None,
              scope=None):
  """ResNet_v1模型的前向传播函数
  参数：
    inputs, 
    blocks???
    num_classes, is_training, 
    global_pool??
    output_stride??
  返回：

  """
  with tf.variable_scope(scope, 'resnet_v1', [inputs], reuse=reuse) as sc:  #此处scope??
    end_points_collection = sc.original_name_scope + '_end_points'   # original_name_scope????
    with slim.arg_scope([slim.conv2d, bottleneck, resnet_utils.stack_blocks_dense], outputs_collections=end_points_collection): # 规定这些操作的outputs_collections值
      with slim.arg_scope([slim.batch_norm], is_training=is_training):
        net = inputs
        # 如果包含前两层，7×7卷积层和池化层
        if include_root_block:
          if output_stride is not None:
            if output_stride % 4 != 0:
              raise ValueError('The output_stride needs to be a multiple of 4.')
            output_stride /= 4
          net = resnet_utils.conv2d_same(net, 64, 7, stride=2, scope='conv1') # 第一层7×7的卷积层，stride=2，filters=64
          net = slim.max_pool2d(net, [3, 3], stride=2, scope='pool1') # 紧跟池化层，3×3，stride=2
      
        # 堆叠的blocks
        net = resnet_utils.stack_blocks_dense(net, blocks, output_stride,
                                              store_non_strided_activations)
