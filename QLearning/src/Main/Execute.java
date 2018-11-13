package Main;

import java.util.List;

import Table.QTable;
import Table.RewardTable;

public class Execute {
	public static final double GAMA=0.8;
	public static void main(String[] args) {
		QTable qtable=new QTable();
		RewardTable rewardtable=new RewardTable();
		int repeats=0;//��������
		//ѭ��ֱ������
		while(repeats<100){
			//�½�һ��Episode
			Episode episode =new Episode();
			while(!episode.EpisodeEnd()){
				int backState=episode.state;//����״̬
				//ִ��һ������������״̬�����ض����ͽ���ֵ,ͬʱ�ı�episode״̬
				List<Integer> actionreward=episode.generateAction();
				int presentReward=actionreward.get(1);
				int action=actionreward.get(0);
				//��ȡ�¸�״̬������ۼƽ���
				int maxReward=Math.max(Math.max(rewardtable.rewards[episode.state][0], rewardtable.rewards[episode.state][0]), 
						Math.max(rewardtable.rewards[episode.state][0], rewardtable.rewards[episode.state][0]));
				//����QTable
				qtable.updateQTable((int)(presentReward+GAMA*maxReward),backState,action);
			}
		}
		
		for(int i=0;i<8;i++){
			for (int j = 0; j < 4; j++) {
				System.out.println(" "+qtable.Q[i][j]);
			}
		}

	}

}
