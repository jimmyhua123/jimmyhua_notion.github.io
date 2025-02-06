---
layout: post
title: "Scalable-Softmax (SSMax) - 新型 Softmax 替代方案"
date: 2025-02-06 10:00:00 +0800
categories: ['NotionExport']
math: true
---

📌 文章來源：[arXiv:2501.19399v1](https://arxiv.org/abs/2501.19399v1)

✍ 摘要整理 by JimmyHua

## 🔹 什麼是 Scalable-Softmax (SSMax)?

SSMax 的設計目標是 避免注意力衰退，並提高長度泛化能力。

它與傳統 Softmax 類似，將輸入向量轉換為機率分佈，但關鍵差異在於其指數的基數取決於輸入向量的大小 (n)。

---

## 🔹 Softmax vs. SSMax

### 🔹 Softmax 公式

$$
z_i = \frac{e^{z_i}}{\sum_{j=1}^n e^{z_j}}
$$

### 🔹 SSMax 公式

$$
z_i \mapsto \frac{n^{sz_i}}{\sum_{j=1}^n n^{sz_j}} = \frac{e^{(s\log n)z_i}}{\sum_{j=1}^n e^{(s\log n)z_j}}
$$

> 主要改進點

---

## 🔹 SSMax 的優勢

### ✅ 解決「注意力衰退」問題

- 傳統 Softmax 在處理長文本時，隨著輸入向量變長，注意力權重會變得扁平，導致關鍵資訊難以捕捉。
- SSMax 透過對數縮放調整，使注意力能夠集中在關鍵元素上，提升模型效能。
### ✅ 提升「長度泛化能力」

- SSMax 即使在訓練時未見過長文本，也能保持良好表現。
- 可擴展至 10 倍以上的序列長度，適用於長篇文章、對話或語音任務。
### ✅ 強化「關鍵資訊檢索」

- 在長上下文內檢索特定資訊時，SSMax 比 Softmax 更容易鎖定目標（例如「大海撈針」測試）。
### ✅ 可無縫整合至 Transformer

- 只需少量修改程式碼，即可將 SSMax 替換為 Softmax，適用於現有的 Transformer 架構。
---

## 🔹 實驗結果分析

### 📊 1️⃣ 學習曲線分析

- 使用 SSMax 訓練的模型，在預訓練期間的損失值明顯低於 Softmax，收斂更穩定。
### 📊 2️⃣ 長文本泛化能力測試

- 方法：將 RoPE (旋轉位置編碼) 的 θ 值增加到訓練時的 50 倍，評估模型在長文本上的表現。
- 結果：
  - SSMax 模型（特別是標準 SSMax 和無縮放參數的版本）在 10 倍訓練序列長度（約 10,000 個 Token）時，仍能維持較低的測試損失值。

### 📊 3️⃣ 「大海撈針」測試（Needle-In-A-Haystack）

- 在極長的文本內，隱藏一段關鍵資訊，測試模型是否能正確檢索。
- SSMax 模型 在 長達 10 倍序列長度的文本內，依然能精準找出關鍵資訊。
---

## 🔹 SSMax 部署建議

### 🚀 1️⃣ 預訓練期間替換 Softmax

- 最佳做法：在預訓練初期就使用 SSMax，效果最佳。
- 適應性：即使 在預訓練後才替換，仍可帶來一定效能提升，但影響較小。
### 🔧 2️⃣ 兼容性與實作

- SSMax 可以 直接取代 Softmax，且對 Transformer 模型幾乎無影響。
- 只需調整 Softmax 計算方式，無需改動架構。
---

## 🔹 結論

✅ SSMax 有效解決 Softmax 在長文本處理時的「注意力衰退」問題

✅ SSMax 提高 Transformer 模型的「長度泛化能力」，適用於長序列任務

✅ SSMax 可無縫整合至現有模型，適用於預訓練與微調階段

✅ SSMax 具備成為 Transformer 標準組件的潛力

---

## 📌 參考連結

🔗 [論文原文: arXiv 2501.19399v1](https://arxiv.org/abs/2501.19399v1)

---
