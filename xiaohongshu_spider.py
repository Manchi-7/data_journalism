"""
xiaohongshu_spider.py   —— 多关键词小红书笔记爬虫（Selenium版）
-------------------------------------------------------------
功能：
1. 关键词列表从 keywords.txt 读取（每行一个关键词）
2. 每个关键词的笔记写入 Excel 独立 Sheet
3. 使用Selenium模拟真实浏览器，绕过API限制
4. 支持自动滚动加载更多内容

使用说明：
1. 需要安装：pip install selenium pandas openpyxl
2. 需要下载ChromeDriver并配置路径
3. 运行前需要手动登录小红书（会自动打开浏览器）

"""

import os, time, random
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


with open("keywords.txt", "r", encoding="utf-8") as f:
    KEYWORD_LIST = [line.strip() for line in f if line.strip()]

MAX_POSTS = 100          # 每个关键词抓取笔记数量
SCROLL_TIMES = 15        # 页面滚动次数（每次滚动加载更多）
CHROMEDRIVER_PATH = "path/to/chromedriver"  # ChromeDriver路径，改为你的实际路径


def init_driver():
    """初始化Chrome浏览器"""
    options = Options()
    # options.add_argument("--headless")  # 无头模式，取消注释可隐藏浏览器窗口
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    # 隐藏webdriver特征
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver


def login_xiaohongshu(driver):
    """打开小红书并等待手动登录"""
    driver.get("https://www.xiaohongshu.com/")
    print("\n👉 请在浏览器中登录小红书账号...")
    print("   登录完成后回到终端按 Enter 继续")
    input()
    
    # 验证登录状态 - 尝试多个可能的选择器
    login_selectors = [
        ".user-info",
        ".avatar", 
        "[class*='avatar']",
        "[class*='user']",
        "img[alt*='头像']",
        ".login-container",  # 如果能找到这个说明未登录
    ]
    
    is_logged_in = False
    for selector in login_selectors[:-1]:  # 排除最后一个（未登录标识）
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✅ 检测到登录元素: {selector}")
                is_logged_in = True
                break
        except:
            continue
    
    if not is_logged_in:
        # 检查是否有未登录的标识
        try:
            driver.find_element(By.CSS_SELECTOR, ".login-container")
            print("⚠️  检测到未登录标识，但将继续尝试...")
        except:
            # 找不到未登录标识，可能是已登录
            print("✅ 未检测到明确登录元素，但页面正常，将继续...")
    
    return True  # 总是返回True继续执行


def scroll_to_load_more(driver, times=5):
    """滚动页面以加载更多内容"""
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 3))
        print(f"  📜 滚动 {i+1}/{times}")


def crawl_keyword(driver, keyword: str, max_posts: int) -> pd.DataFrame:
    """爬取指定关键词的笔记"""
    rows = []
    
    # 构建搜索URL
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
    
    print(f"\n正在爬取关键词: '{keyword}'")
    driver.get(search_url)
    time.sleep(3)
    
    # 滚动加载更多
    scroll_to_load_more(driver, SCROLL_TIMES)
    
    try:
        # 等待笔记列表加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.note-item, .feeds-container a"))
        )
    except TimeoutException:
        print(f"  ⚠️  未找到笔记列表，可能页面结构已变化")
        return pd.DataFrame()
    
    # 尝试多种选择器
    selectors = [
        "section.note-item",
        ".feeds-container a.cover",
        "a[href*='/explore/']",
        ".note-item",
    ]
    
    note_elements = []
    for selector in selectors:
        note_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if note_elements:
            print(f"  ✓ 使用选择器: {selector}, 找到 {len(note_elements)} 个笔记")
            break
    
    if not note_elements:
        print(f"  ✗ 未找到任何笔记元素")
        return pd.DataFrame()
    
    # 提取数据
    for idx, elem in enumerate(note_elements[:max_posts]):
        try:
            # 提取笔记链接 - 优先从元素本身获取，否则查找子元素中的a标签
            link = elem.get_attribute("href") or ""
            
            # 如果元素本身没有href，尝试在内部查找a标签
            if not link:
                try:
                    link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                    link = link_elem.get_attribute("href") or ""
                except NoSuchElementException:
                    pass
            
            # 调试输出
            if idx < 3:  # 只输出前3个元素的调试信息
                print(f"  [调试] 元素{idx+1} link: {link[:80] if link else '无链接'}")
            
            # 如果找到链接且包含关键路径，提取note_id
            note_id = ""
            if link and ("/explore/" in link or "/discovery/item/" in link):
                note_id = link.split("/")[-1].split("?")[0]
            else:
                # 如果没有有效链接，仍然尝试提取其他信息
                note_id = f"note_{idx+1}"
            
            # 尝试提取标题
            title = ""
            try:
                # 尝试多个可能的标题选择器
                title_selectors = [".title", ".note-title", "span.title", ".footer .title"]
                for sel in title_selectors:
                    try:
                        title_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        title = title_elem.text.strip()
                        if title:
                            break
                    except NoSuchElementException:
                        continue
                
                # 如果还是没有标题，获取整个元素的文本
                if not title:
                    title = elem.text.strip()[:100]  # 取前100字符
                    
            except Exception:
                title = f"笔记_{idx+1}"
            
            # 尝试提取作者
            user = ""
            try:
                user_selectors = [".author", ".username", ".name", ".author-wrapper .name"]
                for sel in user_selectors:
                    try:
                        user_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        user = user_elem.text.strip()
                        if user:
                            break
                    except NoSuchElementException:
                        continue
            except Exception:
                user = "未知"
            
            # 尝试提取点赞数
            likes = 0
            try:
                like_selectors = [".like-count", ".likes", ".interaction .count", "span[class*='like']", ".footer-container .count"]
                for sel in like_selectors:
                    try:
                        like_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        likes_text = like_elem.text.strip()
                        # 处理可能的k、w等单位
                        if 'w' in likes_text:
                            likes = int(float(''.join(filter(lambda x: x.isdigit() or x == '.', likes_text))) * 10000)
                        elif 'k' in likes_text.lower():
                            likes = int(float(''.join(filter(lambda x: x.isdigit() or x == '.', likes_text))) * 1000)
                        else:
                            likes = int(''.join(filter(str.isdigit, likes_text))) if likes_text else 0
                        if likes > 0:
                            break
                    except (NoSuchElementException, ValueError):
                        continue
            except Exception:
                likes = 0
            
            # 尝试提取评论数
            comments = 0
            try:
                comment_selectors = [".comment-count", ".comments", "span[class*='comment']", ".footer-container .comment"]
                for sel in comment_selectors:
                    try:
                        comment_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        comments_text = comment_elem.text.strip()
                        # 处理可能的k、w等单位
                        if 'w' in comments_text:
                            comments = int(float(''.join(filter(lambda x: x.isdigit() or x == '.', comments_text))) * 10000)
                        elif 'k' in comments_text.lower():
                            comments = int(float(''.join(filter(lambda x: x.isdigit() or x == '.', comments_text))) * 1000)
                        else:
                            comments = int(''.join(filter(str.isdigit, comments_text))) if comments_text else 0
                        if comments > 0:
                            break
                    except (NoSuchElementException, ValueError):
                        continue
            except Exception:
                comments = 0
            
            # 尝试提取发布日期
            publish_date = ""
            try:
                date_selectors = [".publish-date", ".date", "span[class*='time']", ".footer-container .time"]
                for sel in date_selectors:
                    try:
                        date_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        publish_date = date_elem.text.strip()
                        if publish_date:
                            break
                    except NoSuchElementException:
                        continue
            except Exception:
                publish_date = "未知"
            
            # 尝试提取词条/标签
            tags = ""
            try:
                tag_selectors = [".tag", ".tags", "[class*='tag']", ".footer-container .tag"]
                tag_elements = []
                for sel in tag_selectors:
                    try:
                        tag_elements = elem.find_elements(By.CSS_SELECTOR, sel)
                        if tag_elements:
                            break
                    except NoSuchElementException:
                        continue
                
                if tag_elements:
                    tags = ", ".join([tag.text.strip() for tag in tag_elements[:5] if tag.text.strip()])  # 最多取5个标签
            except Exception:
                tags = ""
            
            # 只要有标题就保存数据（不再强制要求link包含explore）
            if title and title != f"笔记_{idx+1}":
                rows.append({
                    "笔记ID": note_id,
                    "标题": title,
                    "用户": user if user else "未知",
                    "发布日期": publish_date if publish_date else "未知",
                    "点赞数": likes,
                    "评论数": comments,
                    "词条/标签": tags if tags else "无",
                    "链接": link if link else "无",
                })
            
        except Exception as e:
            print(f"  ⚠️  提取第 {idx+1} 个笔记数据失败: {e}")
            continue
    
    print(f"  ✓ 成功提取 {len(rows)} 条笔记数据")
    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("小红书笔记爬虫 (Selenium版)")
    print("=" * 60)
    
    # 初始化浏览器
    driver = init_driver()
    
    try:
        # 登录
        login_xiaohongshu(driver)
        
        # 开始爬取
        with pd.ExcelWriter("xiaohongshu_data.xlsx", engine="openpyxl") as writer:
            for keyword in KEYWORD_LIST:
                df = crawl_keyword(driver, keyword, MAX_POSTS)
                
                if df.empty:
                    print(f"  ⚠️  关键词 '{keyword}' 无数据")
                    continue
                
                # 保存到Excel
                sheet_name = keyword[:31]  # Sheet名限制31字符
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  ✅ 关键词 '{keyword}' 写入完成（{len(df)} 条）\n")
                
                # 间隔时间，避免请求过快
                time.sleep(random.uniform(2, 4))
        
        print("\n" + "=" * 60)
        print("✅ 所有数据已保存到 xiaohongshu_data.xlsx")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
    finally:
        print("\n关闭浏览器...")
        driver.quit()


if __name__ == "__main__":
    main()
