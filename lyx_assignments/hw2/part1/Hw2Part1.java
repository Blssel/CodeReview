import java.io.IOException;
import java.util.StringTokenizer;
import java.util.Scanner;
import java.lang.Double;
import java.text.DecimalFormat;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapred.TextInputFormat;
import org.apache.hadoop.mapred.TextOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;




public class Hw2Part1 {
      public static class LineMapper extends Mapper<Object, Text, Text, DoubleWritable> {

        private Text address = new Text();
  
        protected void map(Object key, Text value, Context context) throws IOException, InterruptedException {
            /* if (value == null || value.getLength() == 0) {
                return;
            } */
            String line = value.toString();
           // System.out.println("################");
           // System.out.println(line+'@');
           // System.out.println(line.matches("^[^ ]+\\s[^ ]+\\s\\d+(\\.\\d+)$"));
           // System.out.println("#################");
	   if(line.charAt(0)==' ')
             return;
           line=line.trim();// if char at index 0 is not a space, we remove the last space,if exist. 
	   String regex="^[^ ]+\\s[^ ]+\\s\\d+(\\.\\d+)$";
	   if(!line.matches(regex)){
              System.out.println(line+"not match!!!!!!!!!!!!");
	      return;
	    }
            String[] items=line.split(" ");
            //if(items.length!=3){
	    //  System.out.println("*******************************************************");
            //  return;
            //}
            String add_pair=items[0]+" "+items[1];
            address.set(add_pair);
            DoubleWritable time = new DoubleWritable(Double.parseDouble(items[2]));

            context.write(address, time);
        }
      }

        public static class LineReducer extends Reducer<Text,DoubleWritable,Text,Text> {
          private DoubleWritable sum = new DoubleWritable();

          private Text result_value= new Text();//存放result_value
          public void reduce(Text key, Iterable<DoubleWritable> values,
                             Context context) throws IOException, InterruptedException {
            int count=0;
            double sum=0.0;
            for (DoubleWritable val : values) {
              count++;
              sum+=val.get();
            }
            double avg=sum/count;
          //写入result_value
          result_value.set(Integer.toString(count)+" "+new DecimalFormat("##0.000").format(avg));
          context.write(key, result_value);
        }
  }


    

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
	conf.set("mapred.textoutputformat.separator", " ");
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.exit(2);
        }

        Job job = Job.getInstance(conf, "line job");

        job.setJarByClass(Hw2Part1.class);

        job.setMapperClass(LineMapper.class);
        job.setReducerClass(LineReducer.class);

        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(DoubleWritable.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        for (int i = 0; i < otherArgs.length - 1; ++i) {
            FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }
        FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}
