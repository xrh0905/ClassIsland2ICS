# ClassIsland2ICS

ClassIsland2ICS is a Python project that reads JSON files containing class schedules and converts them into ICS (iCalendar) files. This allows users to import their class schedules into calendar applications like Google Calendar, Outlook, etc.

## 特性

- 读取各种编码的 JSON 文件。
- 将课程表转换为 ICS 格式。
- 记录读取和解析文件的过程。

## 要求

该项目需要以下 Python 包：

- `icalendar`
- `pytz`

可以使用以下命令安装这些包：

```sh
pip install -r requirements.txt
```

## 使用方法

1. **准备你的 JSON 文件**：确保你的课程表在一个 JSON 文件中。
2. **运行脚本**：执行 `main.py` 脚本将 JSON 文件转换为 ICS 文件。

```sh
python main.py
```

## 许可证

该项目使用 Apache-2.0 许可证。有关详细信息，请参阅 LICENSE 文件。

## 贡献

欢迎贡献！请 fork 该仓库并提交 pull request。

## 联系方式

如有任何问题或建议，请在 GitHub 上打开一个 issue。