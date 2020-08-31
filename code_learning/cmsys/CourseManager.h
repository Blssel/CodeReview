#ifndef CMSYS_COURSEMANGER_H
#define CMSYS_COURSEMANGER_H

#include <vector>
#include "Course.h"

using namespace std;

// 课程管理类：用来维护课程列表，执行课程处理任务
class CourseManager {
    
public:
    // 默认构造函数
    CourseManager() = default;

    // 构造函数：根据课程vector创建CourseManager
    CourseManager(const vector<Course>& courseVect); 

    // 获取课程列表长度
    inline int GetCourseNum() { return courseList.size(); }
    
    // 添加新的课程
    void AddCourse(const Course &course); 
    void AddCourse(const string& courseName); 
    
    // 删除课程：删除最后一个课程
    void RemoveLast();
    
    // 删除课程：删除指定名称的课程
    void RemoveByName(const string &name); 
    
    // 删除课程：删除指定ID的课程
    void RemoveById(int id);
    
    // 打印课程列表信息
    void PrintAllCourse(); 

    // 根据课程名称打印指定课程信息
    void PrintCourse(const string &name); 

    // 根据课程ID打印指定课程信息
    void PrintCourse(int id); 

    // 打印名称最长的课程
    void PrintLongNameCourse();

private:

    // 存储课程列表
    vector<Course> courseList;
    
    // 根据课程名称查找课程，返回课程列表中的索引值，无法找到返回-1
    int FindCourse(const string& name); 
    
    // 根据课程ID查找课程，返回课程列表中的索引值，无法找到返回-1
    int FindCourse(int id); 

};


#endif //CMSYS_COURSEMANGER_H