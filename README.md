# 社交媒体数据分析项目

这是一个用于分析社交媒体平台数据的Python项目，支持从新榜获取关键词趋势和内容数据，并进行可视化分析。

## 功能特性

### 数据采集
- **新榜爬虫** (`xinbang_spider.py`): 使用Selenium自动化浏览器获取关键词趋势和内容数据
- **小红书爬虫** (`xiaohongshu_spider.py`): 使用Selenium模拟真实浏览器，根据关键词搜索并爬取小红书笔记数据

### 数据分析与可视化
- **基础分析** (`analysis.py`): 生成词云、高频词统计、互动数据对比等
- **高级图表** (`advanced_charts.py`): 创建雷达图、分组柱状图、堆积柱状图等专业图表
- **表格生成** (`table_generator.py`): 将统计数据转换为美观的表格图片

## 文件结构

```
├── advanced_charts.py      # 高级图表生成
├── analysis.py             # 数据分析脚本
├── table_generator.py      # 表格图片生成
├── xiaohongshu_spider.py   # 小红书爬虫 (Selenium版)
├── xinbang_spider.py       # 新榜爬虫
├── keywords.txt            # 关键词列表
└── README.md              # 项目说明
```

## 环境要求

- Python 3.7+
- Chrome浏览器
- ChromeDriver (版本需与Chrome匹配)

## 安装依赖

```bash
pip install pandas matplotlib seaborn jieba wordcloud selenium openpyxl
```

## 使用方法

### 1. 数据采集

#### 小红书数据采集
1. 下载ChromeDriver并放到项目目录，或修改代码中的路径
2. 运行爬虫：
```python
python xiaohongshu_spider.py
```
3. 程序会自动打开浏览器，请手动登录小红书账号
4. 登录完成后回到终端按Enter继续
5. 程序会自动搜索关键词并爬取笔记数据

**爬取字段：**
- 笔记ID
- 标题
- 用户
- 发布日期
- 点赞数
- 评论数
- 词条/标签
- 链接

#### 新榜数据采集
1. 下载并配置ChromeDriver路径
2. 修改 `xinbang_spider.py` 中的 `CHROMEDRIVER_PATH`
3. 运行爬虫：
```python
python xinbang_spider.py
```
4. 手动登录新榜账号后按Enter继续

### 2. 数据分析

确保数据文件存在后，依次运行分析脚本：

```python
python analysis.py          # 基础分析
python advanced_charts.py   # 高级图表
python table_generator.py   # 表格生成
```

## 输出文件

### 数据文件
- `keyword_trend.csv`: 关键词趋势数据
- `content_meta.csv`: 内容元数据
- `xiaohongshu_data.xlsx`: 小红书笔记数据（每个关键词一个Sheet）

### 可视化文件
- `杨枝甘露_词云.png`, `奶皮子_词云.png`: 词云图
- `高频词对比.png`: 高频词对比图
- `互动数据对比.png`: 互动数据箱线图
- `平均互动对比.png`: 平均互动柱状图
- `发布时间分布.png`: 发布时间分布图
- `互动数据雷达图.png`: 雷达图
- `互动数据分组柱状图.png`: 分组柱状图
- `互动数据占比堆积图.png`: 堆积柱状图
- `核心数据对比表.png`: 核心数据对比表
- `杨枝甘露_TOP作品.png`, `奶皮子_TOP作品.png`: TOP作品榜单
- `杨枝甘露_活跃账号.png`, `奶皮子_活跃账号.png`: 活跃账号榜单
- `互动指标详细统计.png`: 详细统计表

## 注意事项

1. **ChromeDriver版本**: 版本需与本地Chrome浏览器匹配
2. **登录要求**: 小红书和新榜爬虫都需要手动登录账号
3. **数据文件**: 分析脚本依赖特定的Excel文件，请确保数据格式正确
4. **字体支持**: 图表生成需要中文字体支持，Windows系统默认包含
5. **爬取限制**: 请合理控制爬取频率，避免账号被限制
6. **数据隐私**: 请遵守相关平台的使用条款，仅用于学习和研究目的


## 许可证


本项目仅供学习和研究使用，请遵守相关平台的使用条款。

