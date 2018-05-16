#include <stdio.h>
#include <string.h>
#include <math.h>

#include "GraphLite.h"

#define VERTEX_CLASS_NAME(name) PageRankVertex##name

#define EPS 1e-6

class VERTEX_CLASS_NAME(InputFormatter): public InputFormatter {
public:
    int64_t getVertexNum() {
        unsigned long long n;
        sscanf(m_ptotal_vertex_line, "%lld", &n);
        m_total_vertex= n;
        return m_total_vertex;
    }
    int64_t getEdgeNum() {
        unsigned long long n;
        sscanf(m_ptotal_edge_line, "%lld", &n);
        m_total_edge= n;
        return m_total_edge;
    }
    int getVertexValueSize() {
        m_n_value_size = sizeof(double);
        return m_n_value_size;
    }
    int getEdgeValueSize() {
        m_e_value_size = sizeof(double);
        return m_e_value_size;
    }
    int getMessageValueSize() {
        m_m_value_size = sizeof(double);
        return m_m_value_size;
    }
    void loadGraph() {
        unsigned long long last_vertex;
        unsigned long long from;
        unsigned long long to;
        double weight = 0;
        
        double value = 1;
        int outdegree = 0;
        
        const char *line= getEdgeLine();

        // Note: modify this if an edge weight is to be read
        //       modify the 'weight' variable

        sscanf(line, "%lld %lld", &from, &to);
        addEdge(from, to, &weight);

        last_vertex = from;
        ++outdegree;
        for (int64_t i = 1; i < m_total_edge; ++i) {
            line= getEdgeLine();

            // Note: modify this if an edge weight is to be read
            //       modify the 'weight' variable

            sscanf(line, "%lld %lld", &from, &to);
            if (last_vertex != from) {
                addVertex(last_vertex, &value, outdegree);
                last_vertex = from;
                outdegree = 1;
            } else {
                ++outdegree;
            }
            addEdge(from, to, &weight);
        }
        addVertex(last_vertex, &value, outdegree);
    }
};

class VERTEX_CLASS_NAME(OutputFormatter): public OutputFormatter {
public:
    void writeResult() {
        int64_t vid;
        double value;
        char s[1024];

        for (ResultIterator r_iter; ! r_iter.done(); r_iter.next() ) {
            r_iter.getIdValue(vid, &value);
            int n = sprintf(s, "%lld: %f\n", (unsigned long long)vid, value);
            writeNextResLine(s, n);
        }
    }
};

// An aggregator that records a double value tom compute sum
class VERTEX_CLASS_NAME(Aggregator): public Aggregator<double> {
public:
    void init() {
        m_global = 0;
        m_local = 0;
    }
    void* getGlobal() {
        return &m_global;
    }
    void setGlobal(const void* p) {
        m_global = * (double *)p;
    }
    void* getLocal() {
        return &m_local;
    }
    void merge(const void* p) {
        m_global += * (double *)p;
    }
    void accumulate(const void* p) {
        m_local += * (double *)p;
    }
};

// 继承Vertex类，三个数据类型分别对应：顶点，边，消息的数据类型
class VERTEX_CLASS_NAME(): public Vertex <double, double, double> {
public:
    void compute(MessageIterator* pmsgs) {
        int in_trgl, out_trgl,thr_trgl,cyc_trgl
        int64_t vertex_id;
        vector<int64_t> in_neighbors;
        vector<int64_t> out_neighbors;
        //0th superstep，send vertex id to neighbors
        if(getSuperstep()==0){
          vertex_id=getVertexId();
          sendMessageToAllNeighbors(vertex_id)
        }
        //1th superstep, get all in-neighbor ids
        else if(getSupierstep()==1){
          // send in_neighbors to neighbors
          for(;!pmsgs->done();pmsgs->next()){
            int64_t in_neigh=pmsgs.getValue();
            in_neighbors.push_back(in_neigh);
            int64_t in_msg=in_neigh*10;
            sendMessageToAllNeighbors(in_msg);
          }
          
          // send out_neighbors to neighbors
          OutEdgeIterator out_ite = getOutEdgeIterator();
          for( ; ! out_ite.done(); out_ite.next() ){
            int64_t out_neigh =out_ite.target();
            out_neighbors.push_back(out_neigh);
            int64_t out_msg=out_neigh*10+1;
            sendMessageToAllNeighbors(out_msg);
          }

        }

        /* 2th superstep, collect in-neighbors' neighbors*/
        vector<int64_t> in_neigh_neigh;
        else if(getSuperstep()==2){
          for( ; ! pmsgs->done(); pmsgs->next()){
            in_neigh_neigh.push_back(pmsgs.getValue());
          }
        }
        // judge type of Trianglies
        vector<int>::iterator out_ite = out_neighbors.begin();
        for (; out_ite != out_neighbors.end(); out_ite++){
          int64_t out_neigh = *out_ite;
          for(vector<int64_t>::iterator ite = in_neigh_neigh.begin();ite != in_neigh_neigh.end(); ++ite){
            if(*ite%10==1){
              int64_t prim=*ite/10;
              if(prim==out_neigh){
                int addition = 1;
                accumulateAggr(1, &addition);
                int addition = 2;
                accumulateAggr(2, &addition);
              }
            }else{
              int64_t prim=*ite/10;
              if(prim==out_neigh){
                int addition = 3;
                accumulateAggr(3, &addition);
              }
            }
          }
        }
        
        for(vector<int64_t>::iterator ite = in_neigh_neigh.begin(); ite != in_neigh_neigh.end(); ++ite){
          if(find(in_neighbors.begin(), in_neighbors.end(), *ite/10) != in_neighbors.end()){
            int addition = 0;
            accumulateAggr(0, &addition);       
          } 
        }
        else if (getSuperstep() >= 3){
            A = * (int *)getAggrGlobal(0);
            B = * (int *)getAggrGlobal(1);
            C = * (int *)getAggrGlobal(2);
            D = * (int *)getAggrGlobal(3);
            voteToHalt(); 
            return;
        }


        * mutableValue() = val;
        const int64_t n = getOutEdgeIterator().size();
        sendMessageToAllNeighbors(val / n);
    }
};

class VERTEX_CLASS_NAME(Graph): public Graph {
public:
    VERTEX_CLASS_NAME(Aggregator)* aggregator;

public:
    // argv[0]: PageRankVertex.so
    // argv[1]: <input path>
    // argv[2]: <output path>
    void init(int argc, char* argv[]) {

        setNumHosts(5);
        setHost(0, "localhost", 1411);
        setHost(1, "localhost", 1421);
        setHost(2, "localhost", 1431);
        setHost(3, "localhost", 1441);
        setHost(4, "localhost", 1451);

        if (argc < 3) {
           printf ("Usage: %s <input path> <output path>\n", argv[0]);
           exit(1);
        }

        m_pin_path = argv[1];
        m_pout_path = argv[2];

        aggregator = new VERTEX_CLASS_NAME(Aggregator)[1];
        regNumAggr(1);
        regAggr(0, &aggregator[0]);
    }

    void term() {
        delete[] aggregator;
    }
};

/* STOP: do not change the code below. */
extern "C" Graph* create_graph() {
    Graph* pgraph = new VERTEX_CLASS_NAME(Graph);

    pgraph->m_pin_formatter = new VERTEX_CLASS_NAME(InputFormatter);
    pgraph->m_pout_formatter = new VERTEX_CLASS_NAME(OutputFormatter);
    pgraph->m_pver_base = new VERTEX_CLASS_NAME();

    return pgraph;
}

extern "C" void destroy_graph(Graph* pobject) {
    delete ( VERTEX_CLASS_NAME()* )(pobject->m_pver_base);
    delete ( VERTEX_CLASS_NAME(OutputFormatter)* )(pobject->m_pout_formatter);
    delete ( VERTEX_CLASS_NAME(InputFormatter)* )(pobject->m_pin_formatter);
    delete ( VERTEX_CLASS_NAME(Graph)* )pobject;
}
