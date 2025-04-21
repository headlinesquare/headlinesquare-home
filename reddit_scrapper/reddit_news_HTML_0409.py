#!/usr/bin/env python
'''
Reddit News Scraper v0.1_HTML (Improved)

Install:
    conda install requests pytz beautifulsoup4
or 
    pip install requests pytz beautifulsoup4

Run:
    python reddit_news_scraper.py Conservative --start 2025-03-23T19:00:00-04:00 \
    --cutoff 2025-03-24T19:00:00-04:00 --reset --output conservative_0324.jsonl
    
    python reddit_news_scraper.py Conservative --start 2025-03-23T19:00:00-04:00 \
    --cutoff 2025-03-26T19:00:00-04:00 --reset --daily_page --output conservative.jsonl
'''

import argparse, json, time, os, requests
from datetime import datetime, timezone, timedelta
from pytz import timezone as tz
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# Use a descriptive user-agent per Reddit's guidelines.
HEADERS = {"User-Agent": "script:reddit_news_scraper:v0.1 (by u/YourRedditUsername)"}
BASE_URL = "https://old.reddit.com/r/{}/new/"
CHECKPOINT = "checkpoint.txt"

def build_session():
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    sess.mount("https://", adapter)
    return sess

def parse_number(text):
    """
    Convert a string like "1.2k" or "45" to an integer.
    Returns 0 if conversion fails or if the text is empty or "•".
    """
    try:
        text = text.strip()
        if text in ["", "•"]:
            return 0
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        return int(text)
    except Exception:
        return 0

def fetch_full_selftext(post_url, sess, timeout=10):
    """
    Given a post URL, fetch its individual page and try to extract the full selftext.
    A timeout (in seconds) is applied to prevent getting stuck.
    Prints an error message whenever a timeout or any other exception occurs.
    """
    if post_url.startswith("/"):
        full_url = "https://old.reddit.com" + post_url
    else:
        full_url = post_url
    try:
        resp = sess.get(full_url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        expando = soup.find("div", class_="expando")
        if expando:
            usertext = expando.find("div", class_="usertext-body")
            if usertext:
                return usertext.get_text(separator="\n").strip()
            else:
                return expando.get_text(separator="\n").strip()
        return ""
    except requests.exceptions.Timeout as te:
        print(f"Timeout error fetching full selftext from {full_url}: {te}")
        return ""
    except Exception as e:
        print(f"Error fetching full selftext from {full_url}: {e}")
        return ""



def fetch_page(sess, subreddit, after=None):
    params = {"count": 25}
    if after:
        params["after"] = after
    resp = sess.get(BASE_URL.format(subreddit), headers=HEADERS, params=params)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    valid_posts = []
    for thing in soup.find_all("div", class_="thing"):
        if thing.get("data-stickied", "false").lower() == "true":
            continue
        classes = thing.get("class", [])
        if "promotedlink" in classes or thing.get("data-promoted", "false").lower() == "true":
            continue

        post = {}
        title_tag = thing.find("a", class_="title")
        title = title_tag.text.strip() if title_tag else ""
        expando = thing.find("div", class_="expando")
        selftext = expando.get_text(separator="\n").strip() if expando else ""
        url_link = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
        score_tag = thing.find("div", class_="score unvoted")
        score_text = score_tag.text.strip() if score_tag else "0"
        score = parse_number(score_text)
        num_comments = 0
        comment_tag = thing.find("a", string=lambda t: t and "comment" in t.lower())
        if comment_tag:
            comment_text = comment_tag.text.strip().split()[0]
            num_comments = parse_number(comment_text)

        domain = thing.get("data-domain", "")
        permalink = thing.get("data-permalink", "")
        author = thing.get("data-author", "")
        fullname = thing.get("data-fullname", "")
        timestamp = thing.get("data-timestamp")
        if timestamp:
            try:
                created_utc = float(timestamp) / 1000
            except:
                created_utc = 0
        else:
            time_tag = thing.find("time")
            if time_tag and time_tag.has_attr("datetime"):
                try:
                    dt = datetime.fromisoformat(time_tag["datetime"])
                    created_utc = dt.timestamp()
                except:
                    created_utc = 0
            else:
                created_utc = 0
        if created_utc == 0:
            continue

        thumbnail = None
        thumb_tag = thing.find("a", class_="thumbnail")
        if thumb_tag:
            img_tag = thumb_tag.find("img")
            if img_tag and img_tag.has_attr("src"):
                thumbnail = img_tag["src"]

        post["created_utc"] = created_utc
        post["title"] = title
        post["selftext"] = selftext  # May be "loading..."
        post["url"] = url_link
        post["score"] = score
        post["num_comments"] = num_comments
        post["domain"] = domain
        post["permalink"] = permalink
        post["author"] = author
        post["fullname"] = fullname
        post["thumbnail"] = thumbnail

        valid_posts.append(post)

    next_button = soup.select_one("span.next-button > a")
    after_param = None
    if next_button and "after=" in next_button["href"]:
        parsed = urlparse(next_button["href"])
        qs = parse_qs(parsed.query)
        if "after" in qs:
            after_param = qs["after"][0]

    return valid_posts, after_param

def load_checkpoint():
    return open(CHECKPOINT).read().strip() if os.path.exists(CHECKPOINT) else None

def save_checkpoint(after):
    with open(CHECKPOINT, "w") as f:
        f.write(after or "")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("subreddit")
    p.add_argument("--start", type=lambda s: datetime.fromisoformat(s), required=True,
                   help="ISO start date (UTC), e.g. 2025-03-23T19:00:00-04:00")
    p.add_argument("--cutoff", type=lambda s: datetime.fromisoformat(s), required=True,
                   help="ISO end date (UTC), e.g. 2025-03-25T19:00:00-04:00")
    p.add_argument("--output", default="posts.jsonl")
    p.add_argument("--reset", action="store_true")
    p.add_argument("--daily_page", action="store_true",
                   help="Split output into daily pages (requires exact 24-hour segments)")
    return p.parse_args()


def main():
    args = parse_args()
    sess = build_session()
    after = None if args.reset else load_checkpoint()

    original_start, original_cutoff = args.start, args.cutoff
    start_dt, end_dt = original_start.astimezone(timezone.utc), original_cutoff.astimezone(timezone.utc)

    # Validate daily_page settings
    base, ext = os.path.splitext(args.output)
    mode = "w" if args.reset else "a"
    if args.daily_page:
        if original_start.timetz() != original_cutoff.timetz():
            print("Error: With --daily_page, start and cutoff must have identical time-of-day.")
            exit(1)
        total_seconds = (end_dt - start_dt).total_seconds()
        num_days = int(total_seconds // (24 * 3600))
        # Open files for each daily segment.
        full_files, simple_files, curated_files = {}, {}, {}
        for i in range(num_days):
            date_str = (original_start + timedelta(days=i+1)).strftime("%m%d%Y")
            full_files[i] = open(f"{base}_{date_str}{ext}", mode, encoding="utf-8")
            simple_files[i] = open(f"{base}_{date_str}_simple{ext}", mode, encoding="utf-8")
            curated_files[i] = open(f"{base}_{date_str}_curated{ext}", mode, encoding="utf-8")
            # Initialize daily article ID counters, starting at 1 for each segment.
            daily_ids = {i: 1 for i in range(num_days)}
    else:
        full_out = open(f"{base}{ext}", mode, encoding="utf-8")
        simple_out = open(f"{base}_simple{ext}", mode, encoding="utf-8")
        curated_out = open(f"{base}_curated{ext}", mode, encoding="utf-8")

    eastern = tz("US/Eastern")
    total = 0 # (used only when not daily_page)

    while True:
        valid_posts, after = fetch_page(sess, args.subreddit, after)
        time.sleep(2)
        if not valid_posts:
            print("No valid posts found on this page.")
            break

        i = 0
        while i < len(valid_posts):
            post = valid_posts[i]
            created = datetime.fromtimestamp(post["created_utc"], timezone.utc)
            if created > end_dt:
                i += 1
                continue

            # This is for the rare exceptions that older posts outside of the coverage window are occasionally mixed with newer posts. 
            if created < start_dt:
                # Look ahead at up to the next 10 posts from the current page.
                subset = valid_posts[i+1:i+11]
                # If there are not enough posts on this page, try fetching one extra page.
                if len(subset) < 10 and after:
                    extra_posts, new_after = fetch_page(sess, args.subreddit, after)
                    time.sleep(2)
                    subset.extend(extra_posts)
                # Check: If all (up to 10) posts are older than start_dt, then stop pagination.
                if subset and all(datetime.fromtimestamp(p["created_utc"], timezone.utc) < start_dt for p in subset):
                    print("Reached posts older than start date; stopping pagination.")
                    after = None
                    break
                else:
                    # Skip this post and continue with the next one.
                    print("Skipped a post created earlier than the coverage window.")
                    i += 1
                    continue

            if post["selftext"].lower() == "loading..." and post.get("url", "").startswith("/"):
                post["selftext"] = fetch_full_selftext(post.get("url"), sess)
                time.sleep(2)
            total += 1

            full_line = json.dumps(post, ensure_ascii=False) + "\n"
            created_eastern = created.astimezone(eastern).isoformat()
            simple_line = json.dumps({
                "created": created_eastern,
                "title": post.get("title"),
                "selftext": post.get("selftext", ""),
                "url": post.get("url"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "domain": post.get("domain"),
                "post_url": f"https://reddit.com{post.get('permalink')}",
                "author": post.get("author"),
            }, ensure_ascii=False) + "\n"
            
            if args.daily_page:
                segment_index = int((created - start_dt).total_seconds() // (24 * 3600))
                curated_id = daily_ids[segment_index]
                daily_ids[segment_index] += 1
            else:
                curated_id = total

            curated_line = json.dumps({
                "id": curated_id,
                "domain": post.get("domain"),
                "title": post.get("title"),
                "url": post.get("url"),
            }, ensure_ascii=False) + "\n"

            if args.daily_page:
                segment_index = int((created - start_dt).total_seconds() // (24 * 3600))
                full_files[segment_index].write(full_line)
                simple_files[segment_index].write(simple_line)
                curated_files[segment_index].write(curated_line)
            else:
                full_out.write(full_line)
                simple_out.write(simple_line)
                curated_out.write(curated_line)
            i += 1

        print(f"Fetched {len(valid_posts)} posts on this page — next after={after} (total {total})")
        save_checkpoint(after)
        if not after:
            break



    # Close file handles.
    if args.daily_page:
        for f in full_files.values():
            f.close()
        for f in simple_files.values():
            f.close()
        for f in curated_files.values():
            f.close()
    else:
        full_out.close(); simple_out.close(); curated_out.close()
    print(f"Done — total posts: {total}")

if __name__ == "__main__":
    main()
