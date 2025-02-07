---
layout: post
title: "1. January Mixtral's Mixture of Experts Approach"
date: 2025-02-07 10:00:00 +0800
categories: ['NotionExport']
math: true
---

# Mixtral 8x7B（SMoE）與 MoE 架構比較

📌 文章來源：[arXiv: 2401.04088](https://arxiv.org/abs/2401.04088)

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
  


![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/1c9ce5ad-ec87-4678-b178-dd3f83e53f2e/b403f33c-4469-47c8-a73e-0c74e89eb730/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466Z7U5PMJ3%2F20250207%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250207T020538Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFAaCXVzLXdlc3QtMiJHMEUCIDxUpRm8Xt7t6onQf8nEv0jYwQGUnGdZPDEjW03j6SgLAiEAgno9xUkUXbw8CNHwS5dy%2FYg4%2F0xENHDLy7kWmLT0ueYq%2FwMIaRAAGgw2Mzc0MjMxODM4MDUiDB5y61GFTAbGH%2Ft9dircA9eeXVrYlLMA9fmFcs8qR58y9op4WgrFNNlW38X0TG2oBbuRQrEVUbOgCU%2FKFTjoOLFnSOCzdqH%2FieAhWdckPG6EMBxJkOWLejx4uUe9sdhFqXS1yi1%2FgQa4As%2B1iasNqN5kwhgoBme%2FHxP1uAyQHdot4DpXFStzDMnbyw9vgTq%2FKx0SfrBApkV%2Bb3MhZkr7xti7V%2FDzCkMPVZpcUJ%2F%2FJOXq9FTzaZQGVjOGZH5oIkjgDCmHrDwaYp0vjF7f31dcnuwAlVWzLUQXk2mBhVGXmTf%2B%2BIUxRI1mC8tBAwHDZ4DqGfDnfgBZsj22qQRDwaAlai15L4yzZi%2B6JovfvaYSaB5FdHAniZrVvrGYmcBmyuhMz3MTwpI0JRwbnC6%2BuoPzCkv9UPLwzSPO4viEezApWCCq54Q2%2FTQuqqb%2FK1u4Ag9jP9nppxrhzAlthSDwfTa0vXrOAXZNJWquPeZgX10xcehTAadmUz0%2FoOVBieVdD1frPkMhMp0vPRfnCskDJRs%2B9hZpvmNBG2KsiM5HJIMD0ewIilzZ1%2BW%2FFiXn0x%2BiF6bOhSqKK%2BlhlnzElIQW1bjZ30gvE08Cn2UVOqrbB9mzXp9XAHpnQs%2F7BCZDgL9DiwuYQVsSRPyu7BQA%2FLtoMIyalb0GOqUBxKPbWpWsoWK0%2Bt%2FwuEEuSuV%2B64tsuK6tC603RRet6bkwQuDzTqbvBzOXiXXo2KjLpvwOx0cJO5PWH5pQUtJLY8nvaJtpyKEXvTXqXfZNjt8dUNmK%2FnLvunJfB5%2FouI2IjFGlM9zHSJsLLCD0kSeRRfNdaE6XZZ3UDiLE9P%2Bkfn2On8Jj1LWFqiaAkWbk6ebAEpfV8MUVG1lMUmfKPMP9ke8BoDnB&X-Amz-Signature=29d19ab93557ebc420e29bcff91c891c11c2e8ca85fcf1b1d82294dc9f39df2c&X-Amz-SignedHeaders=host&x-id=GetObject)

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

---

## 🔹 4. 相似點與差異

### ✅ 相似點

- 🔀 動態路由機制：根據輸入數據選擇專家，提高計算效率。
- 🧩 集成學習（Ensemble Learning）：各專家獨立處理數據，最終融合預測結果。
- ⚡️ 計算資源最佳化：稀疏激活 減少資源浪費，適用於超大規模模型。
### 🔥 主要差異

---

## 🔹 5. 結論

✅ Mixtral 8x7B 採用 固定 8 專家，每 token 僅與 2 專家互動，有效降低計算成本。

✅ MoE 架構更靈活，允許不同專家數量與門控機制，應用範圍更廣。

✅ Mixtral MoE 是經過優化的 SMoE 架構，特別適用於 LLM 訓練與推理，而 傳統 MoE 適用於更多 AI 領域。

---
