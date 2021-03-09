# SciGraph
科技文献挖掘简单demo，更完整的demo体验网站：http://101.124.42.4:4999/zh-hans/ (服务器已到期)

## Dependency
- Adobe Acrobat DC (windows) 地址:https://pan.baidu.com/s/12MzmdneyEFljSyLG8pfVYQ 提取码: kfcu
需要用到这个工具把PDF转成XML

- python3.7

- pip install django==2.2.4

- pip install pywin32==223

- BeautifulSoup4
- lxml

- [pdf.js]( http://mozilla.github.io/pdf.js/)

## TODO
- subscribe: 
	- 存储邮件到数据库
	- 显示订阅的人数。admin可管理订阅
	- 发送邮件给订阅者，提醒订阅成功
	- 若有更新，发送邮件提醒更新
- 用户自己删除服务器media下是数据，导致upload history显示不一致，需要更改
