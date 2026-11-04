import requests
from config import Config

headers = {
    'Authorization': f'Bearer {Config.GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# 1. Fetch user accessible repos
page = 1
all_repos = []
while True:
    resp = requests.get(f'https://api.github.com/user/repos?per_page=100&page={page}', headers=headers)
    if resp.status_code != 200:
        break
    data = resp.json()
    if not data:
        break
    all_repos.extend(data)
    page += 1

print('Total user accessible repos across all owners:', len(all_repos))
andalusia_repos = [r for r in all_repos if r.get('owner', {}).get('login') == 'Andalusia-Data-Science-Team']
print('Total Andalusia-Data-Science-Team repos visible to this token:', len(andalusia_repos))

# 2. Query org repos directly with type=all
resp_org = requests.get('https://api.github.com/orgs/Andalusia-Data-Science-Team/repos?per_page=100&type=all', headers=headers)
print('Direct Org query status:', resp_org.status_code)
if resp_org.status_code == 200:
    print('Direct Org repos on page 1:', len(resp_org.json()))
    for r in resp_org.json():
        print(f"  {r['name']} (Private: {r['private']}) - {r.get('description') or 'No description'}")

