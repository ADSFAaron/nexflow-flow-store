# 維護手冊

給商店維護者看的：GitHub 端要做的設定、日常審核，以及要改什麼的時候怎麼改。
設計的來龍去脈在 NexFlow repo 的 [`docs/flow-store/DESIGN.md`](https://github.com/ADSFAaron/NexFlow/blob/master/docs/flow-store/DESIGN.md)。

## 一次性設定

依序做。前面的沒做，後面的 workflow 會失敗。

### 1. Ed25519 簽章金鑰（current 與 next 兩把）

在**自己的電腦**上產生，私鑰不要放進任何 repo 或雲端同步資料夾：

```bash
mkdir -p ~/nexflow-store-keys && cd ~/nexflow-store-keys && umask 077
openssl genpkey -algorithm ed25519 -out current.pem
openssl genpkey -algorithm ed25519 -out next.pem
openssl pkey -in current.pem -pubout -out current.pub
openssl pkey -in next.pem    -pubout -out next.pub
```

- `current.pub`、`next.pub` 複製到本 repo 的 `keys/`，走 PR commit。
- `current.pem`、`next.pem` 做**離線備份**（例如 USB 隨身碟與密碼管理器各一份），之後從電腦刪掉。
- 兩把公鑰之後要內建進 App（P3）。

### 2. `production` Environment（簽章要人工核准）

Settings → Environments → New environment，名稱 `production`：
- **Required reviewers**：自己。不要勾 *Prevent self-review*（只有一位維護者）。
- **Deployment branches and tags**：Selected branches → `master`。
- **Environment secrets**：`FLOW_STORE_SIGNING_KEY` ＝ `current.pem` 的完整內容（含 `-----BEGIN PRIVATE KEY-----` 那兩行）。

### 3. GitHub Pages

Settings → Pages → Source 選 **GitHub Actions**。第一次 publish 後網址是 `https://adsfaaron.github.io/nexflow-flow-store/`。

### 4. 投稿用的私人 GitHub App

GITHUB_TOKEN 開的 PR 不會觸發 validate，所以 issue 投稿要用 App 開 PR。

1. <https://github.com/settings/apps/new>
   - 名稱：例如 `nexflow-flow-store-bot`；Homepage：本 repo 網址
   - **Webhook：取消勾選 Active**
   - Repository permissions：**Contents: Read and write**、**Pull requests: Read and write**，其他全部 No access。
     **絕對不要給 Workflows 或 Administration**：token 外洩時，最多只能開垃圾 PR。
   - Where can this GitHub App be installed：**Only on this account**
2. 建立後：記下 **Client ID**；Generate a private key（會下載 `.pem`）。
3. Install App → Only select repositories → `nexflow-flow-store`。
4. 本 repo 的 Settings → Secrets and variables → Actions：
   - Variables：`FLOW_STORE_APP_CLIENT_ID` ＝ Client ID
   - Secrets：`FLOW_STORE_APP_PRIVATE_KEY` ＝ 剛下載的 `.pem` 內容（存好後把檔案刪掉；要換就重新產生一把）

### 5. （已不需要）暫時的 CLI 來源

P1 合進 NexFlow `master` 之前，曾用 repo 變數 `NEXFLOW_REF` 讓 validate 與 submission 改抓 P1 分支。
P1 已於 NexFlow#40 合併，這個變數已刪除。之後若要讓 CI 暫時改用某個 NexFlow 分支，仍可在
Settings → Secrets and variables → Actions → **Variables 分頁**設定 `NEXFLOW_REF`，用完記得刪。

### 6. master 的 Ruleset

套用下面的 Ruleset（bypass 只有 Repository admin，也就是你本人；Actions 與 App 都不在名單上）。
`validate` 這個 status check 要等 validate 至少在 PR 上跑過一次才選得到，所以**先開第一個 PR、跑完 CI，再設 Ruleset**。

```bash
gh api -X POST repos/ADSFAaron/nexflow-flow-store/rulesets --input - <<'JSON'
{
  "name": "master",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [ { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" } ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": false
    } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [ { "context": "validate", "integration_id": 15368 } ]
    } }
  ]
}
JSON
```

（`actor_id: 5` 是 Repository admin 角色；`integration_id: 15368` 是 GitHub Actions。）

### 7. Project 自動加入

[NexFlow Flow Store](https://github.com/users/ADSFAaron/projects/5) → Workflows → Auto-add to project：
filter 改成 `is:issue label:report,submission,ci-broken`。`ci-broken` 是每週檢查失敗時 workflow 自己開的 issue。

### 8. 帳號

ADSFAaron 帳號開 passkey 或 2FA。**repo 與帳號都永遠不改名**（見 README）。

## 日常

### 審 PR

CI 過了不代表可以合併。每個 PR 要看：
- **標題與描述講的，是不是流程真正做的事。** validate 的留言有 dry run，照著讀一遍。
- **高風險動作（SMS、撥號、HTTP、點擊）有沒有道理。** 網址連去哪裡？傳了什麼？
- **`.github/` 有沒有被改。** fork 來的 PR 會跑它自己版本的 validate.yml，改了它等於改了「CI 通過」的意思。
- 改別人的流程時，留言會 @ 原作者；不必等他回覆。
- 合併方式不限；作者的判定不受影響（見 `.github/scripts/authors.py`）。

合併後 publish 會停在 `production` 等核准，按下去才會簽章上線。

### 檢舉與下架

照 [MODERATION.md](MODERATION.md)。下架＝一個 PR 同時把 slug 加進 `revoked.json`、刪掉 `flows/<slug>/`。

### 換 publish 用的 NexFlow 版本

`.github/nexflow-tools.ref` 放一個完整的 commit SHA。NexFlow 的 catalog 或規則改了、要讓商店跟上時，開 PR 改這個檔。

### 精選與 official

- `featured.json`：列在最前面的 slug，依序。
- `maintainers.json`：這些帳號的流程會標 official。

### 金鑰外洩或輪替

照 [SECURITY.md](SECURITY.md)。
