#!/usr/bin/env python3
"""support.html の <details> から FAQPage 構造化データを生成して埋め込む。

    python3 tools/build_faq_ld.py

Google のリッチリザルト（検索結果に質問が展開される）を狙う。無料で露出が増える。
本文と1文字でもずれると規約違反になるので、必ずHTMLから機械的に抜き出すこと。
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "support.html"
M0, M1 = "<!-- BUILD:faqld -->", "<!-- /BUILD:faqld -->"


def text_of(fragment: str) -> str:
    """タグを落として素のテキストにする。リンクは文言だけ残す。"""
    s = re.sub(r"<br\s*/?>", " ", fragment)
    s = re.sub(r"</(p|li|ol|ul|div)>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    s = SRC.read_text()
    body = re.sub(re.escape(M0) + r".*?" + re.escape(M1), "", s, flags=re.S)

    qas = []
    for m in re.finditer(r"<details>\s*<summary>(.*?)</summary>\s*<div class=\"a\">(.*?)</div>\s*</details>",
                         body, re.S):
        q = text_of(m.group(1))
        a = text_of(m.group(2))
        if not q or not a:
            continue
        # 長すぎる回答は検索結果に出ないので切る（本文は変えない）
        if len(a) > 1200:
            a = a[:1190].rstrip() + "…"
        qas.append((q, a))

    # 同じ質問文が複数アプリにあるので、質問文で重複を除く（先に出たものを残す）
    seen, uniq = set(), []
    for q, a in qas:
        if q in seen:
            continue
        seen.add(q)
        uniq.append((q, a))

    ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in uniq
        ],
    }
    blk = ('\n<script type="application/ld+json">\n'
           + json.dumps(ld, ensure_ascii=False, indent=2)
           + "\n</script>\n")

    if M0 in s:
        s = re.sub(re.escape(M0) + r".*?" + re.escape(M1), M0 + blk + M1, s, flags=re.S)
    else:
        i = s.index("</head>")
        s = s[:i] + M0 + blk + M1 + "\n" + s[i:]
    SRC.write_text(s)
    print(f"FAQPage: {len(uniq)}件の質問を埋め込み（重複 {len(qas) - len(uniq)}件を除外）")


if __name__ == "__main__":
    main()
