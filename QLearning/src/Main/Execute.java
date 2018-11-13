package Main;

import java.util.List;

import Table.QTable;
import Table.RewardTable;

public class Execute {
	public static final double GAMA=0.8;
	public static void main(String[] args) {
		QTable qtable=new QTable();
		RewardTable rewardtable=new RewardTable();
		int repeats=0;//迭代次数
		//循环直至收敛
		while(repeats<100){
			//新建一个Episode
			Episode episode =new Episode();
			while(!episode.EpisodeEnd()){
				int backState=episode.state;//备份状态
				//执行一个动作并更新状态，返回动作和奖赏值,同时改变episode状态
				List<Integer> actionreward=episode.generateAction();
				int presentReward=actionreward.get(1);
				int action=actionreward.get(0);
				//获取下个状态的最大累计奖赏
				int maxReward=Math.max(Math.max(rewardtable.rewards[episode.state][0], rewardtable.rewards[episode.state][0]), 
						Math.max(rewardtable.rewards[episode.state][0], rewardtable.rewards[episode.state][0]));
				//更新QTable
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
