"""Drive the local web UI for the demo recording (run under Xvfb while ffmpeg captures)."""

import sys
import time

from playwright.sync_api import sync_playwright

QUESTION = sys.argv[1] if len(sys.argv) > 1 else "Is the Python requests library still maintained, or should I switch to httpx?"

CAPTION_JS = """
(text) => {
  let el = document.getElementById('demo-caption');
  if (!el) {
    el = document.createElement('div'); el.id = 'demo-caption';
    el.style.cssText = 'position:fixed;left:50%;bottom:30px;transform:translateX(-50%);max-width:980px;' +
      'background:#1b1a17;color:#f6f3ed;border-radius:10px;padding:13px 22px;' +
      'font:500 17px/1.45 Inter,system-ui,sans-serif;z-index:9999;box-shadow:0 10px 34px rgba(27,26,23,.35);text-align:center';
    document.body.appendChild(el);
  }
  el.textContent = text; el.style.display = text ? 'block' : 'none';
}
"""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                    args=["--start-maximized", "--no-first-run", "--no-default-browser-check", "--disable-infobars"])
        page = browser.new_page(no_viewport=True)
        page.wait_for_timeout(1500)
        cap = lambda t: page.evaluate(CAPTION_JS, t)  # noqa: E731
        page.goto("http://127.0.0.1:8000/")
        cap("citescout: a research agent for developers. Every claim cited, every disagreement flagged. Powered by SerpApi.")
        time.sleep(3)
        cap("Running locally. Ask a real developer question:")
        page.click("#q")
        page.keyboard.type(QUESTION, delay=30)
        time.sleep(1)
        page.click("#go")
        cap("1. The LLM plans searches across SerpApi engines (Google, Google News), each with a purpose")
        page.wait_for_selector("text=results", timeout=60000)
        time.sleep(2)
        cap("2. SerpApi runs the searches in parallel. 3. Live PyPI + GitHub APIs verify versions and activity")
        page.wait_for_selector("text=Cross-checking", timeout=60000)
        time.sleep(2)
        cap("4. The model writes claims that may only cite retrieved evidence ids. Code checks every citation.")
        page.wait_for_selector("#verdict", timeout=100000)
        time.sleep(1)
        cap("Verdict with inline citations: each [E#] opens the exact source")
        time.sleep(4)
        page.mouse.move(900, 400)
        cap("Confidence is computed in code: independent domains, source type, freshness, live registry data")
        page.evaluate("document.querySelector('#out').children[1].scrollIntoView({behavior:'smooth'})")
        time.sleep(5)
        dis = page.query_selector(".disagree")
        if dis:
            cap("Sources disagree: the agent surfaces conflicts instead of hiding them, and says which side the evidence favours")
            dis.scroll_into_view_if_needed()
            page.evaluate("window.scrollBy({top:-60})")
            time.sleep(7)
        cap("Every source is typed: official docs, repository, registry, news, forum... with the SerpApi engine that found it")
        page.evaluate("[...document.querySelectorAll('#out .kicker')].find(h=>h.textContent.startsWith('Evidence'))?.scrollIntoView({behavior:'smooth',block:'start'})")
        time.sleep(6)
        cap("Credits used this run are shown. Results are cached, so re-runs cost 0 SerpApi credits.")
        page.evaluate("window.scrollTo({top:document.body.scrollHeight, behavior:'smooth'})")
        time.sleep(3)
        cap("")
        browser.close()


if __name__ == "__main__":
    main()
