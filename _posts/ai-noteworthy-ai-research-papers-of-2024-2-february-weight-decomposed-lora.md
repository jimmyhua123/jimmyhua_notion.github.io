---
layout: post
title: "2. February: Weight-decomposed LoRA"
categories: ['NotionExport']
math: true
date: 2025-02-12 10:00:00 +0800
---

# 📚 參考文獻

1. DoRA: [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353)
1. LoRA: [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
1. LoRA Survey: [A Survey on LoRA of Large Language Models](https://arxiv.org/abs/2106.09685)
1. 內文中的圖片連結 : [https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1](https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1)
---



## 1.1 數學解釋 🔢

1. 假設預訓練權重矩陣為 $$W_0$$，微調時，權重變為：
$$
\mathbf{W} = \mathbf{W}_0 + \Delta \mathbf{W}
$$

1. LoRA 假設 權重更新 $$\Delta W$$ 可用兩個低秩矩陣的乘積來近似：
其中：
$$
\Delta\mathbf{W}\approx\mathbf{BA}
$$

- $$\mathbf{B} \in \mathbb{R}^{d \times r}$$  $$\mathbf{A} \in \mathbb{R}^{r \times k}$$
- $$r \ll \min(d,k)$$  （秩 $$r$$ 遠小於原始矩陣維度）
1. 在 LoRA 設定下，僅需訓練這兩個小矩陣 $$\mathbf{A}, \mathbf{B}$$，即可在新任務上微調模型，顯著減少參數更新量。


![image]({{ site.baseurl }}/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)

> 小結：LoRA 只調整小規模的低秩矩陣，保留了原始模型的能力，同時讓微調變得更輕量。



---



## 1.2 LoRA 的運作流程 ⚙️

### 1️⃣ 初始化

- 在模型的每個需要適應的權重矩陣 $$W$$ 旁，引入兩個額外的低秩矩陣 $$B$$ 和 $$A$$。
- $$A$$ 通常使用均勻的 Kaiming 分佈 初始化，而 $$B$$ 則初始化為零，確保在訓練開始時 $$\Delta W = BA = 0$$。


### 2️⃣ 前向傳遞

- 當輸入通過模型層時，原始權重 $$W$$ 和低秩更新 $$BA$$ 的輸出會相加：$$$\text{output} = (\mathbf{W} + \mathbf{BA})\mathbf{x}$$$ 其中 $$x$$ 是輸入向量。
  




### 3️⃣ 反向傳遞

- 在反向傳遞過程中，只有 $$B$$ 和 $$A$$ 的參數會被更新，而原始的權重 $$W$$ 保持凍結。


### 4️⃣ 調整秩 $$r$$

- $$r$$ 代表低秩矩陣 $$B$$ 和 $$A$$ 的秩，它控制了模型在微調過程中可以調整的參數數量。
- 較小的 $$r$$ 值 → 更少的參數需要訓練，減少計算和記憶體需求。
- 適當調整 $$r$$ 值 → 在 訓練參數數量 與 模型效能 之間取得平衡。




---



## 1.3 LoRA 的效率與影響 🚀

### ✅ 參數效率

- 直接用 Adam 微調 GPT-3（175B 參數），參數量龐大。
- LoRA 可將可訓練參數數量減少約 10,000 倍，並降低 3 倍 GPU 記憶體需求。


### 🎯 秩（r）的影響

- 小 r（如 r = 4）：能放大 預訓練模型未強調，但對特定任務重要的特徵方向。
- 大 r：可能包含預訓練時已強調的方向，對新任務增益有限。


### 🔄 可插拔性

- LoRA 參數可獨立保存，並隨時掛載到原模型上，方便共享或跨任務切換。
- 可將多個任務的 LoRA 模組疊加，實現跨任務泛化。


### ⏩ 訓練與推論效率

- 更高訓練吞吐量：因為更新參數少，微調速度更快。
- 不增加推理延遲：LoRA 更新矩陣形狀與原模型一致，推理時無需額外計算。


---



## 1.4 LoRA 的優勢總結 ✅

| 優勢 | 描述 |
| --- | --- |
| 參數效率 | 可訓練參數減少 10,000 倍，降低 GPU 記憶體需求。 |
| 計算效率 | 只更新低秩矩陣，提高微調速度。 |
| 零額外推理延遲 | 微調後的推理開銷與原模型相同。 |
| 可插拔性 | 可以輕鬆切換 LoRA 模組，支持多任務。 |
| 易於實作 | 目前已有許多開源庫支援，開發門檻低。 |



---



# 2️⃣ DoRA：Weight-Decomposed LoRA

現在來介紹 DoRA（Weight-Decomposed Low-Rank Adaptation），它基於 LoRA，但在 權重拆解方式 上更進一步。

## 2.1 DoRA 的基本概念

- 權重分解（Weight Decomposition）：將預訓練權重矩陣拆成 「量值（Magnitude）」與「方向（Direction）」 兩部分。
  - 量值 m：權重向量的長度或強度。

  - 方向 V：權重向量的指向。

- 量值 m：權重向量的長度或強度。
- 方向 V：權重向量的指向。
> 與 LoRA 的差異：

- LoRA 直接對 $$\Delta\mathbf{W}$$ 進行低秩近似。
- DoRA 先將權重 $$\mathbf{W}$$ 分解為 $$(m, \mathbf{V})$$，再針對「方向」V 進行低秩更新，同時允許「量值」m 調整。


---



# 2.2 DoRA 的運作機制 ⚙️

### 1️⃣ 權重分解（Decompose）

$$

\mathbf{W} = \mathbf{m} \times \mathbf{V}

$$

- $$m$$（量值，Magnitude）：控制權重的大小
- $$V$$（方向，Direction）：決定權重的方向


### 2️⃣ 方向更新（Direction Update）

$$

\Delta \mathbf{V} = \mathbf{A} \times \mathbf{B}

$$

- 僅更新方向矩陣 $$V$$，採用 LoRA 風格的低秩更新
- 這種方法能 有效降低參數更新量，提升訓練效率 📉


### 3️⃣ 量值更新（Magnitude Update）

- 量值向量 $$m$$ 也可以更新，但不同於 $$V$$，它不使用低秩分解，而是獨立調整。
- 這樣的設計允許更靈活地適應不同的模型需求。


### 4️⃣ 權重合併（Merge）🚀（推理時）

$$

\mathbf{W}' = (\mathbf{m} + \Delta \mathbf{m}) \times (\mathbf{V} + \Delta \mathbf{V})

$$

- 最終部署時，會將 $$m$$ 和 $$V$$ 的更新結果合併回原始權重：
✅ 優勢：

- 不額外增加推理時的計算成本 🎯
- 只需在 訓練後合併權重，無需修改推理過程。


### 5️⃣ 視覺化圖解 📊

![image]({{ site.baseurl }}/images/197fbb85-7f9e-8054-8cd4-d99988309113.png)

![image]({{ site.baseurl }}/images/197fbb85-7f9e-800c-ab1e-f50b49b78a63.png)





---



# 3️⃣ 小結 📝

- LoRA（Low-Rank Adaptation）：主要應用於 Transformer 架構的線性層（dense layers），尤其是 self-attention 模組中的權重矩陣。它通過對 權重更新 $$\Delta\mathbf{W}$$ 進行低秩近似，實現高效微調。
- DoRA（Decomposed Rank Adaptation）：進一步將權重拆解為 (magnitude, direction)，並 僅對方向進行低秩更新，從而提升效能與靈活性。
- 核心機制對比：
  - LoRA：透過 $$W \approx W_0 + BA$$ 進行微調，並調整 秩 $$r$$，但並非單純地調整 $$r$$，而是更新兩個低秩矩陣 $$B$$ 和 $$A$$，以實現參數高效微調。

  - DoRA：先將權重拆解為 $$W \approx m \cdot v$$（幅度 $$m$$ 和方向 $$v$$），再僅微調 $$m$$，並對 $$v$$ 應用 LoRA（即 $$v \rightarrow BA$$），最後合併兩者。

- LoRA：透過 $$W \approx W_0 + BA$$ 進行微調，並調整 秩 $$r$$，但並非單純地調整 $$r$$，而是更新兩個低秩矩陣 $$B$$ 和 $$A$$，以實現參數高效微調。
- DoRA：先將權重拆解為 $$W \approx m \cdot v$$（幅度 $$m$$ 和方向 $$v$$），再僅微調 $$m$$，並對 $$v$$ 應用 LoRA（即 $$v \rightarrow BA$$），最後合併兩者。
- 結論：LoRA 和 DoRA 雖然都基於低秩近似來減少參數更新，但 DoRA 進一步優化了權重更新方式，使微調更加靈活且高效！ 🚀
