
# 先修知识——protocol buffer
TF框架中多处使用了protocol buffer，protocol buffer全称Google Protocol Buffer，简称Protobuf，是一种结构化数据存储格式，类似于常见的Json和xml，而且这种格式经过编译可以生成对应C++或Java或Python类的形式，即可以用编程语言读取或修改数据，不仅如此，还可以进一步将定义的结构化数据进行序列化，转化成二进制数据存下来或发送出去，非常适合做数据存储或 RPC 数据交换格式。更具体的介绍可以参考网上比较推荐的文章：[Google Protocol Buffer 的使用和原理](https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/)。其实TensorFlow计算图思想的实现也是[基于protocol buffer](https://zhuanlan.zhihu.com/p/31308381)的，感兴趣的可以看一下，本文主要介绍TFRecords，TFRecords是TF官方推荐使用的数据存储形式，也是使用了protocol buffer，下面详细介绍其使用方法和原理。

### protocol buffer的使用
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

# 将数据集转化成TFRecords形式
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
以上存储数据时，`Example`调用`SerializeToString()`方法将自己序列化并由`writer = tf.python_io.TFRecordWriter("train.tfrecords")`对象保存，最终是将所有的图片文件和label保存到同一个tfrecords文件`train.tfrecords`中了。读取数据则以上过程的逆，先获取序列化数据，再解析：由`tf.python_io.tf_record_iterator("train.tfrecords")`方法(注意这个是方法)返回所有本地序列化文件迭代器，然后由`Example`调用`ParseFromString()`方法解析，代码如下：
```python
for serialized_example in tf.python_io.tf_record_iterator("train.tfrecords"):
  # 本段代码来自[TensorFlow高效读取数据](http://ycszen.github.io/2016/08/17/TensorFlow%E9%AB%98%E6%95%88%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE/)
  example = tf.train.Example()
  # 进行解析
  example.ParseFromString(serialized_example)
  # 逐个读取example对象里封装的东西
  image = example.features.feature['image'].bytes_list.value
  label = example.features.feature['label'].int64_list.value
  # 可以做一些预处理之类的
  print image, labe
```
这是最基本的数据读取方式，`tf.python_io.tf_record_iterator`方法每次解析一个`.tfrecords`文件。而在实际应用中，由于数据集往往很大，所以往往将数据分开保存至多个`tfrecords`文件中，在这种情况下，TF提供了其他的接口进行读取，所以正常情况下我们可能不会使用上述的数据读取方式，以下才是重点，但必须强调的是整体的思想是一致的，都是先获取序列化文件，然后解析，只是接口函数稍有不同。

TF的多线程训练是TF框架重新设计的，不是简单地使用python语言多线程来搞得，而且TF多线程是和TFRecords配套使用的，下面介绍的数据读取方法也是多线程训练的数据读取方式。[十图详解tensorflow数据读取机制](https://zhuanlan.zhihu.com/p/27238630)这篇文章深入浅出>的介绍了TF多线程读取数据和训练的原理，多线程这一块接口多，也比较难以理解，下面仅从使用的角度出发谈谈我个人的理解，不详细追究里面的实现原理。

假设我们按照上述方式将数据保存到了两个`tfrecords`文件中，分别为'1.tfrecords'和'2.tfrecords'，保存在DATA_ROOT路径中，那么我们分几步读取数据，参考如下代码：
- 1) 读取`tfrecords`文件名到队列中，使用`tf.train.string_input_producer`函数，该函数可以接收一个文件名列表，并自动返回一个对应的文件名队列`filename_queue`，之所以用队列是为了后续多线程考虑（队列和多线程经常搭配使用）
- 2) 实例化`tf.TFRecordReader()`类生成`reader`对象，接收`filename_queue`参数，并读取该队列中文件名对应的文件，得到`serialized_example`(读到的就是.tfrecords序列化文件)
- 3) 解析，注意这里的解析不是用的`Example`对象里的函数，而是`tf.parse_single_example`函数，该函数能从`serialized_example`中解析出一条数据，当然也可以用`tf.parse_example`解析多条数据，此处暂不赘述。这里`tf.parse_single_example`函数传入参数`serialized_example`和`features`，其中`features`是字典的形式，指定每个key的解析方式，比如`image_raw`使用`tf.FixedLenFeature`方法解析，这种解析方式返回一个Tensor，大多数解析方式也都是这种，另一种是`tf.VarLenFeature`方法，返回`SparseTensor`，用于处理稀疏数据，不赘述。这里还要注意必须告诉解析函数以何种数据类型解析，这必须与生成`TFRecords`文件时指定的数据类型一致。最后返回`features`是一个字典，里面存放了每一项的解析结果。
- 4) 最后只要读出`features`中的数据即可。比如，`features['label']`,`features['pixels']`。但要注意的是，此时的`image_raw`依然是字符串类型的(可以看写入代码中的`image_raw`)，需要进一步还原成像素数组，用TF提供的函数`tf.decode_raw`来搞定`images = tf.decode_raw(features['image_raw'],tf.uint8)`。

至此，就定义好了完成一次数据读取的代码，有了它，下面的训练时的多线程方法就有了数据来源，下节讨论。
```python
# 读取文件。
filename_queue = tf.train.string_input_producer(["Records/output.tfrecords"])
reader = tf.TFRecordReader()
_,serialized_example = reader.read(filename_queue)

# 解析读取的样例。
features = tf.parse_single_example(
    serialized_example,
    features={
        'image_raw':tf.FixedLenFeature([],tf.string),
        'pixels':tf.FixedLenFeature([],tf.int64),
        'label':tf.FixedLenFeature([],tf.int64)
    })

images = tf.decode_raw(features['image_raw'],tf.uint8)
labels = tf.cast(features['label'],tf.int32) #需要用tf.cast做一个类型转换
pixels = tf.cast(features['pixels'],tf.int32)

# 下面的代码下节讨论
sess = tf.Session()

# 启动多线程处理输入数据。
coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess,coord=coord)

for i in range(10):
    image, label, pixel = sess.run([images, labels, pixels])
```

# TF多线程机制
假设已将数据集文件转换成了`TFRecords`格式，共两个文件，每个文件中存储两条数据，两个文件如下，下面用多线程的方式读取并训练，分为以下几个步骤：
```shell
/patah/to/data.tfrecords-00000-of-00002
/patah/to/data.tfrecords-00001-of-00002
```
- 1) 获取`TFRecords`文件队列。TF提供了`tf.train.match_filenames_once`函数帮助获取所有满足条件的`TFRecords`文件，`tf.train.match_filenames_once`函数参数为正则表达式，返回匹配上的所有文件名集合变量。当然，也可以选择不用该函数，用纯python也可以匹配，python的话最终返回一个list类型即可，但正规起见，还是推荐使用TF提供的方法。然后`tf.train.string_input_producer`函数依此生成文件名队列`filename_queue`。
```python
files = tf.train.match_filenames_once("/patah/to/data.tfrecords-*") # 
filename_queue = tf.train.string_input_producer(files, shuffle=False)
```
- 2) 解析`TFRecords`文件中的数据，和上面一样，不赘述。
```python
# 读取文件。
reader = tf.TFRecordReader()
_,serialized_example = reader.read(filename_queue)

# 解析读取的样例。
features = tf.parse_single_example(
    serialized_example,
    features={
        'image_raw':tf.FixedLenFeature([],tf.string),
        'pixels':tf.FixedLenFeature([],tf.int64),
        'label':tf.FixedLenFeature([],tf.int64)
    })

decoded_images = tf.decode_raw(features['image_raw'],tf.uint8)
retyped_images = tf.cast(decoded_images, tf.float32)
#pixels = tf.cast(features['pixels'],tf.int32)
# 最后只要labels和images
labels = tf.cast(features['label'],tf.int32)
images = tf.reshape(retyped_images, [784])
```
- 3)将读取到的数据打包为batch。上一段代码得到了`labels`和`images`，这是一条数据，训练一次需要一个`batch`的数据，怎么搞？难道将上述代码用`for`循环反复执行`batch_size`次？这样做未尝不可，但效率很低，TF提供了`tf.train.shuffle_batch`函数，上述解析代码只要提供一次，然后将`labels`和`images`作为`tf.train.shuffle_batch`函数的参数，`tf.train.shuffle_batch`就能自动获取到一个batch的`labels`和`images`。`tf.train.shuffle_batch`函数获取`batch`的过程需要生成一个队列（加入计算图中），然后一个一个入队`labels`和`images`，然后出队组合batch。关于里面参数的解释，`batch_size`就是`batch`的大小，`capacity`指的是队列的容量，比如`capacity`设为1，而`batch_szie`为3，那么组成一个`batch`的过程中，出队的操作就会因为数据不足而频繁地被阻塞来等待入队加入数据，运行效率很低。相反，如果`capacity`被设置的很大，比如设为1000，而`batch_size`设置为3，那么入队操作在空闲时就会频繁入队，供过于求并非坏事，糟糕的是这样会占用很多内存资源，而且没有得到多少效率上的提升。还有一点值得注意，当使用`tf.train.shuffle_batch`时，为了使得`shuffle`效果好一点，出队后队列剩余元素必须得足够多，因为太少的话也没什么必要打乱了，因此`tf.train.shuffle_batch`函数要求提供`min_after_dequeue`参数来保证出队后队内元素足够多，这样队列就会等队内元素足够多时才会出队。显而易见，`capacity`必须大于`min_after_dequeue`。关于`capacity`和`min_after_dequeue`的设置，参考《TensorFlow 实战Google深度学习框架》，给出了设置`capacity`大小的一种比较科学的方式，`min_after_dequeue`根据数据集大小和`batch_size`综合考虑，而`capacity`则设置为$capacity= min_after_dequeue+ 3*batch_size$，在效率和资源占用之间取得平衡。组合`batch_size`的代码如下：
```python
min_after_dequeue = 10000
batch_size = 100
capacity = min_after_dequeue + 3 * batch_size

image_batch, label_batch = tf.train.shuffle_batch([images, labels], 
                                                    batch_size=batch_size, 
                                                    capacity=capacity, 
                                                    min_after_dequeue=min_after_dequeue)
```

- 4) 启动多线程训练模型。训练过程和单线程的基本一致，唯一的区别就是多了一个`tf.train.start_queue_runners`函数，这个函数中传入参数`sess`,就可以做到多线程训练，具体地细节还不是很了解，但照壶画瓢应该没问题了，有空再深挖下。
```python
# 前向传播
y = inference(image_batch)
    
# 计算交叉熵及其平均值
cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=label_batch)
cross_entropy_mean = tf.reduce_mean(cross_entropy)
    
# 计算最后的损失函数（加入正则化）
regularizer = tf.contrib.layers.l2_regularizer(REGULARAZTION_RATE)
regularaztion = regularizer(weights1) + regularizer(weights2)
loss = cross_entropy_mean + regularaztion

# 优化损失函数
train_step = tf.train.GradientDescentOptimizer(0.01).minimize(loss)
    
# 初始化会话，并开始训练过程。
with tf.Session() as sess:
  # 初始化所有变量
  tf.global_variables_initializer().run()
   
  coord = tf.train.Coordinator()

  threads = tf.train.start_queue_runners(sess=sess, coord=coord)
  # 循环的训练神经网络。
  for i in range(TRAINING_STEPS):
    if i % 1000 == 0:
      print("After %d training step(s), loss is %g " % (i, sess.run(loss)))              
    sess.run(train_step) 

    coord.request_stop()
    coord.join(threads
```









# 参考
[TensorFlow高效读取数据](http://ycszen.github.io/2016/08/17/TensorFlow%E9%AB%98%E6%95%88%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE/)

[Google Protocol Buffer 的使用和原理](https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/)
