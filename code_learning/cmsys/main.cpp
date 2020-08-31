#include <iostream>

#include "CmdManager.h"

using namespace std;

// 主函数
int main() {

    // 输入的命令
    int cmd;
    

    // 创建命令管理对象
    CmdManager cmdManager;
    cmdManager.Init();

    // 打印帮助信息
    cmdManager.PrintAllHelp();

    cout << "New Command:";

    // 进入主循环并处理输入信息
    while (cin >> cmd) {
        if (cin.good()) {
            bool exitCode = cmdManager.HandleCmd((CourseCmd)cmd);
            if (!exitCode)
                return 0;
        }

        cout << "-------------------------" << endl;
        cout << "New Command:";

        // 清理输入流，避免刚才流中的字符影响后续输入
        cin.clear();
        cin.ignore();
    }

    return 0;
}