import numpy as np
import random

def Network(object):
	def __init__(self,sizes):
		self.num_layers=len(sizes)
		biases=[np.random.randn(y,1) for y in sizes[1:]]
		weights=[np.random.randn(y,x) for (x,y) in zip(sizes[:-1],sizes[1:])]
	
	def feedforward(a):
		
		
	def SGD(self,training_datas,epochs,mini_batch_size,eta,test_data=None):
		training_datas=training_datas.shuffle()
		for j in xrange(epochs)
		batchs=[training_datas[k:k+mini_batch] for k in xrange(training_datas.size())]
		for batch in batchs:
			self.update(batch,eta)
	
	
	
	#更新针对一个batch
	def update(self,batch,eta):
		#定义一个权重和偏置的list，盛放batch中所求梯度和偏置的和
		sum_delta_biases=[np.zero(y) for y in self.biases]
		sum_delta_weights=[np.zero(y) for y in self.weights]
		for x,y in batch:
			one_biases,one_weights=self.backpropgation()
			sum_delta_biases=[sdb+ob for sdb ob in zip(sum_delta_biases,one_biases)]
			sum_delta_weights=[sdw+ow for sdw,ow in zip(sum_delta_weights,one_weights)]
		#更新参数
		self.biases=[bs-eta/len(batch)*sdb for bs,sdb in zip(self.biases,sum_delta_biases)]
		self.weights=[ws-eta/len(batch)*sdw for ws,sdw in zip(self.weights,sum_delta_weights)]

		
		
		
	#反向传播是针对一个输入数据的
	def backpropgation(self,s,y):
		delt_weights=[np.zero(y.shape) for y in self.weights]
		delt_biases=[np.zero(y.shape) for y in self.biases]
		as=[x]
		zs=[]
		a=x
		for w,b in zip(self.weights,self.biases):
			z=np.dot(w,x)+b
			zs.append(z)
			a=self.sigmoid(z)
			as.append(z)
		#计算L层错误量
		delta=(as[-1]-y)*sigmoid_der(zs[-1])
		#计算L层上的w和b的偏导数
		delt_biases[-1]=delta
		delt_weights[-1]=np.dot(delta,as[-2].transpose())
		#错误量反传的同时计算两个梯度
		for i in xrange(2,len(self.weights)):
			#反传误差
			delta=np.dot(self.weights[-i+1].transpose(),delt)*sigmoid_der(z[-i])
			delt_biases[-i]=delta
			delt_weights[-i]=np.dot(delta,as[-i-1].transpose())
		return (delt_biases,delt_weights)
		
	
	
def sigmoid(z):
	a=1.0/(1.0+exp(z))
	return a

	

def main()
	Network([8,15,8])
		