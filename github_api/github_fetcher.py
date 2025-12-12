# github_api/github_fetcher.py
from apis.collectors import fetch_github

def fetch_github_data_for_user(username):
    """
    Backwards-compatible function name used elsewhere in your codebase.
    Returns: { "repos": [ ... ] } to match previous structure
    """
    data = fetch_github(username)
    # convert to previous expected format
    return {
        "repos": data.get("repos", []),
        "repos_count": data.get("repos_count", 0),
        "total_commits_estimate": data.get("total_commits_estimate", 0),
        "error": data.get("error")
    }
