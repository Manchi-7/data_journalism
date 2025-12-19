import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file1 = '固体杨枝甘露-全平台Top20作品导出 1118~1218.xlsx'
file2 = '奶皮子糖葫芦-全平台Top20作品导出 1118~1218.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# 数据清理
for col in ['获赞数', '评论数', '分享数', '收藏数']:
    df1[col] = pd.to_numeric(df1[col], errors='coerce')
    df2[col] = pd.to_numeric(df2[col], errors='coerce')

# 颜色定义
colors_palette = {
    'header': '#5B9BA6',
    'row_odd': '#E8F3F5',
    'row_even': '#FFFFFF',
    'text': '#333333'
}

def create_table_image(data, title, filename):
    """创建漂亮的表格图片"""
    # 根据列数调整图表宽度
    col_count = len(data.columns)
    fig_width = max(10, col_count * 1.5)
    fig_height = max(6, len(data) * 0.5 + 2)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('tight')
    ax.axis('off')
    
    # 计算列宽
    col_widths = [1.0 / col_count] * col_count
    
    # 创建表格
    table = ax.table(cellText=data.values,
                     colLabels=data.columns,
                     cellLoc='center',
                     loc='center',
                     colWidths=col_widths)
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)
    
    # 设置表头样式
    for i in range(len(data.columns)):
        cell = table[(0, i)]
        cell.set_facecolor(colors_palette['header'])
        cell.set_text_props(weight='bold', color='white', fontsize=10)
        cell.set_height(0.08)
    
    # 设置数据行样式
    for i in range(1, len(data) + 1):
        for j in range(len(data.columns)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor(colors_palette['row_odd'])
            else:
                cell.set_facecolor(colors_palette['row_even'])
            cell.set_text_props(color=colors_palette['text'], fontsize=9)
            cell.set_edgecolor('#CCCCCC')
            # 设置自动换行
            cell.set_height(0.06)
    
    # 添加标题
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ 表格已保存: {filename}")
    plt.close()

# ============ 1. 基本统计对比表 ============
summary_data = {
    '指标': ['总作品数', '平均获赞', '平均评论', '平均分享', '平均收藏', '活跃账号数'],
    '固体杨枝甘露': [
        len(df1),
        f"{df1['获赞数'].mean():.0f}",
        f"{df1['评论数'].mean():.0f}",
        f"{df1['分享数'].mean():.0f}",
        f"{df1['收藏数'].mean():.0f}",
        df1['账号'].nunique()
    ],
    '奶皮子糖葫芦': [
        len(df2),
        f"{df2['获赞数'].mean():.0f}",
        f"{df2['评论数'].mean():.0f}",
        f"{df2['分享数'].mean():.0f}",
        f"{df2['收藏数'].mean():.0f}",
        df2['账号'].nunique()
    ]
}

df_summary = pd.DataFrame(summary_data)
create_table_image(df_summary, '两款产品核心数据对比', '核心数据对比表.png')

# ============ 2. 最高互动作品表 ============
def get_top_works(df, product_name, top_n=8):
    """获取互动最高的作品"""
    df_copy = df.copy()
    df_copy['互动数'] = df_copy['获赞数'] + df_copy['评论数'] + df_copy['分享数'] + df_copy['收藏数']
    top = df_copy.nlargest(top_n, '互动数')[['标题', '账号', '获赞数', '评论数', '互动数']]
    top = top.reset_index(drop=True)
    top.index = top.index + 1
    
    # 截取标题，超出部分舍弃
    top['标题'] = top['标题'].apply(lambda x: x[:17] + '..' if len(x) > 17 else x)
    
    return top[['标题', '账号', '获赞数', '评论数', '互动数']]

top_works_1 = get_top_works(df1, '固体杨枝甘露')
top_works_2 = get_top_works(df2, '奶皮子糖葫芦')

# 重命名列以显示
top_works_1.columns = ['标题', '账号', '获赞数', '评论数', '总互动数']
top_works_2.columns = ['标题', '账号', '获赞数', '评论数', '总互动数']

create_table_image(top_works_1, '固体杨枝甘露 - TOP作品榜单', '杨枝甘露_TOP作品.png')
create_table_image(top_works_2, '奶皮子糖葫芦 - TOP作品榜单', '奶皮子_TOP作品.png')

# ============ 3. 最活跃账号表 ============
def get_top_accounts(df, product_name, top_n=10):
    """获取最活跃的账号"""
    accounts = df['账号'].value_counts().head(top_n).reset_index()
    accounts.columns = ['账号', '作品数']
    accounts.index = accounts.index + 1
    
    return accounts

top_acc_1 = get_top_accounts(df1, '固体杨枝甘露')
top_acc_2 = get_top_accounts(df2, '奶皮子糖葫芦')

create_table_image(top_acc_1, '固体杨枝甘露 - 最活跃账号TOP10', '杨枝甘露_活跃账号.png')
create_table_image(top_acc_2, '奶皮子糖葫芦 - 最活跃账号TOP10', '奶皮子_活跃账号.png')

# ============ 4. 互动指标详细统计 ============
stats_metrics = {
    '指标': ['获赞数', '评论数', '分享数', '收藏数'],
    '固体杨枝甘露_平均': [
        f"{df1['获赞数'].mean():.0f}",
        f"{df1['评论数'].mean():.0f}",
        f"{df1['分享数'].mean():.0f}",
        f"{df1['收藏数'].mean():.0f}",
    ],
    '固体杨枝甘露_最高': [
        f"{df1['获赞数'].max():.0f}",
        f"{df1['评论数'].max():.0f}",
        f"{df1['分享数'].max():.0f}",
        f"{df1['收藏数'].max():.0f}",
    ],
    '奶皮子糖葫芦_平均': [
        f"{df2['获赞数'].mean():.0f}",
        f"{df2['评论数'].mean():.0f}",
        f"{df2['分享数'].mean():.0f}",
        f"{df2['收藏数'].mean():.0f}",
    ],
    '奶皮子糖葫芦_最高': [
        f"{df2['获赞数'].max():.0f}",
        f"{df2['评论数'].max():.0f}",
        f"{df2['分享数'].max():.0f}",
        f"{df2['收藏数'].max():.0f}",
    ]
}

df_stats = pd.DataFrame(stats_metrics)
create_table_image(df_stats, '互动指标详细统计', '互动指标详细统计.png')

print("\n✅ 所有表格图片已生成完成!")
