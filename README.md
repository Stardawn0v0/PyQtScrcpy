# 使用Python PyQt制作的Scrcpy GUI版本

## 基础使用
没什么好说的，把原版Scrcpy的命令行参数包装了一下而已

## TODO
- 在未开启某些设备的ADB输入限制时弹出提示（比如米米的USB调试-安全设置）
- 按键映射功能（我用不上所以优先级较低 欢迎PR）

## 跨平台支持
|    平台     |   工作情况    |
|:---------:|:---------:|
| Windows11 |   运行正常    |
| Windows10 | 缺少窗口模糊特效  |
|   Linux   | 尝试适配 尚未测试 |
|   MacOS   | 尝试适配 尚未测试 |

## BUG反馈
不建议非开发者尤其是玩机小白提交issue，除非你能保证你的issue详细、符合规范且有意义。

## License
采用 GPL-3.0 License，同时**禁止商用**。

## 关于
这是我接触Python后的首个开源项目，此前技术栈均为Go等Web开发，所以你可能在此项目中看到：
- 逆天的函数命名
- 耦合度高到爆炸的代码
- 混乱不堪的逻辑
- 史

但仍欢迎您与我一起优化改进PyQtScrcpy，欢迎提出issue或Pull Request！

## 注意
项目中使用的部分Icon来自[IconPark](https://iconpark.oceanengine.com/official)，它们并不是PyQtScrcpy的一部分！
