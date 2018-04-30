from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import tensorflow as tf

slim = tf.contrib.slim

# Block类继承collections.namedtuple('Block', ['scope', 'unit_fn', 'args'])类
class Block(collections.namedtuple('Block', ['scope', 'unit_fn', 'args'])):



def stack_blocks_dense(net,
                       blocks,
                       output_stride=None,
                       outputs_collections=None):
  """该函数创建堆叠的blocks  而且对每个block都创建不同的scopes：
  比如：'block_name/unit_1', 'block_name/unit_2'等

  并且，该函数灵活性很强，可以允许调整输出的尺寸。怎么实现的？？？


  Most ResNets consist of 4 ResNet blocks and subsample the activations by a
  factor of 2 when transitioning between consecutive ResNet blocks. This results
  to a nominal ResNet output_stride equal to 8. If we set the output_stride to
  half the nominal network stride (e.g., output_stride=4), then we compute
  responses twice.
  Control of the output feature density is implemented by atrous(??) convolution.
  
  参数：

  """

  current_stride = 1

  rate = 1

  for block in blocks:
    with tf.variable_scope(block.scope, 'block', [net]) as sc:
      for i, unit in enumerate(block.args):
        if output_stride is not None and current_stride > output_stride:
          raise ValueError('The target output_stride cannot be reached.')

      with variable_scope.variable_scope('unit_%d' % (i + 1), values=[net]):
          # If we have reached the target output_stride, then we need to employ
          # atrous convolution with stride=1 and multiply the atrous rate by the
          # current unit's stride for use in subsequent layers.
          if output_stride is not None and current_stride == output_stride:
            net = block.unit_fn(net, rate=rate, **dict(unit, stride=1))
            rate *= unit.get('stride', 1)

          else:
            net = block.unit_fn(net, rate=1, **unit)
            current_stride *= unit.get('stride', 1)


































