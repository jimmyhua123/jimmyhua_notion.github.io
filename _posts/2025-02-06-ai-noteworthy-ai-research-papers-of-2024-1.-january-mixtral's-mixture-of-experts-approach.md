---
layout: post
title: "1. January Mixtral's Mixture of Experts Approach"
date: 2025-02-06 10:00:00 +0800
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
  ![image](/assets/images/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466UNULVVP4%2F20250206%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250206T073950Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjED8aCXVzLXdlc3QtMiJIMEYCIQCrELtX%2FhMJY0Qxn%2FGr3nG5%2FWq42Hjzldlz7tun5Ef5VwIhAPB7UtJIYbPiT%2Bu0FoVnYpkCcgGTAnj5Sd6HIIgAD3RDKv8DCFgQABoMNjM3NDIzMTgzODA1IgwkadbHaZRX3tePbYoq3AOgJqafQOk0HPI6WspExbeKiRnRPzycXP3ctT%2Fd%2B7WJhuA9pYjb2XaKiBB8sVMjjTAaYCfKXle5LZfrSxEGDOVgiU6Wq2IsN%2FRZwV69b79%2FQlLFrL3%2FEmLjbdcxLGyYcSMEYXi3ntq4mwwYy5rFrb7RraBLM76diThyEVgvIF58vjJRNtFY%2B5is%2Fr%2BSQBAthQHm85qTlFvBc3%2BJ%2FW%2B6%2FjrfQYLwJ%2B6J5jWJuBQFSTFfuMXVmhTO0NCWTPNclLYwyRNkjD9r9rrqVx7ryaYve0JkLNo95g7XhFy%2Ba%2FCa2iBfTnisZiRlrChCESNxSYOhRr7qa%2FbVAU7by0dp79BN3YNoz6qcWohTmuGcUyoVUsFJO6G25wTNiHBIlTXfcis67NKMTTmlR%2Bjb%2BWKXXLvfOaThfOlrQYjo5uCmhqlXPmeGGwP6XU7ANe7yaA1hmiZLzB41SsVkHVbm2aBrfd%2B6K5jU7CVRCuM%2FnwxXfxaSha%2FURGutYd%2BOawGpEV07bnqmj3hBuBh1DwmBZEaCD0w%2BZeKfD3KzDHIHhP5iZLW6LcNpAMZo%2FFX6Xesw60EN26NFh%2BmtrTDDqNdCO1hwKDc7DyrLAzcahFc70QAbn7PIRq3lArF9JUzpZd5DrlFn0jCLtpG9BjqkAZMicWB5eYLHJpirJjB4Hb0a%2FfpnvYK2ElcxB9KmHhYDgfgeDGiGLQNORaOkYXGo9m4ysScpEFQjS50XVmOU6zanq4hVD0Ekh5MSIgqtrEd4%2Ba7%2F1vZ2GHPSP880dx59pxhzXXNWeHS3KNh%2FWHaBErVdKSYnHRF3JwFkK8NKGG4B%2FYsriH7grmYkDjnVtHXhQonnilFjD53ZsRuEKa%2FyO9ylDtcV&X-Amz-Signature=cfe5a1435996a76ffd3e3cc802e09df589dfdb0cc95bfe940f07fac2a3b869a5&X-Amz-SignedHeaders=host&x-id=GetObject)




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

Mixtral 透過稀疏激活 + 高效路由機制，在計算資源有限的情況下，提供與 Llama 2 70B、GPT-3.5 相當的效能，為 MoE 架構帶來 新突破！ 🚀

---
