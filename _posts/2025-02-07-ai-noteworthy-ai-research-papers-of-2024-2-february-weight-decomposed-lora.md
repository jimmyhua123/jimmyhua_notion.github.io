---
layout: post
title: "2. February: Weight-decomposed LoRA"
date: 2025-02-07 10:00:00 +0800
categories: ['NotionExport']
math: true
---

# 參考文獻 📚

1. DoRA: [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353)
1. LoRA: [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
1. LoRA Survey: [A Survey on LoRA of Large Language Models](https://arxiv.org/abs/2106.09685)
---

# 1️⃣ 什麼是 LoRA？

在介紹 DoRA 之前，先簡要回顧 LoRA（Low-Rank Adaptation） 的基礎概念。

## 1.1 背景與核心假設

- 低「內在維度」（Intrinsic Dimension）
  - Aghajanyan 等人指出，預訓練的語言模型內在維度極低，即便將模型參數投影到更小的空間，也能有效學習，顯示出模型參數的冗餘性。

- Aghajanyan 等人指出，預訓練的語言模型內在維度極低，即便將模型參數投影到更小的空間，也能有效學習，顯示出模型參數的冗餘性。
- LoRA 的核心假設
  - 微調時，權重的更新可以用低秩矩陣（Low-Rank Matrix）來近似，從而減少參數更新量，提高計算效率。

- 微調時，權重的更新可以用低秩矩陣（Low-Rank Matrix）來近似，從而減少參數更新量，提高計算效率。
## 1.2 數學解釋 🔢

1. 假設預訓練權重矩陣為 W0W_0，微調時，權重變為：
  W=W0+ΔWW = W_0 + \Delta W


W=W0+ΔWW = W_0 + \Delta W

1. LoRA 假設 權重更新 ΔW\Delta W 可用兩個低秩矩陣的乘積來近似：

其中：
  ΔW≈BA\Delta W \approx B A


  - B∈Rd×rB \in \mathbb{R}^{d \times r}

  - A∈Rr×kA \in \mathbb{R}^{r \times k}

  - r≪min⁡(d,k)r \ll \min(d, k)（秩  遠小於原始矩陣維度）
  rr


  ![image](/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)



  rr


  ![image](/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)


ΔW≈BA\Delta W \approx B A

- B∈Rd×rB \in \mathbb{R}^{d \times r}
- A∈Rr×kA \in \mathbb{R}^{r \times k}
- r≪min⁡(d,k)r \ll \min(d, k)（秩  遠小於原始矩陣維度）
  rr


  ![image](/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)


rr

![image](/images/196fbb85-7f9e-8050-9627-c85ad4b2fbdb.png)

1. 在 LoRA 設定下，僅需訓練這兩個小矩陣 A,BA, B，即可在新任務上微調模型，顯著減少參數更新量。
> 小結：LoRA 只調整小規模的低秩矩陣，保留了原始模型的能力，同時讓微調變得更輕量。

---

## 1.3 LoRA 的效率與影響 🚀

### ✅ 參數效率

- 直接用 Adam 微調 GPT-3（175B 參數），參數量龐大。
- LoRA 可將可訓練參數數量減少約 10,000 倍，並降低 3 倍 GPU 記憶體需求。
### 🎯 秩（r）的影響

- 小 rr（如 ）：能放大 預訓練模型未強調，但對特定任務重要的特徵方向。
  r=4r=4


r=4r=4

- 大 rr：可能包含預訓練時已強調的方向，對新任務增益有限。
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
  - 量值 mm：權重向量的長度或強度。

  - 方向 VV：權重向量的指向。

- 量值 mm：權重向量的長度或強度。
- 方向 VV：權重向量的指向。
> 與 LoRA 的差異：

- LoRA 直接對 ΔW\Delta W 進行低秩近似。
- DoRA 先將權重 WW 分解為 (m,V)(m, V)，再針對「方向」VV 進行低秩更新，同時允許「量值」 調整。
  mm


mm

---

## 2.2 DoRA 的運作機制 ⚙️

1. 權重分解（Decompose）
  W=m×VW = m \times V


  - mm：代表「量值」

  - VV：代表「方向」

W=m×VW = m \times V

- mm：代表「量值」
- VV：代表「方向」
1. 方向更新（Direction Update）
  - 只對 方向矩陣 VV 進行 LoRA 風格的低秩更新：
  ΔV=A×B\Delta V = A \times B



  ΔV=A×B\Delta V = A \times B


- 只對 方向矩陣 VV 進行 LoRA 風格的低秩更新：
  ΔV=A×B\Delta V = A \times B


ΔV=A×B\Delta V = A \times B

1. 量值更新（Magnitude Update）
  - 量值向量  也可更新，但不像方向那樣使用低秩矩陣，而是獨立調整。
  mm



  mm


- 量值向量  也可更新，但不像方向那樣使用低秩矩陣，而是獨立調整。
  mm


mm

1. 權重合併（Merge）（推理時）
  - 部署時，將更新後的  和  合併回原始權重：
  mm


  VV


  W′=(m+Δm)×(V+ΔV)W' = (m + \Delta m) \times (V + \Delta V)



  mm


  VV


  W′=(m+Δm)×(V+ΔV)W' = (m + \Delta m) \times (V + \Delta V)


  - 不額外增加推理計算成本。

- 部署時，將更新後的  和  合併回原始權重：
  mm


  VV


  W′=(m+Δm)×(V+ΔV)W' = (m + \Delta m) \times (V + \Delta V)


mm

VV

W′=(m+Δm)×(V+ΔV)W' = (m + \Delta m) \times (V + \Delta V)

- 不額外增加推理計算成本。
---

## 2.3 DoRA 的優勢 🔥

### ✅ 更高靈活性

- LoRA 均勻調整量值與方向，但 DoRA 可獨立控制方向與量值，調整更精細。
### 📈 更高效能

- 在 LLaMA-7B 上，DoRA 比 LoRA 準確度高 3.7%，甚至超越 ChatGPT。
- 在 LLaMA2-7B、LLaMA3-8B 亦明顯優於 LoRA。
- 視覺語言任務中，DoRA 比 LoRA 高 1%～2%。
### 🔍 更低秩敏感度

- 不同秩（r）設定下，DoRA 表現更穩定，對  的敏感度較低。
  rr


rr

### ⏳ 訓練穩定性更好

- 收斂更快，更穩定。
### ⏩ 不增加推理延遲

- 與 LoRA 相同，推理時不需額外計算。
### 🔗 兼容性

- 可與 QLoRA 結合形成 QDoRA，同時兼顧低 GPU 記憶體需求與高效能。
---

# 3️⃣ 小結

- LoRA：針對權重更新  進行低秩近似，實現高效微調。
  ΔW\Delta W


ΔW\Delta W

- DoRA：進一步拆解權重為 (magnitude, direction)，並 只對方向進行低秩更新，帶來更好的效能與靈活性。
