hadoop fs -rm /hw2/part1-input/test
hdfs dfs -copyFromLocal ./part1-input/test /hw2/part1-input
rm -f *.class *.jar
javac Hw2Part1.java
jar cfm Hw2Part1.jar Hw2Part1-manifest.txt Hw2Part1*.class
hdfs dfs -rm -f -r /hw2/output
hadoop jar ./Hw2Part1.jar /hw2/part1-input/test /hw2/output
#hadoop jar ./Hw2Part1.jar /hw2/part1-input/input_1 /hw2/output
#hadoop jar ./Hw2Part1.jar /hw2/part1-input/input_2 /hw2/output
hdfs dfs -cat '/hw2/output/part-*'
