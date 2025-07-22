import re
from serpapi import GoogleScholarSearch
from openai import OpenAI

# ✅ 设置 API 密钥
client = OpenAI(api_key="your_key1")
SERPAPI_KEY = "your_key2"

# ✅ 提取 Google Scholar 用户 ID
def extract_scholar_user_id(url: str) -> str:
    match = re.search(r"user=([\w-]+)", url)
    if not match:
        raise ValueError("❌ 无效的 Google Scholar 链接")
    return match.group(1)

# ✅ 使用 SerpApi 获取学者数据
def get_scholar_data(user_id: str) -> dict:
    print("🔍 正在抓取学者信息...")

    params = {
        "engine": "google_scholar_author",
        "author_id": user_id,
        "api_key": SERPAPI_KEY,
        "num": 100
    }

    search = GoogleScholarSearch(params)
    results = search.get_dict()

    author_info = results.get("author", {})
    publications = results.get("articles", [])

    if not author_info:
        raise ValueError("❌ 未能获取作者信息")

    papers = []
    for pub in publications:
        papers.append({
            "title": pub.get("title", ""),
            "year": int(pub.get("year", 0) or 0),
            "venue": pub.get("publication", ""),
            "citations": pub.get("cited_by", {}).get("value", 0),
            "authors": pub.get("authors", "")
        })

    # 前5引用最多
    top_cited = []
    #top_cited = sorted(papers, key=lambda x: x["citations"], reverse=True)[:5]

    # 最新的5篇（排除重复）
    latest = sorted(papers, key=lambda x: x["year"], reverse=True)[:30]
    latest_unique = []
    seen_titles = {p["title"] for p in top_cited}
    for pub in latest:
        if pub["title"] not in seen_titles:
            latest_unique.append(pub)
            seen_titles.add(pub["title"])
        if len(latest_unique) >= 30:
            break

    final_papers = top_cited + latest_unique

    return {
        "name": author_info.get("name", ""),
        "affiliation": author_info.get("affiliations", ""),
        "papers": final_papers
    }

# ✅ 构建毒舌段子提示词
def generate_prompt(data: dict) -> str:
    prompt = f"""这是一个研究者的信息：
- 名字: {data['name']}
- 单位: {data['affiliation']}
- 代表作:
"""
    for p in data["papers"]:
        prompt += (
            f"  - 《{p['title']}》，{p['venue']}，{p['year']}年，引用 {p['citations']} 次，作者：{p['authors']}\n"
        )

    prompt += """
请用中文写一个毒舌、粗口、但学术专业的段子来评价这位学者。风格必须像一位中文母语的博士/科研狗，在深夜看完论文后忍无可忍、在微信群里狂喷的那种——地道、狠毒、节奏快、有学术信息量。

【格式要求】：
- 开头用一句地道情绪词 + 学术人设分打分，例如：【服了】（6/10）或【笑死】（5/10）
- 正文必须在 500 字以内，密度高、内容狠、节奏快
- 嘴臭风格必须专业懂行，不是泼妇骂街，是“会看论文的人在有理有据地骂”
- 必须提及以下几个点，但不要像讲报告一样写，要自然融入吐槽中：

  1. 研究方向：是在认真做题，还是灌水垃圾论文？
  2. 论文水平：顶会还是水灌？有没有真贡献？
  3. 引用情况：是真影响力，还是互引互捧？
  4. 学术行为：拼命发灌水的打印机，还是有技术也肯干的苦逼人？
  5. 综合判断：是“科研带货男”“学术社牛”“标题大师”“综述皇帝”，还是有点水平？

【风格要求】：
- 语言必须地道、有中国博士的嘴臭感，不能有机翻味
- 可以用粗口/脏话，但别低俗，重点是“毒而精准”
- 不要洋气标题，要用“服了/笑了/操了/卷疯了/呸了”这种真实情绪
- 段子必须读起来爽，像真实博士看完论文后的爆发，不要像ChatGPT在写影评

最后一句话必须毒辣收尾，精准砍人设。

只允许输出一个段子，500字内，说到就走，不准啰嗦。




"""
    return prompt

# ✅ 调用 GPT-4 生成段子
def get_funny_profile_text(prompt: str) -> str:
    print("🧠 正在生成学术毒舌段子...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个毒舌又幽默的资深学术研究者，评论家，你只看重真实工作价值，极度厌恶灌水垃圾论文。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.95
    )
    return response.choices[0].message.content

# ✅ 主程序
def main():
    url = input("🎓 请输入 Google Scholar 链接：\n").strip()

    try:
        user_id = extract_scholar_user_id(url)
        scholar_data = get_scholar_data(user_id)
        prompt = generate_prompt(scholar_data)
        print('\n📝 生成的提示词如下:\n')
        print(prompt)
        output = get_funny_profile_text(prompt)

        print("\n🔥 学者剖析报告：\n")
        print(output)

    except Exception as e:
        print(f"❌ 出错啦: {e}")

if __name__ == "__main__":
    main()
