package Table;

public class QTable {
	//定义Q表
	public int[][] Q=new int[8][4];
	//初始化Q表
	public QTable(){
		for(int i=0;i<8;i++)
			for(int j=0;j<4;j++)
				this.Q[i][j]=0;
	}
	//更新QTable
	public void updateQTable(int q,int x,int y){
		if(q>Q[x][y]){
			Q[x][y]=q;
		}
	}
}
