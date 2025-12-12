# apis/collectors.py
import os
import requests
import time
from time import sleep
from concurrent.futures import ThreadPoolExecutor

# ---------------------------
# CONFIG
# ---------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
GITHUB_API = "https://api.github.com"
CF_API = "https://codeforces.com/api"
LC_GRAPHQL = "https://leetcode.com/graphql"


# ---------------------------
# GENERIC GET JSON WITH RETRIES
# ---------------------------
def _get_json(url, headers=None, max_retries=3, timeout=10):
    headers = headers or {}
    last_exc = None
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.json(), r.headers
        except requests.RequestException as e:
            last_exc = e
            sleep(1 + attempt * 0.5)
    raise last_exc


# ---------------------------
# GITHUB LINK HEADER PARSER
# ---------------------------
def _parse_link_header(link):
    if not link:
        return None
    parts = link.split(',')
    for p in parts:
        if 'rel="last"' in p:
            return p.split(";")[0].strip().strip("<>")
    return None


# ============================================================
#  GITHUB
# ============================================================
def fetch_github(username, per_page=100, max_pages=5):
    if not username:
        return {"repos": [], "repos_count": 0, "total_commits_estimate": 0}

    repos_out = []
    total_known_commits = 0
    page = 1

    try:
        while True:
            url = f"{GITHUB_API}/users/{username}/repos?per_page={per_page}&page={page}&type=owner&sort=updated"
            data, headers = _get_json(url, headers=GITHUB_HEADERS, timeout=15)

            if not isinstance(data, list) or not data:
                break

            for repo in data:
                name = repo.get("name")
                full_name = repo.get("full_name")
                html_url = repo.get("html_url")

                # Count commits
                commits_count = 0
                last_commit_date = ""
                try:
                    commits_api = f"{GITHUB_API}/repos/{full_name}/commits?per_page=1"
                    cj, ch = _get_json(commits_api, headers=GITHUB_HEADERS, timeout=10)

                    if isinstance(cj, list) and cj:
                        last_commit_date = cj[0].get("commit", {}).get("committer", {}).get("date", "")

                    last_url = _parse_link_header(ch.get("Link", "") if ch else "")
                    if last_url:
                        try:
                            commits_count = int(last_url.split("page=")[-1].split("&")[0])
                        except:
                            commits_count = 1
                    else:
                        commits_count = len(cj) if isinstance(cj, list) else 0
                except:
                    commits_count = 0

                repos_out.append({
                    "name": name,
                    "full_name": full_name,
                    "html_url": html_url,
                    "commits_count": commits_count,
                    "last_commit_date": last_commit_date
                })

                total_known_commits += commits_count

            page += 1
            if page > max_pages:
                break

        return {
            "repos": repos_out,
            "repos_count": len(repos_out),
            "total_commits_estimate": total_known_commits
        }

    except Exception as e:
        return {"error": f"GitHub error: {e}", "repos": [], "repos_count": 0, "total_commits_estimate": 0}


# ============================================================
#  CODEFORCES — ONLY SOLVED COUNT + RATING
# ============================================================
def fetch_codeforces(handle):
    if not handle:
        return {"solved_count": 0, "rating": None, "maxRating": None, "rank": None, "maxRank": None}

    try:
        # 1) user info
        info_url = f"{CF_API}/user.info?handles={handle}"
        js, _ = _get_json(info_url, timeout=10)
        if js.get("status") != "OK":
            return {"solved_count": 0}

        user = js["result"][0]
        rating = user.get("rating")
        maxRating = user.get("maxRating")
        rank = user.get("rank")
        maxRank = user.get("maxRank")

        # 2) count solved
        subs_url = f"{CF_API}/user.status?handle={handle}"
        subs, _ = _get_json(subs_url, timeout=10)

        solved_count = 0
        if subs.get("status") == "OK":
            for sub in subs["result"]:
                if sub.get("verdict") == "OK":
                    solved_count += 1

        return {
            "solved_count": solved_count,
            "rating": rating,
            "maxRating": maxRating,
            "rank": rank,
            "maxRank": maxRank
        }

    except Exception as e:
        return {"error": f"CF error: {e}", "solved_count": 0}


# ============================================================
#  LEETCODE — PROBLEM COUNTS ONLY
# ============================================================
def fetch_leetcode(username):
    if not username:
        return {"total_solved": 0, "problems": []}

    endpoints = [
        f"https://leetcode-stats-api.herokuapp.com/{username}",
        f"https://leetcode-stats.vercel.app/{username}"
    ]

    for url in endpoints:
        try:
            js, _ = _get_json(url, timeout=8)
            if isinstance(js, dict):
                total = js.get("totalSolved") or js.get("total_solved")
                return {"total_solved": int(total or 0), "problems": []}
        except:
            continue

    # fallback GraphQL
    try:
        payload = {
            "query": """
            query userProfile($username: String!) {
              matchedUser(username: $username) {
                submitStats {
                  acSubmissionNum { difficulty count }
                }
              }
            }
            """,
            "variables": {"username": username}
        }
        r = requests.post(LC_GRAPHQL, json=payload, timeout=8)
        r.raise_for_status()
        data = r.json()

        ac_list = data.get("data", {}).get("matchedUser", {}).get("submitStats", {}).get("acSubmissionNum", [])
        total = sum(int(x.get("count", 0)) for x in ac_list)
        return {"total_solved": total, "problems": []}

    except:
        return {"total_solved": 0, "problems": []}


# ============================================================
#  COMBINED FETCH
# ============================================================
def fetch_all_for_student(platform_map, parallel=True):
    pm = {k.lower(): v for k, v in platform_map.items()} if isinstance(platform_map, dict) else {}

    gh = pm.get("github")
    lc = pm.get("leetcode")
    cf = pm.get("codeforces")

    result = {}

    if parallel:
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = {
                "github": ex.submit(fetch_github, gh),
                "leetcode": ex.submit(fetch_leetcode, lc),
                "codeforces": ex.submit(fetch_codeforces, cf)
            }
            for k, fut in futs.items():
                result[k] = fut.result()
    else:
        result["github"] = fetch_github(gh)
        result["leetcode"] = fetch_leetcode(lc)
        result["codeforces"] = fetch_codeforces(cf)

    return result
