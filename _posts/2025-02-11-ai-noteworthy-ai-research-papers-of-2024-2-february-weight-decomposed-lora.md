---
layout: post
title: "2. February: Weight-decomposed LoRA"
date: 2025-02-11 10:00:00 +0800
categories: ['NotionExport']
math: true
---

# 📚 參考文獻

1. DoRA: [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353)
1. LoRA: [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
1. LoRA Survey: [A Survey on LoRA of Large Language Models](https://arxiv.org/abs/2106.09685)


1.2 數學解釋 🔢

1. 假設預訓練權重矩陣為 W_0，微調時，權重變為：
\mathbf{W} = \mathbf{W}_0 + \Delta \mathbf{W}

1. LoRA 假設 權重更新 \Delta W 可用兩個低秩矩陣的乘積來近似：
其中：
- \Delta\mathbf{W}\approx\mathbf{BA}
- \mathbf{B} \in \mathbb{R}^{d \times r} 
-  \mathbf{A} \in \mathbb{R}^{r \times k}
- r \ll \min(d,k)  （秩 r 遠小於原始矩陣維度）
1. 在 LoRA 設定下，僅需訓練這兩個小矩陣 \mathbf{A}, \mathbf{B}，即可在新任務上微調模型，顯著減少參數更新量。


![image]({{ site.baseurl }}/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)

> 小結：LoRA 只調整小規模的低秩矩陣，保留了原始模型的能力，同時讓微調變得更輕量。

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
## 1.4 LoRA 的優勢總結 ✅

| 優勢 | 描述 |
| --- | --- |
| 參數效率 | 可訓練參數減少 10,000 倍，降低 GPU 記憶體需求。 |
| 計算效率 | 只更新低秩矩陣，提高微調速度。 |
| 零額外推理延遲 | 微調後的推理開銷與原模型相同。 |
| 可插拔性 | 可以輕鬆切換 LoRA 模組，支持多任務。 |
| 易於實作 | 目前已有許多開源庫支援，開發門檻低。 |

# 2️⃣ DoRA：Weight-Decomposed LoRA

現在來介紹 DoRA（Weight-Decomposed Low-Rank Adaptation），它基於 LoRA，但在 權重拆解方式 上更進一步。

## 2.1 DoRA 的基本概念

- 權重分解（Weight Decomposition）：將預訓練權重矩陣拆成 「量值（Magnitude）」與「方向（Direction）」 兩部分。
  - 量值 m：權重向量的長度或強度。

  - 方向 V：權重向量的指向。

- 量值 m：權重向量的長度或強度。
- 方向 V：權重向量的指向。
> 與 LoRA 的差異：

- LoRA 直接對 \Delta\mathbf{W} 進行低秩近似。
- DoRA 先將權重 \mathbf{W} 分解為 (m, \mathbf{V})，再針對「方向」V 進行低秩更新，同時允許「量值」m 調整。
![image]({{ site.baseurl }}/images/197fbb85-7f9e-8054-8cd4-d99988309113.png)

## 2.2 DoRA 的運作機制 ⚙️

1. 權重分解（Decompose）
  \mathbf{W} = \mathbf{m} \times \mathbf{V}


  - $$ m $$：代表「量值」

  - $$ V $$：代表「方向」

\mathbf{W} = \mathbf{m} \times \mathbf{V}

- $$ m $$：代表「量值」
- $$ V $$：代表「方向」
1. 方向更新（Direction Update）
  - 只對 方向矩陣 V 進行 LoRA 風格的低秩更新：

  \Delta \mathbf{V} = \mathbf{A} \times \mathbf{B}


- 只對 方向矩陣 V 進行 LoRA 風格的低秩更新：
\Delta \mathbf{V} = \mathbf{A} \times \mathbf{B}

1. 量值更新（Magnitude Update）
  - 量值向量 $$ m $$ 也可更新，但不像方向那樣使用低秩矩陣，而是獨立調整。

- 量值向量 $$ m $$ 也可更新，但不像方向那樣使用低秩矩陣，而是獨立調整。
1. 權重合併（Merge）（推理時）
  - 部署時，將更新後的 $$ m $$ 和 $$ V $$ 合併回原始權重：

  \mathbf{W}' = (\mathbf{m} + \Delta \mathbf{m}) \times (\mathbf{V} + \Delta \mathbf{V})


  - 不額外增加推理計算成本。

- 部署時，將更新後的 $$ m $$ 和 $$ V $$ 合併回原始權重：
\mathbf{W}' = (\mathbf{m} + \Delta \mathbf{m}) \times (\mathbf{V} + \Delta \mathbf{V})

- 不額外增加推理計算成本。
# 3️⃣ 小結

- LoRA：針對權重更新 $$ \Delta\mathbf{W} $$ 進行低秩近似，實現高效微調。
- DoRA：進一步拆解權重為 (magnitude, direction)，並 只對方向進行低秩更新，帶來更好的效能與靈活性。
