#coding:utf-8
import numpy as np
  
#定义神经网络类
"""
定义神经网络首先要定义几个重要属性
1.各层神经元数量
2.层数
3.偏置（以矩阵list的形式）
4.权重（以矩阵list的形式）
"""
class Network(object):
    #初始化神经网络中的必要参数
	def __init__(self,size_each_layer):
        self.size_each_layer=size_each_layer
        self.num_layers=len(size_each_layer)
        self.biases=[np.random.randn(i,1) for i in self.size_each_layer[1:]]#定义偏置，每层偏置为一列
        self.weights=[np.random.randn(i,j) for i,j in zip(size_each_layer[1:],size_each_layer[:-1])]#定义权重，每层权重为一个矩阵
		
		
    #对于一个输入进行前向传播（传播过程中涉及的每层的中间结果都要保存）
    def feedforward(self,x)
        #定义各层z值和激活值
        z_list=[]
		a=x
        a_list=[x]#其中第一层算作激活值
        #前向传播并记录结果
        for b,w in zip(self.biases,self.weights):
			z=np.dot(w,a)+b
			a=sigmoid(z)
			z_list.append(z)
			a_list.append(a)
		return (z_list,a_list)
       
def main(): 
    n=Network([1,2]) 
	z,a=feedforward(1)
    print(z,a)
main()
