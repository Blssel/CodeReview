package Main;

import java.util.ArrayList;
import java.util.List;

import Table.RewardTable;

public class Episode {
	int state;
	//�������һ��λ�ã������ж�������ԣ���Ϊ������������״̬��
	public Episode(){
		do{
			this.state=7*(int)Math.random();
		}while(this.state>=5&&state<=7);
	}
	//��Ե�ǰ״̬�������һ������Ķ���,���ض����ͽ���ֵ,���ı�״̬
	public List<Integer> generateAction(){
		List<Integer> actionreward=new ArrayList<>();
		int action;
		do{
			action=3*(int)Math.random();
		}while(action>3||action<0);
		actionreward.add(action);
		int backState=this.state;
		int reward=0;
		changeState(action);
		actionreward.add(getReward(backState, action));
		return actionreward;
	}
	public int getReward(int backState,int action){
		RewardTable rewardtable=new RewardTable();
		int reward=rewardtable.rewards[backState][action];
		return reward;
	}
	//�ı�״̬
	public void changeState(int action){
		if (this.state == 0) {
			switch(action){
			case 1:
				this.state=5;
				break;
			case 3:
				this.state=1;
				break;
			}
		}
		if (this.state == 1) {
			switch(action){
			case 2:
				this.state=0;
				break;
			case 3:
				this.state=2;
				break;
			}
		}
		if (this.state == 2) {
			switch(action){
			case 1:
				this.state=6;
				break;
			case 2:
				this.state=1;
				break;
			case 3:
				this.state=3;
				break;
			}
		}
		if (this.state == 3) {
			switch(action){
			case 2:
				this.state=2;
				break;
			case 3:
				this.state=4;
				break;
			}
		}
		if (this.state == 4) {
			switch(action){
			case 1:
				this.state=7;
				break;
			case 2:
				this.state=2;
				break;
			}
		}
	}
	public boolean EpisodeEnd(){
		if(this.state>=5&&this.state<=7)
			return true;
		else
			return false;
	}
}
