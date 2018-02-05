随着TF的不断发展，许多旧的模式或接口不断被性能更佳，更科学的版本替代，在AI急速发展的今天我们需要紧跟潮流，因为一不小心你就发现，你用的东西已经被淘汰了， 而别人用的新东西你却看不懂。今天，就对TF中的数据读取方式做个最新总结，给卡在第一步的小伙伴一个引导。

现在TF的最新版本是TF1.5，版本更新的特别快，到1.5版本为止，TF中数据读取方式共有4种，其中官方推荐使用的是Datasets API（于1.3版本正式推出）。在TF1.2版本的时候，官方文档中对数据读取的描述有三种，并且没有绝对推荐哪一种，但从1.3版本开始，新增了Datasets API，官方直接推荐使用Datasets API，之前的三种由于各自有其适用性并未淘汰，只是在描述时变成了“推荐使用Datasets API，除此之外还有另外3种读取方式”。这三种方式分别是：
> Feeding方式：也就是常见的placeholder+feed的方式，使用python的for来循环进行每一步的训练，在每一步的开始将python代码读取到的数据feed给placeholder，这种方式在很多经典教程里很常见。
> 从文件（磁盘）中读取数据：就是之前介绍的TFRecords的方式，这种方式中数据是通过pipeline读取到TF计算图的开头的，支持多线程。
> 预加载数据：这种方式比较鸡肋，就是直接将输入做成一个常量类型（constant）固化在计算图中，估计除了测试代码很少会用这种方式。

本文主要介绍TF主推的Datasets API，一切以1.5版本为参考。

该方法涉及的模块是`tf.data`模块，这个模块的设计采用了管道(pipeline)模式，它可以将文件系统中的文件读取出来，通过管道呈现给用户可以直接送入神经网络训练的数据，用户完全不用考虑技术细节，比如，这个管道可以从分布式文件系统中将你指定的文件读取并拼凑出来，然后你可以指定对图片做一些预处理(比如随机抖动)，组成你指定大小的batch输出出来供训练使用。总之，用户只需使用它提供的接口即可，完全不必考虑内部的实现细节！

`tf.data`模块同时也是个包，里面包含了读取数据所需的几个核心模块，`tf.data`定义在`tensorflow/python/data/__init__.py`中，可以大致看一下：
```python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# pylint: disable=unused-import
from tensorflow.python.data.ops.dataset_ops import Dataset
from tensorflow.python.data.ops.iterator_ops import Iterator
from tensorflow.python.data.ops.readers import FixedLengthRecordDataset
from tensorflow.python.data.ops.readers import TextLineDataset
from tensorflow.python.data.ops.readers import TFRecordDataset
# pylint: enable=unused-import

from tensorflow.python.util.all_util import remove_undocumented
remove_undocumented(__name__)
```

# 用Datasets API读取数据
用Datasets API读取数据主要分为以下几个步骤：
- 1) 创建`tf.data.Dataset`对象。`tf.data.Dataset`类可以读入任何数据并封装。创建`Dataset`对象需要借助`Dataset`本身提供的方法，最常见的是`tf.data.Dataset.from_tensors() `和`tf.data.Dataset.from_tensor_slices()`方法，以后者为例(其详细作用见代码注释)，如下代码`Example1`中我们得到了一个`dataset`对象，该对象就代表了整个要用来训练的数据集，里面封装着所有文件的文件名和label，而这仅仅是文件名而已，并非真正的文件内容，下面才是真正厉害的地方，只要再调用一个函数，就可以将`dataset`对象中的文件名转化为对应的文件内容（图片像素矩阵），如下代码`Example2`
```python
# Example1
filenames = tf.constant(["/var/data/image1.jpg", "/var/data/image2.jpg", ...])
labels = tf.constant([0, 37, ...])
# 此时dataset中的一个元素是(filename, label)
dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))

# Example2
def _parse_function(filename, label):
 image_string = tf.read_file(filename)
 image_decoded = tf.image.decode_image(image_string)
 image_resized = tf.image.resize_images(image_decoded, [28, 28])
 return image_resized, label

# 此时dataset中的一个元素是(image_resized, label)
dataset = dataset.map(_parse_function)
```
















在最新的TF中，对数据读取的方式

taset API是TensorFlow 1.3版本中引入的一个新的模块，主要服务于数据读取，构建输入数据的pipeline。

此前，在TensorFlow中读取数据一般有两种方法：

使用placeholder读内存中的数据

使用queue读硬盘中的数据（关于这种方式，可以参考我之前的一篇文章：十图详解tensorflow数据读取机制）

Dataset API同时支持从内存和硬盘的读取，相比之前的两种方法在语法上更加简洁易懂。此外，如果想要用到TensorFlow新出的Eager模式，就必须要使用Dataset API来读取数据。

本文就来为大家详细地介绍一下Dataset API的使用方法（包括在非Eager模式和Eager模式下两种情况）。








# 参考
[TensorFlow1.5官方文档:Importing Data](https://www.tensorflow.org/programmers_guide/datasets)
