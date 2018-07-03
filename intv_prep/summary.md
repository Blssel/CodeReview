# 优化方法
## 梯度下降
### 梯度下降
首先必须谈一下最原始的随机梯度下降法(Vanilla gradient descent或称Batch gradient descent)。我们执行优化的目的是让损失函数在整个训练集上达到全局最优（当然为了避免过拟合，往往不需要真正达到最优），原始的梯度下降法每次参数更新操作都是在整个数据集上进行的，但这样做存在两个缺点：**第一**，训练效率低。因为每做一个小的梯度更新都需要在整个训练集上进行一次计算，代价太大。**第二**，冗余计算。训练集中有许多相似样本，对于梯度跟新来讲，其实只要计算其中一个就够了，无须全部计算。

### 随机梯度下降(SGD)
随机梯度下降(Stochastic gradient descent)每次参数更新只考虑一个样本。它可以很好的克服上述缺点，但也存在自己的问题，那就是每次梯度下降的方向都存在极大地不确定性，归根到底还是样本量太小导致的，因此该方法在收敛过程中波动非常大，收敛速度非常慢，如下图所示。

![](https://note.youdao.com/yws/public/resource/3f007aef5f79a9fa8a01b51a43ab1108/xmlnote/WEBRESOURCE8a6a36866825e6a6015840ed991d3c6d/23072)

### Mini-batch 随机梯度下降(Mini-batch SGD)
Mini-batch gradient descent比较合适的在前两者之间取得了一个trade-off，在减小训练波动性的情况下提升了训练效率。
> 随机梯度下降系列方法共同的缺点：
> - learning rate比较难设置，太小收敛太慢，太大，产生波动性或无法收敛;
> - 对于数据中出现比较频繁的样本，希望更小的学习率，而对那些稀有样本则希望增大学习率，该类方法无法胜任;
> - 可能获得的是次优解而非最优解(容易陷入鞍点附近无法跳出)

## 常用优化策略或算法
### Momentum
尽管Mini-batch gradient descent能够一定程度的解决优化时的不稳定性，但也只能是缓解而已，并非是从本质上解决的，Momentum在此基础上可以进一步缓解该问题，Momentum累积之前每次计算得到的梯度，并以一定的比率α衰减，同时以1-α的衰减加入新计算的梯度。这样的好处就是可以避免噪音数据带来的梯度更新方向的偏移，从而更快的收敛，同时，还可以一定程度的缓解因显存不够而导致的batch size设置不上去带来的无法收敛的尴尬。
下面是Momentum的优化公式:

![](https://note.youdao.com/yws/public/resource/3f007aef5f79a9fa8a01b51a43ab1108/xmlnote/WEBRESOURCE599231a8b98a3dc733462ce145718a0e/23074)

### Nesterov accelerated gradient

### Adagrad


### RMSProp 算法
RMSProp（Root Mean Square Prop，均方根支）算法是在对梯度进行指数加权平均的基础上，引入平方和平方根。具体过程为（省略了 l）：

### Adam

## 如何选择优化算法 
# 激活函数及其优缺点
