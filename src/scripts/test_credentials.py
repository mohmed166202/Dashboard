"""
Quick utility to test GitHub authentication and token scopes.
"""

import sys
from config import Config
from github_client import GitHubClient


def main():
    print("=" * 60)
    print("GitHub Credentials & Connectivity Check")
    print("=" * 60)
    
    summary = Config.get_summary()
    print(f"Token Configured: {summary['github_token']}")
    print(f"Target Type:      {summary['target_type']}")
    print(f"Target Owner:     {summary['target_owner']}")
    print(f"Database Target:  {summary['database_path']}")
    print("-" * 60)

    if not Config.validate_github_creds():
        print("\n[!] GITHUB_PERSONAL_ACCESS_TOKEN is missing or still set to the default placeholder.")
        print("Please edit your '.env' file in this folder and add your Personal Access Token:")
        print("   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_actual_token")
        sys.exit(1)

    print("Contacting GitHub API...")
    try:
        client = GitHubClient()
        auth = client.check_auth()
        print("\n[SUCCESS] Authentication Succeeded!")
        print(f"  User / Account:   {auth['login']} ({auth.get('name') or 'No name provided'})")
        print(f"  Account Email:    {auth.get('email') or 'Private'}")
        print(f"  Public Repos:     {auth.get('public_repos')}")
        print(f"  Private Repos:    {auth.get('total_private_repos')}")
        print(f"  Token Scopes:     {', '.join(auth['scopes']) if auth['scopes'] else 'None (default public read)'}")
        print(f"  API Rate Limit:   {auth['rate_remaining']} remaining (out of {auth['rate_limit']})")
        print("\nYou are ready to run Phase 1 Discovery: python run_phase1.py")
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

