import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import jieba
from wordcloud import WordCloud
import numpy as np
from pathlib import Path

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = 'white'

# 尝试使用系统字体文件
font_path = r'C:\Windows\Fonts\simhei.ttf'
if Path(font_path).exists():
    from matplotlib.font_manager import FontProperties
    zhfont = FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = [zhfont.get_name()]
else:
    # 备选方案
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']

sns.set_style("whitegrid")

# 蓝绿色系低饱和度配色
COLOR_PALETTE = {
    'color1': '#5B9BA6',  # 蓝绿主色
    'color2': '#8FB3AB',  # 浅蓝绿
    'color3': '#A3C4BC',  # 更浅蓝绿
    'color4': '#B5D4CB',  # 淡蓝绿
}

# 读取数据
file1 = '固体杨枝甘露-全平台Top20作品导出 1118~1218.xlsx'
file2 = '奶皮子糖葫芦-全平台Top20作品导出 1118~1218.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# 添加产品名称标签
df1['产品'] = '固体杨枝甘露'
df2['产品'] = '奶皮子糖葫芦'

# 合并数据
df_all = pd.concat([df1, df2], ignore_index=True)

print("=" * 50)
print("数据加载完成")
print(f"固体杨枝甘露: {len(df1)} 条作品")
print(f"奶皮子糖葫芦: {len(df2)} 条作品")
print("=" * 50)

# ============ 1. 标题分词和词云 ============
def create_wordcloud(texts, title, filename):
    """生成词云"""
    # 合并所有文本
    text = ' '.join(texts.dropna().astype(str))
    
    # 分词
    words = jieba.cut(text)
    words_list = [w for w in words if len(w) > 1]  # 过滤单字
    
    # 生成词云
    wc = WordCloud(
        font_path='C:\\Windows\\Fonts\\SimHei.ttf',
        width=1200, 
        height=600,
        background_color='white',
        colormap='viridis'
    ).generate(' '.join(words_list))
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ 词云已保存: {filename}")
    plt.close()

# 创建各产品的词云
create_wordcloud(df1['标题'], '固体杨枝甘露 - 标题词云', '杨枝甘露_词云.png')
create_wordcloud(df2['标题'], '奶皮子糖葫芦 - 标题词云', '奶皮子_词云.png')

print()

# ============ 2. 高频词统计 ============
def get_top_keywords(texts, top_n=15):
    """获取高频词"""
    text = ' '.join(texts.dropna().astype(str))
    words = jieba.cut(text)
    words_list = [w for w in words if len(w) > 1]
    counter = Counter(words_list)
    return counter.most_common(top_n)

top_words_1 = get_top_keywords(df1['标题'])
top_words_2 = get_top_keywords(df2['标题'])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 固体杨枝甘露
words_1, counts_1 = zip(*top_words_1)
axes[0].barh(words_1[::-1], counts_1[::-1], color=COLOR_PALETTE['color1'])
axes[0].set_xlabel('出现频次', fontsize=12)
axes[0].set_title('固体杨枝甘露 - 高频词TOP15', fontsize=14, fontweight='bold')
axes[0].grid(axis='x', alpha=0.3)

# 奶皮子糖葫芦
words_2, counts_2 = zip(*top_words_2)
axes[1].barh(words_2[::-1], counts_2[::-1], color=COLOR_PALETTE['color2'])
axes[1].set_xlabel('出现频次', fontsize=12)
axes[1].set_title('奶皮子糖葫芦 - 高频词TOP15', fontsize=14, fontweight='bold')
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('高频词对比.png', dpi=300, bbox_inches='tight')
print("✓ 高频词对比已保存: 高频词对比.png")
plt.close()

# ============ 3. 互动数据对比 ============
# 清理数据 - 转换为数值类型
for col in ['获赞数', '评论数', '分享数', '收藏数']:
    df1[col] = pd.to_numeric(df1[col], errors='coerce')
    df2[col] = pd.to_numeric(df2[col], errors='coerce')

metrics = ['获赞数', '评论数', '分享数', '收藏数']
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, metric in enumerate(metrics):
    data_to_plot = [
        df1[metric].dropna(),
        df2[metric].dropna()
    ]
    
    bp = axes[idx].boxplot(data_to_plot, labels=['固体杨枝甘露', '奶皮子糖葫芦'],
                           patch_artist=True)
    
    # 设置颜色
    colors = [COLOR_PALETTE['color1'], COLOR_PALETTE['color2']]
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    axes[idx].set_ylabel(metric, fontsize=11)
    axes[idx].set_title(f'{metric} 分布对比', fontsize=12, fontweight='bold')
    axes[idx].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('互动数据对比.png', dpi=300, bbox_inches='tight')
print("✓ 互动数据对比已保存: 互动数据对比.png")
plt.close()

# ============ 5. 平均互动数据对比 ============
metrics_stats = []

for metric in metrics:
    metrics_stats.append({
        '指标': metric,
        '固体杨枝甘露': df1[metric].mean(),
        '奶皮子糖葫芦': df2[metric].mean()
    })

df_stats = pd.DataFrame(metrics_stats)
df_stats_plot = df_stats.set_index('指标')

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(df_stats_plot.index))
width = 0.35

bars1 = ax.bar(x - width/2, df_stats_plot['固体杨枝甘露'], width, 
              label='固体杨枝甘露', color=COLOR_PALETTE['color1'])
bars2 = ax.bar(x + width/2, df_stats_plot['奶皮子糖葫芦'], width,
              label='奶皮子糖葫芦', color=COLOR_PALETTE['color2'])

ax.set_ylabel('平均数值', fontsize=12)
ax.set_title('互动指标平均值对比', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df_stats_plot.index)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

# 添加数值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.0f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('平均互动对比.png', dpi=300, bbox_inches='tight')
print("✓ 平均互动对比已保存: 平均互动对比.png")
plt.close()

# ============ 6. 发布时间分析 ============
df_all['发布时间'] = pd.to_datetime(df_all['发布时间'], errors='coerce')
df_all['日期'] = df_all['发布时间'].dt.date
df_all['时段'] = df_all['发布时间'].dt.hour

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 按产品统计发布日期分布
for product, ax, color in [('固体杨枝甘露', axes[0], COLOR_PALETTE['color1']), 
                            ('奶皮子糖葫芦', axes[1], COLOR_PALETTE['color2'])]:
    date_dist = df_all[df_all['产品'] == product]['日期'].value_counts().sort_index()
    ax.plot(range(len(date_dist)), date_dist.values, marker='o', linewidth=2, 
           markersize=6, color=color)
    ax.fill_between(range(len(date_dist)), date_dist.values, alpha=0.3, color=color)
    ax.set_xlabel('发布日期', fontsize=11)
    ax.set_ylabel('作品数量', fontsize=11)
    ax.set_title(f'{product} - 发布日期分布', fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3)
    # 显示x轴标签
    if len(date_dist) <= 10:
        ax.set_xticks(range(len(date_dist)))
        ax.set_xticklabels([str(d)[-5:] for d in date_dist.index], rotation=45)

plt.tight_layout()
plt.savefig('发布时间分布.png', dpi=300, bbox_inches='tight')
print("✓ 发布时间分布已保存: 发布时间分布.png")
plt.close()

# ============ 8. 生成统计摘要 ============
print("\n" + "=" * 50)
print("数据统计摘要")
print("=" * 50)

print("\n📊 固体杨枝甘露")
print(f"  总作品数: {len(df1)}")
print(f"  平均获赞: {df1['获赞数'].mean():.0f}")
print(f"  平均评论: {df1['评论数'].mean():.0f}")
print(f"  平均分享: {df1['分享数'].mean():.0f}")
print(f"  平均收藏: {df1['收藏数'].mean():.0f}")
print(f"  活跃账号数: {df1['账号'].nunique()}")

print("\n📊 奶皮子糖葫芦")
print(f"  总作品数: {len(df2)}")
print(f"  平均获赞: {df2['获赞数'].mean():.0f}")
print(f"  平均评论: {df2['评论数'].mean():.0f}")
print(f"  平均分享: {df2['分享数'].mean():.0f}")
print(f"  平均收藏: {df2['收藏数'].mean():.0f}")
print(f"  活跃账号数: {df2['账号'].nunique()}")

print("\n✅ 所有分析图表已生成!")
print("=" * 50)
