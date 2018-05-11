import java.io.*;
import java.util.*;
import java.net.URI;
import java.net.URISyntaxException;
import java.text.DecimalFormat;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;

import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.MasterNotRunningException;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.ZooKeeperConnectionException;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;

import org.apache.log4j.*;

public class Hw1Grp3{
    public static void main(String[] args) throws IOException, URISyntaxException, MasterNotRunningException, ZooKeeperConnectionException{
        
        /*** 解析参数 ***/
        String filename=args[0];   //保存传递的第一个参数 文件路径
        String row_key=args[1];    //保存传递的第二个参数 key的位置
        String column_key=args[2]; //保存传递的第三个参数 中间操作
        filename=filename.substring(2,filename.length());                       //第一个参数去掉头部，得到路径
        int key_column=Integer.parseInt(row_key.substring(9,row_key.length())); //第二个参数去掉头部，保存key所在列号
        String[] res_name=column_key.split(",");                                //将第三个参数分隔开，存放到res_name中，表示要进行的中间处理操作
        res_name[0]=res_name[0].substring(4,res_name[0].length());              //去掉res_name[0]的头部
        
        String file= "hdfs://localhost:9000/".concat(filename);                 //得到文件的全部路径
        
        /*** 从HDFS读取文件 ***/
        Configuration conf = new Configuration();
        FileSystem fs = FileSystem.get(URI.create(file), conf);
        Path path = new Path(file);                            //实例化一个Path
        FSDataInputStream in_stream = fs.open(path);           //打开文件
        BufferedReader in = new BufferedReader(new InputStreamReader(in_stream));
        String s;                                              //字符串用来保存读入的每一行
        List<Line> lines=new ArrayList<Line>();                //实例化list，名为lines，存放取出来所需列后的的每一行
        boolean hasCount=false; //用于判断中间处理操作是否有count
        boolean hasAvg=false;   //用于判断中间处理操作是否有avg
        boolean hasMax=false;   //用于判断中间处理操作是否有max
        
        /*** 将文件的每行读进来并取出需要的列 ***/
        while ((s=in.readLine())!=null)      //当还有行存在就继续读，否则停止
        {
            String[] columns=s.split("\\|"); //将每一行分割为多个字符串，存放到columns中
            Line line=new Line();            //实例化一个arraylist存放取出来的部分字符串
            line.key=columns[key_column];    //取出key依照key_column，存放到line.key中
            
            /*取出对应的列*/
            for(int i=0;i<res_name.length;i++)//遍历存放中间操作的数组，有什么就取出相应的列
            {
                //如果有count
                if(res_name[i].equals("count"))
                    hasCount=true;    //将hasCount标记为true
                //如果为avg
                if(res_name[i].startsWith("avg")){
                    hasAvg=true;      //将hasAvg标记为true
                    line.avgColumn.add(res_name[i]);  //line的avgColumn存放需要的操作
                    int index=Integer.parseInt(res_name[i].substring(5,res_name[i].length()-1));//将需要的列号提取出来，并由string转成int
                    line.avg.add(Float.parseFloat(columns[index]));    //将列对应的内容存放到avg对应的arraylist里，并由string转成float
                }
                //如果为max
                if(res_name[i].startsWith("max")){
                    hasMax=true;      //将hasMax标记为true
                    line.maxColumn.add(res_name[i]);  //line的maxColumn存放需要的操作
                    int index=Integer.parseInt(res_name[i].substring(5,res_name[i].length()-1));//将需要的列号提取出来，并由string转成int
                    line.max.add(Float.parseFloat(columns[index]));    //将列对应的内容存放到max对应的arraylist里，并由string转成float
                }
            }
            lines.add(line);//将一行增加到lines类中
        }
        /** 读取文件完毕 **/
        in.close();//free source
        fs.close();
        
        /*** 排序 ***/
        Collections.sort(lines);//自然顺序
        
        Logger.getRootLogger().setLevel(Level.WARN);
        
        /*** create table descriptor ***/
        String tableName= "Result";
        HTableDescriptor htd = new HTableDescriptor(TableName.valueOf(tableName));
        
        /*** create column descriptor ***/
        HColumnDescriptor cf = new HColumnDescriptor("res");
        htd.addFamily(cf);
        
        /*** configure HBase ***/
        Configuration configuration = HBaseConfiguration.create();
        HBaseAdmin hAdmin = new HBaseAdmin(configuration);
        
        /*** 判断如果Result表存在，则删除表 ***/
        if (hAdmin.tableExists(tableName))
        {
            System.out.println("Table already exists");
            hAdmin.disableTable(tableName);
            hAdmin.deleteTable(tableName);
            System.out.println("Table deleted");
            
        }
        
        /*** 创建表 ***/
        hAdmin.createTable(htd);
        System.out.println("table "+tableName+ " created successfully");
        hAdmin.close();
        
        /*** 分组计数并求count、avg、max ***/
        String last_key=lines.get(0).key;            //维持一个字符串，表明上一次的key是什么
        ArrayList<Float> sum=new ArrayList<Float>(); //实例化一个sum，存放和
        for(int i=0;i<lines.get(0).avg.size();i++)   //初始化sum
            sum.add((float)0);
        ArrayList<Float> max=new ArrayList<Float>(); //实例化一个max，存放最大值
        for(int i=0;i<lines.get(0).max.size();i++)   //初始化max
            max.add(Float.NEGATIVE_INFINITY);
        int Count=0;  //用于计数，并初始化
        
        int num_grouped=0;
        /*** 将每一行进行中间处理，有哪个操作就相应对哪一列进行处理 ***/
        for(Line line:lines)
        {
            /*** 如果key改变，说明之前的为一组，求该组count avg max，并初始化max sum count，最后一组在后面实现 ***/
            if(!line.key.equals(last_key))
            {
                /*** 写入hbase的结果表中，并初始化max avg ***/
                HTable table = new HTable(configuration,tableName);//打开表
                Put put = new Put(last_key.getBytes());//写入key
                if(hasCount)
                    put.add("res".getBytes(),"count".getBytes(),String.valueOf(Count).getBytes());//写入Count
                
                if(hasAvg)
                {
                    //求平均值
                    ArrayList<Float> average=calAvg(sum,Count);
                    // 写入avg  "res:avg(R3)",23.34,"res:avg(R6)",435.34,"res:avg(R10)",73.33
                    for(int i=0;i<average.size();i++)
                    {
                        String tmp=new DecimalFormat("##0.00").format(average.get(i));//保留两位小数
                        put.add("res".getBytes(),line.avgColumn.get(i).getBytes(),tmp.getBytes());
                        
                    }
                    initSum(sum,lines.get(0).avg.size());//初始化sum
                }
                if(hasMax)
                {
                    //写入max "res:max(R3)",23.34,"res:max(R6)",435.34,"res:max(R10)",73.33
                    for(int i=0;i<max.size();i++)
                    {
                        String tmp=new DecimalFormat("##0.00").format(max.get(i)); //保留两位小数
                        put.add("res".getBytes(),line.maxColumn.get(i).getBytes(),tmp.getBytes());
                    }
                    initMax(max,lines.get(0).max.size());//初始化max
                }
                table.put(put);//输入到表
                table.close();//关闭表
                Count=0;//Count初始化为0
            }
            last_key=line.key;//更新键值
            Count++;//计数
            if(hasAvg)//有avg则计算sum
                sumAdd(sum,line.avg);
            if(hasMax)//有max则更新max
                updateMax(max,line.max);
        }
        
        /*** 将最后一个key的记录存入hbase ***/
        HTable table = new HTable(configuration,tableName);
        Put put = new Put(last_key.getBytes());//实例化put，存入最后一个key
        if(hasCount)
            put.add("res".getBytes(),"count".getBytes(),String.valueOf(Count).getBytes());//写入Count
        if(hasAvg)
        {
            //求平均值
            ArrayList<Float> average=calAvg(sum,Count);
            // 写入avg  "res:avg(R3)",23.34,"res:avg(R6)",435.34,"res:avg(R10)",73.33
            for(int i=0;i<average.size();i++)
            {
                String tmp=new DecimalFormat("##0.00").format(average.get(i));//保留两位小数
                put.add("res".getBytes(),lines.get(lines.size()-1).avgColumn.get(i).getBytes(),tmp.getBytes());
            }
           	initSum(sum,lines.get(0).avg.size());
       	}
        if(hasMax)
        {
            //写入max "res:max(R3)",23.34,"res:max(R6)",435.34,"res:max(R10)",73.33
            for(int i=0;i<max.size();i++)
            {
                String tmp=new DecimalFormat("##0.00").format(max.get(i)); //保留两位小数
                put.add("res".getBytes(),lines.get(lines.size()-1).maxColumn.get(i).getBytes(),tmp.getBytes());
            }
            initMax(max,lines.get(0).max.size());
        }
        table.put(put);
        table.close();
        
    }
    /*** 初始化sum为0 ***/
    public static void initSum(ArrayList<Float> arraylist,int len){
        for(int i=0;i<len;i++){
            arraylist.set(i,(float)0);
        }
    }
    /*** 初始化max为最小值 ***/
    public static void initMax(ArrayList<Float> arraylist,int len){
        for(int i=0;i<len;i++)
            arraylist.set(i,Float.NEGATIVE_INFINITY);
    }
    /*** 求和 ***/
    public static void sumAdd(ArrayList<Float> sum,ArrayList<Float> avg){
        for(int i=0;i<sum.size();i++)
            sum.set(i,sum.get(i)+avg.get(i));
    }
    /*** 更新max值 ***/
    public static void updateMax(ArrayList<Float> max,ArrayList<Float> m){
        for(int i=0;i<max.size();i++) //对于max中的每一个列都求max
        {
            if(m.get(i)>max.get(i))   //如果m中的值比max本来存的值大，就修改
                max.set(i,m.get(i));
        }
    }
    /*** 计算平均值 ***/
    public static ArrayList<Float> calAvg(ArrayList<Float> sum,int count){
        ArrayList<Float> average=new ArrayList<Float>();//存放平均值的arraylist
        for(int i=0;i<sum.size();i++) //对于sum中的所有列求平均值
            average.add(sum.get(i)/count);
        return average;
    }
}

/*** 定义一个存入hbase表中的类 ***/
class Line implements Comparable<Line>{
    public String key;  //存放主键key
    public int count;   //count为每组的数量
    public ArrayList<String> avgColumn; //存放对应不同列要计算avg的参数
    public ArrayList<Float> avg;        //存放需要计算avg的列的数值
    public ArrayList<String> maxColumn; //存放对应不同列要计算max的参数
    public ArrayList<Float> max;        //存放需要计算max的列的数值
    
    /*** 将class初始化 ***/
    Line(){
        count=-1;
        this.avgColumn=new ArrayList<String>();
        this.avg=new ArrayList<Float>();
        this.maxColumn=new ArrayList<String>();
        this.max=new ArrayList<Float>();
    }
    
    /*** 自定义比较方法，如果认为此实体本身大则返回1，否则返回-1,相等返回0 ***/
    @Override
    public int compareTo(Line line) {
        if(this.key.compareTo(line.key)>0)
            return 1;
        else if(this.key.compareTo(line.key)==0)
            return 0;
        else
            return -1;
    }
}
