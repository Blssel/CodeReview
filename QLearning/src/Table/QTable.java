package Table;

public class QTable {
	//����Q��
	public int[][] Q=new int[8][4];
	//��ʼ��Q��
	public QTable(){
		for(int i=0;i<8;i++)
			for(int j=0;j<4;j++)
				this.Q[i][j]=0;
	}
	//����QTable
	public void updateQTable(int q,int x,int y){
		if(q>Q[x][y]){
			Q[x][y]=q;
		}
	}
}
