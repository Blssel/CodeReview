#include <stdexcept>
#include <iostream>

#include "CmdManager.h"

using namespace std;

// 初始化函数
void CmdManager::Init(){

    // 初始化课程列表
    manager.AddCourse("Linux");
    manager.AddCourse("NodeJS");
    manager.AddCourse("C++");
    manager.AddCourse("Python");
    manager.AddCourse("Spark");
    manager.AddCourse("Hadoop");
    manager.AddCourse("Ruby");
    manager.AddCourse("Java");

    // 初始化命令列表
    cmdMap.insert(pair<CourseCmd, string>(Cmd_PrintHelp, "Help Info"));
    cmdMap.insert(pair<CourseCmd, string>(Cmd_PrintCourse, "Course List"));
    cmdMap.insert(pair<CourseCmd, string>(Cmd_PrintCourseNum, "Course Number"));
    cmdMap.insert(pair<CourseCmd, string>(Cmd_PrintLongName, "Longest Course Name"));
    cmdMap.insert(pair<CourseCmd, string>(Cmd_RemoveLastCourse, "Remove Last Course"));
    cmdMap.insert(pair<CourseCmd, string>(Cmd_Exit, "Exit"));
}

// 打印帮助信息
void CmdManager::PrintAllHelp() const{
    
    cout << "Cmd List:" << endl;
    
    for (auto iter = cmdMap.begin(); iter != cmdMap.end(); iter++)
        cout << iter->first << ":" << iter->second << endl;
}

// 据命令查询帮助信息
void CmdManager::PrintCmdHelp(const CourseCmd cmd) const{
    auto iter = cmdMap.find(cmd);
    
    if (iter != cmdMap.end())
        cout << iter->first << ":" << iter->second << endl;
    else
        cout << "NOT FOUND" << endl;
}

// 处理命令操作，如果返回false则表示退出程序，其他情况返回true
bool CmdManager::HandleCmd(const CourseCmd cmd){
    auto iter = cmdMap.find(cmd);
    
    if (iter == cmdMap.end()) {
        cout << "NOT FOUND" << endl;
        return true;
    }
    
    switch(cmd) {
        case Cmd_PrintHelp: PrintAllHelp(); break;
        case Cmd_PrintCourse: manager.PrintAllCourse(); break;
        case Cmd_PrintCourseNum: cout << manager.GetCourseNum() << endl; break;
        case Cmd_PrintLongName: manager.PrintLongNameCourse(); break;
        case Cmd_RemoveLastCourse: manager.RemoveLast(); break;
        case Cmd_Exit: return false;
        default: break;
    }
    
    return true;
}



























 