#ifndef  CMSYS_CMD_H
#define CMSYS_CMD_H

// 支持的命令
enum CourseCmd
{
    // 打印命令帮助信息
	Cmd_PrintHelp = 0,
    // 打印课程信息
	Cmd_PrintCourse = 1,
    // 打印课程数量
	Cmd_PrintCourseNum = 2,
    // 打印最长的课程名称
	Cmd_PrintLongName = 3,
    // 删除最后一个课程
	Cmd_RemoveLastCourse = 4,
    // 退出程序
	Cmd_Exit = 5,
};

#endif // CMSYS_CMD_H