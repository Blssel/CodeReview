#ifndef CMSYS_COURSE_H
#define CMSYS_COURSE_H

#include <string>

using namespace std;

// 课程类：存储和处理课程信息
class Course {
    
    // 友元函数：读取输入创建新的课程
    friend void read(istream &inputStream, Course &course);

public:
    // 无参数构造函数
    Course();

    // 课程类构造函数：根据课程名称创建课程对象
    Course(const string& cName): Course() { name = cName; };
    
    // 课程类拷贝构造函数
    Course(const Course& course);
    
    // 打印课程信息
    virtual void PrintInfo() const;
    
    // 返回课程名称
    inline string GetName() const { return name; };
    
    // 设置课程名称
    inline void SetName(const string& newName) { name = newName; };

    // 返回课程ID
    inline const int GetId() const { return id; };

    // 操作符<<重载函数，当cout<<输出课程信息时使用
    friend ostream& operator <<(ostream& out, const Course& course);

    
protected:

    // 课程ID
    int id;
    
    // 课程名称
    string name;
    
    // 设置静态变量来生成唯一的ID值
    static int currentId;
};


// 课程分为基础课，项目课，评估课三种不同的类型
// 基础课为基础Course类，而项目课和评估课都继承基础课
// 项目课：比基础课增加了标签
class ProjectCourse: public Course {
public:
    // 设置标签
    inline void SetTag(const string& newTag) { tag = newTag; };

    // 返回标签
    inline string GetTag() const { return tag; };

    // 打印课程信息
    virtual void PrintInfo() const override;
private:
    string tag;
};

// 评估课：比基础课增加了时间限制
class JudgeCourse: public Course {
public:
    // 设置限时
    inline void SetTime(int newTime) { time = newTime; };

    // 返回限时
    inline int GetTime() { return time; };
    
    // 打印课程信息
    virtual void PrintInfo() const override;
private:
    int time;
};

#endif //CMSYS_COURSE_H