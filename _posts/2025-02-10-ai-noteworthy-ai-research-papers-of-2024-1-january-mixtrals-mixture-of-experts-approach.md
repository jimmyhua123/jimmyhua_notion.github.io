---
layout: post
title: "1. January Mixtral's Mixture of Experts Approach"
categories: ['NotionExport']
math: true
date: 2025-02-13 10:00:00 +0800
---

# Mixtral 8x7B（SMoE）與 MoE 架構比較

📌 文章來源：[arXiv: 2401.04088](https://arxiv.org/abs/2401.04088)

📌內文中的圖片連結 : [https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1](https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1)

🔹 1. Mixtral 8x7B 簡介

Mixtral 8x7B 是一種 稀疏混合專家模型（Sparse Mixture of Experts, SMoE），具備 高效能與計算資源優化 的特性。

### 🔍 核心特點

- 🛠 架構
  - 每層 8 個專家（Experts）。

  - 每個 token 僅選 2 個專家 進行計算（透過 路由網絡（Router Network） 決定）。

- 📊 參數效率
  - 總參數量：470 億（47B）。

  - 推論時僅使用 130 億活動參數（13B），顯著降低計算成本。

- 🏆 性能表現
  - 超越或匹配 Llama 2 70B 和 GPT-3.5。

  - 在 數學、程式碼生成、多語言處理 方面表現卓越。

- 🌍 多語言能力
  - 在 法語、德語、西班牙語、義大利語 等基準測試中，顯著優於 Llama 2 70B。

- 🧠 長程效能
  - 支援 32k tokens 上下文視窗。

  - Passkey 檢索任務達到 100% 準確度。

- 📌 指令微調（Instruction-Tuned Model）
  - Mixtral 8x7B – Instruct 在人類評估基準中：
  - 超越 GPT-3.5 Turbo、Claude-2.1、Gemini Pro、Llama 2 70B-chat。


- 📜 開源
  - Apache 2.0 許可，可供 學術與商業用途。

- ⚖️ 模型偏差
  - 相較於 Llama 2 70B，Mixtral 在：
  - BBQ 基準測試中展現較少偏差。

  - BOLD 基準測試中顯示更正向的情感傾向。


- 🛠以下是架構
  


![image]({{ site.baseurl }}/images/192fbb85-7f9e-8029-8e3e-f7eb3b482ac6.png)

---

## 🔹 2. Mixture of Experts（MoE）架構概述

MoE 架構是 高度可擴展的神經網路，特別適用於 大型語言模型（LLM） 及其他複雜 AI 任務。透過 動態選擇少數專家，MoE 提供 計算效率與可擴展性。

### 🧩 核心組成

1. 👨‍🏫 專家（Experts）
  - 獨立的神經網路或子模型，負責特定類型的輸入數據。

1. 📡 路由網絡（Gating Network）
  - 使用 前饋神經網路（Feedforward NN） 計算 專家權重，動態選擇適合的專家。

1. ⚡️ 稀疏激活（Sparse Activation）
  - 每次僅激活少數專家，降低計算成本，提高效率。

### ⚙️ 運作方式

1. 📥 輸入處理
  - 路由網絡計算 每個專家的相關性分數。

1. 🎯 選擇專家
  - 根據分數選擇 前 k 個最相關的專家（通常 k=2 或 3）。

  - 僅選中的專家會被激活 參與當前輸入的計算。

1. 📊 加權輸出
  - 各專家獨立處理數據，最後 加權融合結果。

---

## 🔹 3. Mixtral SMoE vs. MoE 比較

| 特徵 | Mixtral 8x7B（SMoE） | MoE 架構 |
| --- | --- | --- |
| 專家結構 | 每層 8 個專家，每 token 選 2 個。 | 可彈性調整專家數量。 |
| 路由機制 | Router Network 負責專家選擇。 | 使用 Gating Network 或更複雜機制。 |
| 應用場景 | LLM、程式碼生成、多語言處理、數學計算。 | NLP、語音識別、圖像分類等。 |
| 訓練策略 | SFT + DPO 微調，前饋層獨立，其他參數共享。 | 從零開始訓練或遷移學習（Transfer Learning）。 |
| 計算效率 | 稀疏激活，每次推論 13B 參數。 | 可依選擇策略調整計算資源。 |

---

## 🔹 4. 相似點與差異

### ✅ 相似點

- 🔀 動態路由機制：根據輸入數據選擇專家，提高計算效率。
- 🧩 集成學習（Ensemble Learning）：各專家獨立處理數據，最終融合預測結果。
- ⚡️ 計算資源最佳化：稀疏激活 減少資源浪費，適用於超大規模模型。
### 🔥 主要差異

| 區別 | Mixtral 8x7B（SMoE） | MoE |
| --- | --- | --- |
| 專家數量與結構 | 固定 8 個專家，每層選 2 個。 | 彈性專家數量，可依任務調整。 |
| 路由機制 | 輕量級 Router Network，確保高效能。 | 可結合 深度強化學習（Deep RL） 優化選擇。 |
| 應用範圍 | 主要用於 LLM、數學、程式碼生成、多語言處理。 | 更廣泛適用於 NLP、語音識別、圖像處理等。 |

---

## 🔹 5. 結論

✅ Mixtral 8x7B 採用 固定 8 專家，每 token 僅與 2 專家互動，有效降低計算成本。

✅ MoE 架構更靈活，允許不同專家數量與門控機制，應用範圍更廣。

✅ Mixtral MoE 是經過優化的 SMoE 架構，特別適用於 LLM 訓練與推理，而 傳統 MoE 適用於更多 AI 領域。

---
