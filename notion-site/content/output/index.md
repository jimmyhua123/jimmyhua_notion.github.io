---
title: "Scalable Softmax"
date: 2025-02-05T12:00:00+00:00
draft: false
---

## 子頁面: [Scalable-Softmax (SSMax) - 新型 Softmax 替代方案](https://www.notion.so/190fbb857f9e809a90c6ec413212232c)

📌 文章來源：arXiv:2501.19399v1

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

🔗 論文原文: arXiv 2501.19399v1

---



## 子頁面: [Noteworthy AI Research Papers of 2024](https://www.notion.so/190fbb857f9e80e492facf4214b7b88d)

https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1

https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-2

## 子頁面: [1. January Mixtral's Mixture of Experts Approach](https://www.notion.so/190fbb857f9e80f8a70ad27f12c11b42)

https://arxiv.org/abs/2401.04088



## 子頁面: [2. February: Weight-decomposed LoRA](https://www.notion.so/190fbb857f9e807caa22cf8b5f547163)

https://arxiv.org/abs/2402.09353

## 子頁面: [3. March: Tips for Continually Pretraining LLMs](https://www.notion.so/190fbb857f9e80e8b349d82766b46bac)

https://arxiv.org/abs/2403.08763

## 子頁面: [4. April: DPO or PPO for LLM alignment, or both?](https://www.notion.so/190fbb857f9e80e08e08f55749e05578)

https://arxiv.org/abs/2404.10719

## 子頁面: [5. May: LoRA learns less and forgets less](https://www.notion.so/190fbb857f9e80468f0ce781e0927509)

https://arxiv.org/abs/2405.09673



## 子頁面: [6. June: The 15 Trillion Token FineWeb Dataset](https://www.notion.so/190fbb857f9e80438a28e4063229a212)

https://arxiv.org/abs/2406.17557

## 子頁面: [7. July: The Llama 3 Herd of Models](https://www.notion.so/190fbb857f9e80eda325cb0bf08ba0dc)

https://arxiv.org/abs/2407.21783

## 子頁面: [8. August: Improving LLMs by scaling inference-time compute](https://www.notion.so/190fbb857f9e807c9f7ed21df5dfde75)

https://arxiv.org/abs/2408.03314

## 子頁面: [9. September: Comparing multimodal LLM paradigms](https://www.notion.so/190fbb857f9e80a3a7d2ed523f68f692)

https://arxiv.org/abs/2409.11402

## 子頁面: [10. October: Replicating OpenAI o1's reasoning capabilities](https://www.notion.so/190fbb857f9e80d7adc9dff32fa0c986)

https://arxiv.org/abs/2410.18982

## 子頁面: [11. November: LLM scaling laws for precision](https://www.notion.so/190fbb857f9e8091af2df543c4fb4f93)

https://arxiv.org/abs/2411.04330

## 子頁面: [12. December: Phi-4 and Learning from Synthetic Data](https://www.notion.so/190fbb857f9e801fb030c8ea060b6d65)

https://arxiv.org/abs/2412.08905



