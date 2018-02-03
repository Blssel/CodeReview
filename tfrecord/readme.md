
# jieshao
TF框架中多处使用了protocol buffer，protocol buffer全称Google Protocol Buffer，简称Protobuf，是一种结构化数据存储格式，类似于常见的Json和xml，而且这种格式经过编译可以生成对应C++或Java或Python类的形式，即可以用编程语言读取或修改数据，不仅如此，还可以进一步将定义的结构化数据进行序列化，转化成二进制数据存下来或发送出去，非常适合做数据存储或 RPC 数据交换格式。更具体的介绍可以参考网上比较推荐的文章：[Google Protocol Buffer 的使用和原理](https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/)。其实TensorFlow计算图思想的实现也是[基于protocol buffer](https://zhuanlan.zhihu.com/p/31308381)的，感兴趣的可以看一下，本文主要介绍TFRecords，TFRecords是TF官方推荐使用的数据存储形式，也是使用了protocol buffer，下面详细介绍其使用方法和原理。

# use
参考[Google Protocol Buffer 的使用和原理](https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/)可以发现，要得到本地存储的序列化数据，需要先定义.proto 文件，再编译成编程语言描述的类，然后实例化该类（该类也已自动生成setter getter修改类和序列化类等方法），并序列化保存到本地或进行传输。TFRecords的思想也是将数据集中的数据以结构化的形式存到.proto中，然后序列化存储到本地，方便使用时读取并还原数据，只不过TF又对这个过程进行了一点封装，看起来和protocol buffer原始的使用方式略有差别。

protocol buffer中需要先将数据以结构化文件.proto的格式展现，然后可以编译成C++ Java 或python类进行后续操作，在TFRecords的应用中`tf.train.Example`类就是扮演了这一角色，TF中它的原始.proto文件定义在`tensorflow/core/example/example.proto`中,如下代码片:
```C++
message Example {
  Features features = 1;
};
```
可以看到Example类中封装的数据应该是`features`,是`Features`类型的，而`Features`在python代码中就对应了`tf.train.Features`类,其原始.proto文件定义在`tensorflow/core/example/feature.proto`中，如下代码片：
```
message Features {
  // Map from feature name to feature.
  map<string, Feature> feature = 1;
};
```
可以看到，`Features`中的数据又是`feature`（注意没有s），而`feature`属性的类型是`map<string, Feature>`类型，`string`不必说了，关键是`Feature`类型，和`Features`一样，`Feature`对应`tf.train.Feature`类，其原始.proto文件也定义在`tensorflow/core/example/feature.proto`中，如下代码片:
```
message Feature {
  // Each feature can be exactly one kind.
  oneof kind {
    BytesList bytes_list = 1; # bytes_list float_list int64_list也是和之前一样，对应一个类
    FloatList float_list = 2;
    Int64List int64_list = 3;
  }
};
```

# TFRecords
TFRecords的定义过程就是使用了刚介绍的几个类：`tf.train.Example`，`tf.train.Features`，`tf.train.Feature`，知道了这几个类的定义以及它们的嵌套关系，再去理解TFRecords的产生就容易多了。
首先，使用tf.train.Example来封装我们的数据，然后使用tf.python_io.TFRecordWriter来写入磁盘，其中几个类的的嵌套方式和上述一致，见如下代码：

```python
#本段代码来自[TensorFlow高效读取数据](http://ycszen.github.io/2016/08/17/TensorFlow%E9%AB%98%E6%95%88%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE/)

import os
import tensorflow as tf 
from PIL import Image
cwd = os.getcwd()
'''
此处我加载的数据目录如下：
0 -- img1.jpg
     img2.jpg
     img3.jpg
     ...
1 -- img1.jpg
     img2.jpg
     ...
2 -- ...
...
'''
# 先定义writer对象，writer负责将得到的记录写入TFRecords文件，此处为train.tfrecords文件
writer = tf.python_io.TFRecordWriter("train.tfrecords")
for index, name in enumerate(classes):
class_path = cwd + name + "/"
  # 一张一张的写入TFRecords文件
  for img_name in os.listdir(class_path):
    img_path = class_path + img_name
    img = Image.open(img_path)
    img = img.resize((224, 224)) #对图片做一些预处理操作
    img_raw = img.tobytes()     #将图片转化为原生bytes
    # 封装仅Example对象中
    example = tf.train.Example(features=tf.train.Features(feature={
            "label": tf.train.Feature(int64_list=tf.train.Int64List(value=[index])),
            'img_raw': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_raw]))
        }))
    writer.write(example.SerializeToString())  #序列化为字符串并写入磁盘
writer.close()
```

# 读取数据



























# 参考
[TensorFlow高效读取数据](http://ycszen.github.io/2016/08/17/TensorFlow%E9%AB%98%E6%95%88%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE/)
[Google Protocol Buffer 的使用和原理](https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/)
