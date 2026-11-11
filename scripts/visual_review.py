#!/usr/bin/env python3
"""Browser QA for the *built* Elementary 1A MkDocs Material page.

Requires: pip install playwright; python -m playwright install chromium
Usage: python scripts/visual_review.py --site-dir site --output-dir visual-review
This never publishes or modifies the public Pages site.
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RELATIVE_PAGE = "elementary/unit_01/lesson_a/"


def inspect(page, theme):
    return page.evaluate("""(theme) => {
        const root = document.documentElement;
        const tables = [...document.querySelectorAll('article table')];
        const headings = [...document.querySelectorAll('article h1, article h2, article h3')];
        const imgs = [...document.querySelectorAll('article img')];
        const details = [...document.querySelectorAll('article details')];
        return {
          viewport: innerWidth, documentWidth: root.scrollWidth,
          overflowPx: Math.max(0, root.scrollWidth - innerWidth),
          theme: document.body.getAttribute('data-md-color-scheme'),
          requestedTheme: theme,
          bodyBackground: getComputedStyle(document.body).backgroundColor,
          headings: headings.map(x => ({tag: x.tagName, text: x.textContent.trim().slice(0, 90)})),
          tables: tables.map((x,i) => {
            const p=x.parentElement;
            return {number:i+1, columns:x.rows[0]?.cells.length||0,
              width:Math.round(x.getBoundingClientRect().width),
              containerWidth:Math.round(p.getBoundingClientRect().width),
              scrollableContainer:p.scrollWidth>p.clientWidth+1,
              firstHeader:x.rows[0]?.textContent.trim().slice(0,65) || ""};
          }),
          images: imgs.map(x => ({src:x.getAttribute('src'), alt:x.getAttribute('alt'),
              loaded:x.complete&&x.naturalWidth>0,
              displayWidth:Math.round(x.getBoundingClientRect().width),
              naturalWidth:x.naturalWidth})),
          collapsedPanels: details.filter(x=>!x.open).length,
          detailsCount: details.length,
          articleHeight: Math.round(document.querySelector('article')?.getBoundingClientRect().height||0)
        };
    }""", theme)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--site-dir", type=Path, default=Path("site"))
    p.add_argument("--output-dir", type=Path, default=Path("visual-review"))
    args=p.parse_args()
    out=args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    failures=[]
    reports=[]
    try:
        from playwright.sync_api import Error
    except ImportError:
        raise SystemExit("Missing playwright")
    with sync_playwright() as tool:
        browser=tool.chromium.launch(headless=True,args=["--no-sandbox"])
        for label,width,height,scheme in [
            ("desktop-light",1440,900,"default"),
            ("desktop-dark",1440,900,"slate"),
            ("mobile-light",390,844,"default"),
            ("mobile-dark",390,844,"slate"),
            ("narrow-mobile-light",320,700,"default"),
        ]:
            ctx=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1,
                                    is_mobile=("mobile" in label),has_touch=("mobile" in label))
            page=ctx.new_page()
            url=(args.site_dir.resolve() / RELATIVE_PAGE / "index.html").as_uri()
            # file:// cannot reliably load MkDocs root assets (/assets/...) => use HTTP server instead.
            url=f"http://127.0.0.1:8765/{RELATIVE_PAGE}"
            errors=[]
            page.on("pageerror", lambda ex: errors.append(str(ex)))
            response=page.goto(url,wait_until="networkidle",timeout=30000)
            if not response or response.status!=200: failures.append(f"{label}: URL did not return HTTP 200")
            # Material applies its color palettes through a body attribute.
            page.evaluate("(scheme) => document.body.setAttribute('data-md-color-scheme', scheme)",scheme)
            page.wait_for_timeout(300)
            report=inspect(page,scheme)
            if report["overflowPx"] > 3: failures.append(f"{label}: horizontal overflow {report['overflowPx']}px")
            if not report["images"]: failures.append(f"{label}: missing illustration")
            for img in report["images"]:
                if not img["loaded"]: failures.append(f"{label}: broken image {img['src']}")
                if not img["alt"]: failures.append(f"{label}: missing alt for {img['src']}")
            if report["detailsCount"] < 5: failures.append(f"{label}: expected >=5 collapsible answer panels")
            panels=page.locator("article details")
            if panels.count():
                panels.first.locator("summary").click()
                if not panels.first.evaluate("(node)=>node.open"):
                    failures.append(f"{label}: answers did not expand")
                panels.first.locator("summary").click()
                if panels.first.evaluate("(node)=>node.open"):
                    failures.append(f"{label}: answers did not collapse")
            for link in page.locator("article a[href^='#']").all():
                href=link.get_attribute("href")
                if href and len(href)>1 and page.locator(f'[id="{href[1:]}"]').count()==0:
                    failures.append(f"{label}: unresolved local heading anchor {href}")
            if errors: failures.append(f"{label}: JS errors {errors[:3]}")
            page.screenshot(path=str(out/f"{label}.png"),full_page=True,animations="disabled")
            report["name"]=label
            report["panelsToggleTest"]="passed" if not any(label in x and "answers" in x for x in failures) else "failed"
            reports.append(report)
            ctx.close()
        browser.close()
    (out/"report.json").write_text(json.dumps({"reports":reports,"failures":failures},indent=2),encoding="utf-8")
    for r in reports:
        print(f"VISUAL {r['name']}: viewport={r['viewport']} document={r['documentWidth']} overflow={r['overflowPx']}; headings={len(r['headings'])}; tables={len(r['tables'])}; images={len(r['images'])}; expandable={r['detailsCount']}; palette={r['theme']}")
    for f in failures: print("VISUAL ERROR:",f,file=sys.stderr)
    print(f"Screenshot artifacts: {out}")
    sys.exit(1 if failures else 0)


if __name__=="__main__":
    main()
