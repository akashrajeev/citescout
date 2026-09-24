"""Drive the local web UI for the round-2 demo recording (run under Xvfb while ffmpeg captures).

Logs the time of every caption change to demo/out/beats.txt so the voiceover can be mixed
onto the same cut points.
"""

import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

from record_web import CAPTION_JS

QUESTION = sys.argv[1] if len(sys.argv) > 1 else "Is the Python requests library still maintained, or should I switch to httpx?"
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else time.time()
BEATS = open("demo/out/beats.txt", "w")


def scroll_to(page, kicker: str) -> None:
    page.evaluate("(k) => [...document.querySelectorAll('#out .kicker')].find(h => h.textContent.startsWith(k))"
                  "?.closest('.card')?.scrollIntoView({behavior: 'smooth', block: 'start'})", kicker)


def main() -> None:
    with sync_playwright() as p:
        # Real kiosk window (no tabs or URL bar) filling the 1280x800 frame; Playwright attaches over CDP.
        chrome = subprocess.Popen(["/usr/bin/google-chrome", "--kiosk", "--window-position=0,0", "--window-size=1280,800",
                                   "--no-first-run", "--no-default-browser-check", "--disable-infobars",
                                   "--remote-debugging-port=9333", "--user-data-dir=/tmp/citescout-demo-chrome",
                                   "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = browser.contexts[0].pages[0]
        page.wait_for_timeout(1500)

        def cap(name: str, text: str) -> None:
            page.evaluate(CAPTION_JS, text)
            BEATS.write(f"{time.time() - T0:.2f}\t{name}\n")
            BEATS.flush()

        page.goto("http://127.0.0.1:8000/")
        cap("intro", "citescout: a developer research agent that is not allowed to show you an unsourced claim. Powered by SerpApi.")
        time.sleep(9.7)
        cap("ask", "Running locally. Ask a real developer question:")
        page.click("#q")
        page.keyboard.type(QUESTION, delay=30)
        time.sleep(1)
        page.click("#go")
        cap("plan", "The LLM plans searches across SerpApi engines: Google, Google News, and Google Trends for comparisons")
        page.wait_for_selector("text=results", timeout=60000)
        time.sleep(2)
        cap("verify", "Live PyPI, GitHub, download counts and OSV.dev advisories check the facts")
        page.wait_for_selector("#trace >> text=/[Rr]ound 2|gaps/", timeout=120000)
        time.sleep(1)
        cap("round2", "Round 2: code lists what the first draft couldn't settle, and the agent runs targeted follow-up searches")
        page.wait_for_selector("#verdict", timeout=180000)
        time.sleep(1)
        cap("verdict", "Verdict with inline citations: each [E#] opens the exact source")
        time.sleep(7.2)
        scroll_to(page, "Claims")
        cap("deepread", "Deep-read: every version, number and date in a claim is checked against the full cited page or a live API record")
        time.sleep(13.6)
        scroll_to(page, "Side by side")
        cap("compare", "Side by side, built in code from primary data only. Every cell cites its record.")
        time.sleep(9.9)
        page.evaluate("[...document.querySelectorAll('#out .kicker')].find(h => h.textContent.startsWith('Google Trends'))"
                      "?.scrollIntoView({behavior: 'smooth', block: 'center'})")
        cap("trends", "Search interest over 12 months from SerpApi's Google Trends engine")
        time.sleep(6.5)
        if page.query_selector(".disagree"):
            scroll_to(page, "Sources disagree")
            cap("disagree", "Where sources disagree, citescout says so, and which side the evidence favours")
            time.sleep(7.3)
        scroll_to(page, "Round 2")
        cap("gaps", "The gaps from the first draft, and the follow-up searches they turned into")
        time.sleep(6.2)
        scroll_to(page, "Evidence")
        cap("evidence", "Every source is typed, with the engine that found it. Cached re-runs cost 0 credits.")
        time.sleep(5.5)
        page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        cap("export", "Export the brief as Markdown or JSON")
        time.sleep(3.6)
        cap("end", "")
        browser.close()
        chrome.terminate()


if __name__ == "__main__":
    main()
