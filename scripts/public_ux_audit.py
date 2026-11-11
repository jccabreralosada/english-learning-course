#!/usr/bin/env python3
"""Non-deploying MkDocs public-site browser audit (includes before/after captures)."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGES = [
    "", "curriculum/", "elementary/", "elementary/unit_01/lesson_a/",
    "elementary/unit_01/lesson_b/", "elementary/unit_01/lesson_c/",
    "pre_intermediate/", "intermediate/", "intermediate_plus/",
    "upper_intermediate/", "advanced/", "advanced_plus/", "reference/",
    "reference/verb-forms/", "reference/everyday-vocabulary/",
    "reference/grammar-rules/", "reference/phrasal-verbs/",
    "reference/collocations/", "reference/useful-expressions/",
    "reference/confusing-words/", "reference/numbers-dates/",
]
CAPTURE = {"", "curriculum/", "elementary/", "reference/", "reference/grammar-rules/", "intermediate/"}
SIZES = [("desktop-light", 1440, 900, "default"),
         ("desktop-dark", 1440, 900, "slate"),
         ("mobile-light", 390, 844, "default"),
         ("mobile-dark", 390, 844, "slate")]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/")
    parser.add_argument("--before-url", default="http://127.0.0.1:8766/")
    parser.add_argument("--output", default="ux-audit")
    args=parser.parse_args()
    output=Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    problems=[]
    results=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        for label, width, height, scheme in SIZES:
            context=browser.new_context(viewport={"width":width,"height":height},
                                        is_mobile=width<500, has_touch=width<500)
            page=context.new_page()
            for path in PAGES:
                response=page.goto(args.base_url+path,wait_until="domcontentloaded",timeout=25000)
                page.evaluate("(scheme)=>document.body.setAttribute('data-md-color-scheme',scheme)",scheme)
                if not response or response.status != 200:
                    problems.append(f"{label} {path}: non-200 response")
                    continue
                details=page.evaluate("""() => {
                    let article=document.querySelector('article');
                    let tables=[...document.querySelectorAll('article table')];
                    let images=[...document.querySelectorAll('article img')];
                    let canScroll=table=>{
                        if(table.getBoundingClientRect().width<=innerWidth+2) return true;
                        let p=table.parentElement;
                        while(p && p!==document.body){
                            let s=getComputedStyle(p);
                            if(p.scrollWidth>p.clientWidth+2&&['auto','scroll'].includes(s.overflowX)){
                                p.scrollLeft=75;
                                let ok=p.scrollLeft>0;
                                p.scrollLeft=0;
                                return ok;
                            }
                            p=p.parentElement;
                        }
                        return false;
                    };
                    return {
                        h1:document.querySelectorAll('article h1').length,
                        width:document.documentElement.scrollWidth,
                        viewport:innerWidth,
                        tables:tables.length,
                        invalidTables:tables.filter(t=>!canScroll(t)).length,
                        missingAlt:images.filter(i=>!i.getAttribute('alt')).length,
                        missingImages:images.filter(i=>!i.complete || !i.naturalWidth).length,
                        internalLeaks:/editorial draft|not approved|development branch|pull request|asset_sha256/i.test(article?.innerText||''),
                        headingCount:document.querySelectorAll('article h2').length
                    };
                }""")
                if details["h1"]!=1: problems.append(f"{label} {path}: H1 count {details['h1']}")
                if details["width"]>details["viewport"]+3: problems.append(f"{label} {path}: global overflow")
                if details["invalidTables"]: problems.append(f"{label} {path}: non-scrollable wide tables")
                if details["missingImages"] or details["missingAlt"]: problems.append(f"{label} {path}: missing image or alt")
                if details["internalLeaks"]: problems.append(f"{label} {path}: internal editorial text visible")
                if path in CAPTURE:
                    slug=path.strip("/").replace("/","-") or "home"
                    page.screenshot(path=str(output/f"after-{slug}-{label}.png"),full_page=(slug in {"home","elementary","reference","intermediate"}))
                results.append({"path":path,"viewport":label,**details})
            context.close()
        # Baseline captures on the original main branch, independently built and served.
        context=browser.new_context(viewport={"width":1440,"height":900})
        page=context.new_page()
        for path in ["","curriculum/","elementary/","reference/","intermediate/"]:
            response=page.goto(args.before_url+path,wait_until="domcontentloaded",timeout=25000)
            if response and response.status==200:
                slug=path.strip("/").replace("/","-") or "home"
                page.screenshot(path=str(output/f"before-{slug}-desktop-light.png"),full_page=True)
        context.close()
        # Check keyboard navigation and an accessible details control.
        context=browser.new_context(viewport={"width":1440,"height":900})
        page=context.new_page()
        page.goto(args.base_url+"elementary/unit_01/lesson_a/",wait_until="domcontentloaded")
        page.keyboard.press("Tab")
        focused=page.evaluate("document.activeElement?.tagName")
        if focused not in ("A","BUTTON","INPUT","SUMMARY"):
            problems.append(f"Keyboard Tab focus unexpected: {focused}")
        panel=page.locator("article details").first
        if panel.count():
            panel.locator("summary").focus()
            page.keyboard.press("Enter")
            if not panel.evaluate("(el)=>el.open"): problems.append("Keyboard Enter did not open solution panel")
        page.goto(args.base_url+"reference/",wait_until="domcontentloaded")
        for slug in ["verb-forms","everyday-vocabulary","grammar-rules","phrasal-verbs",
                     "collocations","useful-expressions","confusing-words","numbers-dates"]:
            if page.locator(f'article a[href*="{slug}"]').count()==0:
                problems.append(f"Quick Reference category link missing: {slug}")
        context.close()
        browser.close()
    (output/"report.json").write_text(json.dumps({"pages":len(PAGES),"checks":len(results),
                         "results":results,"problems":problems},indent=2),encoding="utf-8")
    print(f"Audited {len(PAGES)} pages across four screen/theme combinations: {len(results)} cases")
    for problem in problems: print("AUDIT ERROR:",problem)
    if problems: raise SystemExit(1)

if __name__ == "__main__":
    main()
