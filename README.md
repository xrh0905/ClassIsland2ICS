# ClassIsland2ICS

ClassIsland2ICS 是一个 Python 项目，用于读取包含课程表的 JSON 文件并将其转换为 ICS (iCalendar) 文件。这样用户可以将课程表导入到 Google Calendar、Outlook 等日历应用中并同步到手表上。

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
pip install -r [requirements.txt](http://_vscodecontentref_/0)
```

## 使用方法

1. **准备你的 JSON 文件**：确保你的课程表在一个 JSON 文件中。
2. **运行脚本**：执行 `main.py` 脚本将 JSON 文件转换为 ICS 文件。

如目录下存在settings.json和启用的profile.json
```sh
python main.py
```

如目录下存在profile.json
```sh
python main.py profile.json
```

## 可选参数
`--calendar-start-date`：日历开始日期 (YYYY-MM-DD)。
`--calendar-end-date`：日历结束日期 (YYYY-MM-DD)。
`--ignore-start-time`：忽略时间段开始 (HH:MM)。
`--ignore-end-time`：忽略时间段结束 (HH:MM)。
`--ignore-class-names`：要忽略的课程名称，逗号分隔。
`--settings`：设置 JSON 文件的路径。
`--start-time`：单周开始时间的 ISO 格式。
`--profile`：课程表 JSON 文件的路径。

## 许可证

该项目使用 Apache-2.0 许可证。有关详细信息，请参阅 LICENSE 文件。

## 贡献

欢迎贡献！请 fork 该仓库并提交 pull request。

## 联系方式

如有任何问题或建议，请在 GitHub 上打开一个 issue。