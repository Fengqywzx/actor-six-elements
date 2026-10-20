#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行动者六要素 · 生命操作系统 — 构建脚本
用法: python build.py
产出: index.html（单文件独立网站）+ obsidian-vault/（Obsidian 知识库）
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
PARTS = os.path.join(ROOT, "parts")
OUT = os.path.join(ROOT, "index.html")
VAULT = os.path.join(ROOT, "obsidian-vault")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def merge_hegel():
    root = {
        "id": "logic",
        "title": "黑格尔《逻辑学》",
        "de": "Wissenschaft der Logik",
        "summary": "黑格尔哲学体系的基石，研究纯粹思想规定的自我展开：从最贫瘠的'存在'出发，经过本质的反思，最终到达'绝对理念'。全书是一条思想的朝圣路——思想在自己展开自己的过程中获得全部内容。对行动者而言：逻辑学不是书斋知识，而是把'混乱的经验'整理成'可行动的体系'的元方法。",
        "key": "逻辑学是研究理念的科学——理念是自在自为的真，是概念的总体。",
        "children": [
            load("hegel_part1_being.json"),
            load("hegel_part2_essence.json"),
            load("hegel_part3_concept.json"),
        ],
    }
    return {
        "meta": {
            "title": "黑格尔《逻辑学》全章节思维导图",
            "subtitle": "Wissenschaft der Logik（大逻辑）· 存在论 / 本质论 / 概念论",
            "source": "依据黑格尔《逻辑学》（1812/1813 年初版，1832 年第二版）原始文本逐章誊写整理",
            "note": "每个节点含：核心命题 · 辩证运动 · 关键句 · 与行动者六要素的落地关联",
        },
        "root": root,
    }


def count_nodes(n):
    return 1 + sum(count_nodes(c) for c in n.get("children", []) or [])


def build_site():
    hegel = merge_hegel()
    total = count_nodes(hegel["root"]) - 1
    hegel["meta"]["count"] = total
    data = {
        "framework": load("framework.json"),
        "hegel": hegel,
        "videos": load("videos.json"),
    }
    js_data = "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"

    html = ""
    for part in ["01_head.html", "02_hero.html", "03_framework.html", "04_mindmap.html",
                 "05_videos.html", "06_livestream.html", "07_treehole.html", "08_scripts.html"]:
        with open(os.path.join(PARTS, part), encoding="utf-8") as f:
            html += f.read() + "\n"
    assert "/*__DATA__*/" in html, "数据注入点缺失"
    html = html.replace("/*__DATA__*/", js_data)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[build] index.html 生成成功: {os.path.getsize(OUT)/1024:.1f} KB, 逻辑学节点 {total} 个")
    return data


# ---------------- Obsidian 知识库 ----------------
def slug(s):
    keep = []
    for ch in s:
        if ch.isalnum() or ch in "·－—()（）":
            keep.append(ch)
        elif ch in "/\\ ":
            keep.append("-")
    return "".join(keep)[:60] or "node"


def walk_nodes(n, path, out):
    out.append((n, path))
    for ch in n.get("children", []) or []:
        walk_nodes(ch, path + [ch["title"]], out)


def build_vault(data):
    if os.path.exists(VAULT):
        shutil.rmtree(VAULT)
    os.makedirs(VAULT)

    hegel = data["hegel"]["root"]
    fw = data["framework"]
    vids = data["videos"]

    nodes = []
    walk_nodes(hegel, [hegel["title"]], nodes)
    slug_by_title = {n["title"]: slug(n["title"]) for n, _ in nodes}

    # ---- 0. 索引 MOC ----
    idx = ["# 行动者六要素 · 生命操作系统 — 知识库索引", "",
           "> 基于黑格尔《逻辑学》的个人行动体系。本库由 build.py 自动生成，可整体拖入 Obsidian 打开。", "",
           "## 快速入口", "",
           "- [[00-行动者六要素总纲|行动者六要素总纲]]",
           "- [[00-未明子行动建议研究总纲|未明子行动建议研究]]",
           "- [[00-黑格尔逻辑学总纲|黑格尔逻辑学总纲]]",
           "", "## 黑格尔《逻辑学》章节树", ""]
    for n, path in nodes:
        if n is hegel:
            continue
        depth = len(path) - 2
        idx.append("  " * max(0, depth) + f"- [[{slug_by_title[n['title']]}|{n['title']}]]")
    idx.append("")
    with open(os.path.join(VAULT, "00-知识库索引.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx))

    # ---- 1. 六要素总纲 ----
    lines = ["---", "title: 行动者六要素总纲", "tags: [MOC, 行动者系统, 六要素]", "---", "",
             "# 行动者的六个要素", "", fw["meta"]["note"], "", "> " + fw["meta"]["structure"], "",
             "## 六要素一览", ""]
    for el in fw["elements"]:
        fn = "01-要素-" + slug(el["title"])
        badge = "⚡ 根本能力" if el["type"] == "engine" else "🧩 附着主题"
        lines.append(f"### [[{fn}|{el['title']}]] · {badge}")
        lines.append(f"- 格言：{el['motto']}")
        lines.append(f"- 概要：{el['summary']}")
        lines.append("")
    lines += ["## 照片原始誊写", "", "### 照片一"]
    lines += [f"- {x}" for x in fw["transcription"]["photo1"]]
    lines += ["", "### 照片二"]
    lines += [f"- {x}" for x in fw["transcription"]["photo2"]]
    lines += ["", "## 相关", "", "- [[00-黑格尔逻辑学总纲]]", "- [[00-未明子行动建议研究总纲]]"]
    with open(os.path.join(VAULT, "00-行动者六要素总纲.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- 2. 每个要素的笔记 ----
    for el in fw["elements"]:
        fn = "01-要素-" + slug(el["title"]) + ".md"
        c = ["---", f"title: {el['title']}", f"tags: [六要素, {el['title']}]", "---", "",
             f"# {el['title']}", "", f"> {el['motto']}", "", el["summary"], "", "## 要点", ""]
        for p in el["points"]:
            c += [f"### {p['title']}", p["detail"], ""]
        c += ["## 逻辑学根据", el["hegelLink"], "", "## 未明子行动建议", el["weimingziLink"], "",
              "## 相关", "", "- [[00-行动者六要素总纲]]", "- [[00-黑格尔逻辑学总纲]]"]
        with open(os.path.join(VAULT, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(c))

    # ---- 3. 黑格尔逻辑学笔记（逐章） ----
    hg_lines = ["---", "title: 黑格尔逻辑学总纲", "tags: [MOC, 黑格尔, 逻辑学]", "---", "",
                "# 黑格尔《逻辑学》总纲", "", hegel["summary"], "", "## 三编结构", ""]
    for book in hegel["children"]:
        fn = "02-逻辑学-" + slug(book["title"])
        hg_lines.append(f"### [[{fn}|{book['title']}]]（{book['de']}）")
        hg_lines.append(book["summary"])
        hg_lines.append("")
    hg_lines += ["## 相关", "- [[00-行动者六要素总纲]]", "- [[00-未明子行动建议研究总纲]]"]
    with open(os.path.join(VAULT, "00-黑格尔逻辑学总纲.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(hg_lines))

    for n, path in nodes:
        if n is hegel:
            continue
        fn = slug(n["title"]) + ".md"
        c = ["---", f"title: {n['title']}", f"tags: [黑格尔, 逻辑学, {path[1] if len(path) > 1 else '总论'}]", "---", "",
             f"# {n['title']}", ""]
        if n.get("de"):
            c += [f"*{n['de']}*", ""]
        if n.get("summary"):
            c += ["## 核心命题", n["summary"], ""]
        if n.get("key"):
            c += ["## 关键句", f"> {n['key']}", ""]
        if n.get("action"):
            c += ["## 与行动者系统的关联", n["action"], ""]
        # 双链：正文中提到其他章节标题的自动链接
        text = (n.get("summary", "") + " " + (n.get("key") or "") + " " + (n.get("action") or ""))
        links = sorted({t for t in slug_by_title if t != n["title"] and len(t) >= 2 and t in text})
        c += ["## 相关概念", ""]
        if links:
            c += [f"- [[{slug_by_title[t]}|{t}]]" for t in links]
        else:
            c.append("- （见 [[00-知识库索引]]）")
        c += ["", "- [[00-黑格尔逻辑学总纲]]"]
        with open(os.path.join(VAULT, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(c))

    # ---- 4. 未明子研究 ----
    w_lines = ["---", "title: 未明子行动建议研究总纲", "tags: [MOC, 未明子, 视频研究]", "---", "",
               "# 未明子 · 行动建议视频全景研究", "",
               f"- UP主：{vids['meta']['up']}（UID {vids['meta']['uid']}）",
               f"- 空间：{vids['meta']['space']}",
               f"- 直播：{vids['meta']['live']}",
               f"- 方法：{vids['meta']['method']}", "",
               "## 系列划分", ""]
    for s in vids["series"]:
        w_lines.append(f"- **{s['name']}**（{s['count']} 个）：{s['desc']}")
    w_lines += ["", "## 视频清单", ""]
    for v in vids["videos"]:
        fn = "03-未明子-" + slug(v["title"])
        w_lines.append(f"### [[{fn}|{v['title']}]]")
        w_lines.append(f"- {v['date']} · {v['duration']} · {v['category']} · 播放 {v['views']}")
        w_lines.append(f"- 核心：{v['core']}")
        w_lines.append("")
    w_lines += ["## 资料来源", ""]
    w_lines += [f"- {s}" for s in vids["sources_list"]]
    w_lines += ["", "## 相关", "- [[00-行动者六要素总纲]]", "- [[00-黑格尔逻辑学总纲]]"]
    with open(os.path.join(VAULT, "00-未明子行动建议研究总纲.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(w_lines))

    for v in vids["videos"]:
        fn = "03-未明子-" + slug(v["title"]) + ".md"
        c = ["---", f"title: {v['title']}", f"tags: [未明子, 视频研究, {v['category']}]", "---", "",
             f"# {v['title']}", "",
             (f"- 链接：https://www.bilibili.com/video/{v['id']}" if v["id"].startswith("BV") else f"- 来源：{v['id']}"),
             f"- 日期：{v['date']} · 时长：{v['duration']} · 播放：{v['views']}", "",
             "## 核心观点", v["core"], "", "## 要点", ""]
        c += [f"- {p}" for p in v["keyPoints"]]
        c += ["", "## 现实落地报告", v["actionReport"], "", f"**资料来源**：{v['sources']}", "",
              "## 相关", "- [[00-未明子行动建议研究总纲]]", "- [[00-行动者六要素总纲]]"]
        with open(os.path.join(VAULT, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(c))

    # ---- 5. Obsidian Canvas 画布 ----
    canvas = {"nodes": [], "edges": []}
    canvas["nodes"].append({"id": "root", "type": "text",
                            "text": "黑格尔《逻辑学》\nWissenschaft der Logik\n三编 · 全部章节",
                            "x": 0, "y": 0, "width": 300, "height": 120, "color": "1"})
    y = 260
    for book in hegel["children"]:
        bid = "b" + slug(book["title"])
        canvas["nodes"].append({"id": bid, "type": "text",
                                "text": f"{book['title']}\n{book['de']}\n{book['summary'][:50]}…",
                                "x": -160, "y": y, "width": 320, "height": 110, "color": "2"})
        canvas["edges"].append({"id": "e" + bid, "fromNode": "root", "toNode": bid,
                                "fromSide": "bottom", "toSide": "top"})
        py = y
        for part in book.get("children", []):
            pid = bid + slug(part["title"])
            canvas["nodes"].append({"id": pid, "type": "text",
                                    "text": f"{part['title']}\n{part.get('de', '')}",
                                    "x": 260, "y": py, "width": 260, "height": 80, "color": "3"})
            canvas["edges"].append({"id": "e" + pid, "fromNode": bid, "toNode": pid,
                                    "fromSide": "right", "toSide": "left"})
            py += 100
        y += max(260, py - y + 60)
    with open(os.path.join(VAULT, "黑格尔逻辑学.canvas"), "w", encoding="utf-8") as f:
        json.dump(canvas, f, ensure_ascii=False, indent=1)

    print(f"[build] Obsidian 知识库生成成功: {len(os.listdir(VAULT))} 个文件 -> {VAULT}")


if __name__ == "__main__":
    d = build_site()
    build_vault(d)
    print("[build] 全部完成 ✓")
