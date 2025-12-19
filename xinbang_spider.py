from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

CHROMEDRIVER_PATH = "path/to/chromedriver"  # 请替换为你的chromedriver路径

options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless") 
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--incognito")
options.add_argument("--disable-extensions")

service = Service(CHROMEDRIVER_PATH)

driver = webdriver.Chrome(
    service=service,
    options=options
)

driver.get("https://www.newrank.cn/")

# 登录验证
print("👉 请手动登录新榜，登录完成后回到终端按 Enter")
input()

try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info"))  # 替换为登录成功后的标志性元素
    )
    print("✅ 登录成功")
except:
    print("❌ 登录失败，请重试")
    driver.quit()
    exit()

# 修改显式等待逻辑
def fetch_keyword_trend(keyword):
    url = f"https://www.newrank.cn/xdnphb/keyword?word={keyword}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr"))
        )
    except:
        print(f"❌ 无法加载关键词趋势页面：{keyword}")
        return []

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    records = []
    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 3:
            records.append({
                "keyword": keyword,
                "date": cols[0].text,
                "volume": cols[1].text,
                "hot_index": cols[2].text
            })

    return records

def fetch_content_list(keyword, max_pages=3):
    url = f"https://www.newrank.cn/xdnphb/content?keyword={keyword}"
    driver.get(url)

    results = []
    for _ in range(max_pages):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".content-item"))
            )
        except:
            print(f"❌ 无法加载内容页面：{keyword}")
            break

        items = driver.find_elements(By.CSS_SELECTOR, ".content-item")
        for it in items:
            try:
                title = it.find_element(By.CSS_SELECTOR, ".content-title").text
                stats = it.find_elements(By.CSS_SELECTOR, ".content-stat span")

                results.append({
                    "keyword": keyword,
                    "title": title,
                    "like": stats[0].text if len(stats) > 0 else None,
                    "comment": stats[1].text if len(stats) > 1 else None,
                    "share": stats[2].text if len(stats) > 2 else None
                })
            except:
                continue

        # 翻页
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".next-page"))
            )
            next_btn.click()
            time.sleep(3)
        except:
            print("❌ 无法翻页，可能已到最后一页")
            break

    return results

keywords = ["奶皮子糖葫芦"]

trend_all = []
content_all = []

for kw in keywords:
    print(f"📈 抓取趋势数据：{kw}")
    trend_all.extend(fetch_keyword_trend(kw))

    print(f"🧾 抓取内容数据：{kw}")
    content_all.extend(fetch_content_list(kw))

pd.DataFrame(trend_all).to_csv(
    "keyword_trend.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(content_all).to_csv(
    "content_meta.csv",
    index=False,
    encoding="utf-8-sig"
)

print("✅ 数据采集完成")
driver.quit()
