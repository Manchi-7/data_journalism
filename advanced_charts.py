import pandas as pd
import matplotlib.pyplot as plt
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

# ============ 1. 雷达图 ============
def create_radar_chart():
    """创建雷达图展示互动数据对比"""
    categories = ['获赞数', '评论数', '分享数', '收藏数']
    
    # 获取平均值
    values1 = [
        df1['获赞数'].mean(),
        df1['评论数'].mean(),
        df1['分享数'].mean(),
        df1['收藏数'].mean()
    ]
    
    values2 = [
        df2['获赞数'].mean(),
        df2['评论数'].mean(),
        df2['分享数'].mean(),
        df2['收藏数'].mean()
    ]
    
    # 数据归一化（以最大值为基准）
    max_value = max(max(values1), max(values2))
    values1_norm = [v / max_value * 100 for v in values1]
    values2_norm = [v / max_value * 100 for v in values2]
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values1_norm += values1_norm[:1]
    values2_norm += values2_norm[:1]
    angles += angles[:1]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 绘制数据
    ax.plot(angles, values1_norm, 'o-', linewidth=2.5, label='固体杨枝甘露', color='#5B9BA6', markersize=8)
    ax.fill(angles, values1_norm, alpha=0.25, color='#5B9BA6')
    
    ax.plot(angles, values2_norm, 'o-', linewidth=2.5, label='奶皮子糖葫芦', color='#8FB3AB', markersize=8)
    ax.fill(angles, values2_norm, alpha=0.25, color='#8FB3AB')
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 添加标题和图例
    plt.title('互动指标对比雷达图', fontsize=16, fontweight='bold', pad=30)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    plt.tight_layout()
    plt.savefig('互动数据雷达图.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 雷达图已保存: 互动数据雷达图.png")
    plt.close()

create_radar_chart()

# ============ 2. 分组柱状图 ============
def create_grouped_bar_chart():
    """创建分组柱状图展示绝对值对比"""
    categories = ['获赞数', '评论数', '分享数', '收藏数']
    
    values1 = [
        df1['获赞数'].mean(),
        df1['评论数'].mean(),
        df1['分享数'].mean(),
        df1['收藏数'].mean()
    ]
    
    values2 = [
        df2['获赞数'].mean(),
        df2['评论数'].mean(),
        df2['分享数'].mean(),
        df2['收藏数'].mean()
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width/2, values1, width, label='固体杨枝甘露', color='#5B9BA6', alpha=0.8)
    bars2 = ax.bar(x + width/2, values2, width, label='奶皮子糖葫芦', color='#8FB3AB', alpha=0.8)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('互动指标', fontsize=12, fontweight='bold')
    ax.set_ylabel('平均数值', fontsize=12, fontweight='bold')
    ax.set_title('互动指标详细对比（绝对值）', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('互动数据分组柱状图.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 分组柱状图已保存: 互动数据分组柱状图.png")
    plt.close()

create_grouped_bar_chart()

# ============ 3. 百分比对比堆积柱 ============
def create_stacked_bar_chart():
    """创建堆积柱状图展示占比对比"""
    values1 = [
        df1['获赞数'].sum(),
        df1['评论数'].sum(),
        df1['分享数'].sum(),
        df1['收藏数'].sum()
    ]
    
    values2 = [
        df2['获赞数'].sum(),
        df2['评论数'].sum(),
        df2['分享数'].sum(),
        df2['收藏数'].sum()
    ]
    
    # 计算占比
    total1 = sum(values1)
    total2 = sum(values2)
    
    pct1 = [v / total1 * 100 for v in values1]
    pct2 = [v / total2 * 100 for v in values2]
    
    categories = ['获赞数', '评论数', '分享数', '收藏数']
    products = ['固体杨枝甘露', '奶皮子糖葫芦']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制堆积柱
    colors = ['#5B9BA6', '#8FB3AB', '#A3C4BC', '#B5D4CB']
    
    bottom1 = np.zeros(1)
    bottom2 = np.zeros(1)
    
    for i, (cat, pct) in enumerate(zip(categories, pct1)):
        ax.bar([0], [pct], bottom=bottom1, label=cat, color=colors[i], alpha=0.8)
        bottom1 += pct
    
    for i, (cat, pct) in enumerate(zip(categories, pct2)):
        ax.bar([1], [pct], bottom=bottom2, color=colors[i], alpha=0.8)
        bottom2 += pct
    
    # 添加百分比标签
    bottom1 = 0
    for pct in pct1:
        ax.text(0, bottom1 + pct/2, f'{pct:.1f}%', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='white')
        bottom1 += pct
    
    bottom2 = 0
    for pct in pct2:
        ax.text(1, bottom2 + pct/2, f'{pct:.1f}%', ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')
        bottom2 += pct
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(products, fontsize=12, fontweight='bold')
    ax.set_ylabel('占比(%)', fontsize=12, fontweight='bold')
    ax.set_title('互动指标占比分布对比', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('互动数据占比堆积图.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ 堆积柱状图已保存: 互动数据占比堆积图.png")
    plt.close()

create_stacked_bar_chart()

print("\n✅ 所有新的图表已生成完成!")
print("   - 互动数据雷达图.png")
print("   - 互动数据分组柱状图.png")
print("   - 互动数据占比堆积图.png")
