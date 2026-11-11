# NexFlow 流程商店

[English](README.md)

[NexFlow](https://github.com/ADSFAaron/NexFlow) 使用者分享的現成自動化流程。

> **狀態：** 建置中。App 內的商店會在之後的 NexFlow 版本推出，在那之前可以先在這裡看流程。

- **瀏覽：** <https://adsfaaron.github.io/nexflow-flow-store/>。每個流程都有一頁說明：它做什麼、安裝時要你填什麼，以及用到哪些高風險動作（傳簡訊、打電話、連網等）。
- **安裝：** 在 App 裡安裝。商店的流程裝好時是關閉的；個人資訊（Wi-Fi 名稱、電話號碼、要開哪個 App）一律在安裝時由你填，不會放在流程裡。
- **投稿：** 見 [CONTRIBUTING.md](CONTRIBUTING.md)（英文）。可以自己開 pull request，也可以填 issue 表單，由機器人替你開。
- **檢舉流程：** [填寫檢舉表單](https://github.com/ADSFAaron/nexflow-flow-store/issues/new?template=report-flow.yml)。處理方式見 [MODERATION.md](MODERATION.md)。
- **商店本身的資安問題：** 見 [SECURITY.md](SECURITY.md)。

## 流程上架的經過

1. 有人提出（pull request 或 issue 表單）。
2. 自動檢查用 NexFlow 自己的驗證器檢查：每個步驟與設定都必須是 App 有的；個人資訊必須留給安裝的人填；陌生人能控制的資料（簡訊內容、網路回應）不能流進會傳送或開啟東西的欄位；網址必須是固定的 `https` 主機；還有其他規則。
3. 維護者審核後合併。
4. 商店重新產生並簽章。App 安裝前會驗證簽章與每個流程的 checksum。

## ⚠️ 請勿更改此 repo 名稱

App 從 `https://adsfaaron.github.io/nexflow-flow-store/` 下載商店，這個網址寫死在所有已發佈的版本裡。更改這個 repo 或 `ADSFAaron` 帳號的名稱，所有已安裝的 App 都會連不上商店（GitHub Pages 不會轉址）。

## 授權

本 repo 的流程以 [CC0 1.0](LICENSE) 釋出到公有領域。
