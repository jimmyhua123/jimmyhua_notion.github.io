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


  ![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/1c9ce5ad-ec87-4678-b178-dd3f83e53f2e/c01e2d9f-cff0-42fa-bc55-dac5b03b364a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466W2PB7YMI%2F20250210%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250210T083819Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIHpA%2FMgRfXZif0h6txtZKsDKOu0GvfysR5gguSrml%2BiAAiEAy%2BrDYfH5En%2FnmgaZxQB59jmltdJBvBZBPierQbx0HsAqiAQIuf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDLOIqsGSjli1rqlp%2FSrcA1iYvB5dwjiXr%2Fxm4JE%2Fm2vRzc8niepuz3IIBuvJitccuVoEzn1Agq3nruWMjjzGaofTqnN6S%2F60rJK3tT3fuyd1IXdH1hoG4ORA1%2F1jPjZHEs7xEOpcKyLk99q%2FB24DTdMJFCxlTtt7WmKU1zLOeq14NJvqFLSZnSGHRjltqZ20zKqNm6v117By2fSyuJ1H35EdfTx4GtU2rlLdPwn%2Bmp8AnHjpB8UqW%2FfhhLSqdXUwmpmsCi2iflALrFF%2BhuSs3G6dpvTB12fDA04nnU1y%2FeYCBQ9zbQjP%2FhnzkA4UC4PDLkTywS%2FcJgyC9JM%2FIEnAHhaID3PO6w35GdD%2B254gYe3K4oXgs7XE1xw5nSrXTqy69%2FhnHal9uoMUbivJ8R4WI5dPjicikIg7i3DE%2BfvUUMqNobDd%2FSQcPbUu5YegMplL91FfM7M1ItNp8JAdCQRHh3UgSSulsqmQXDZ98DXor9iDIbBcG5QzhjqckcElFk2mWJYc7jbU3YVQWm1LBCrDiw71ma2E3moJXEzIJT1jHbs0Sc9eJ%2Fwym9SAWI3xImnw0b3lbuYkXH1VVZU%2BdCKc%2FGBID8sysEVhzPJipQFQqiZkRGenjoHYlF%2Bhh2ViGJJKioSD%2B7B9goBm8tj%2BMJvXpr0GOqUBpVm8xcKRZJZEVQ9GMxIBQ1RR%2Bg1%2BW5jc7Sz5nOf%2BAe8QCIYPrj3kP%2BqOFAi59V%2Foe%2BG7n%2BGCvWS5q8S2RrITQz%2FmGkbU7H35nqdfv1%2FjgyEN%2FcIfqcVUsn4yxbM%2FNDjnacifLmL7hLoIr4mRZqq46VXSbMCdD85V7t9k%2FmVyEB%2Fw6TbvD90UfjfSYvlnjtUwvNu83efaCl31hnJygnZ89k%2B6w0C6&X-Amz-Signature=a5845ab07e75147773a463bff96beb5bc76a8599490ec2ebb29a1acbd60f5ceb&X-Amz-SignedHeaders=host&x-id=GetObject)



  rr


  ![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/1c9ce5ad-ec87-4678-b178-dd3f83e53f2e/c01e2d9f-cff0-42fa-bc55-dac5b03b364a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466TXXWXBXD%2F20250210%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250210T083814Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIA%2BA7SvVNlO50bS01QRtNpQtE%2F%2FJompQwlc9xJoNaTeGAiEA0XmwcIG67V2%2B3z097nViyB0KcmVjrXQQNCk%2FkhGiKa0qiAQIuf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDLs2mTK8UhV4eHCXEyrcA2v3CkFz9ZKEPmIUeHL5%2Fx1J2VB0%2F5a2KbkLeR75%2BrR01QEjxghMfj83e44zrotKJD6WpSdaCY5TyXDrtEGZS9sCuvPpuZ3CUgjYtQIXhPU%2BAOMcQewJq2P%2FT1i6Pv7LpwNYBImjCq3UjEqZd64l8wmE%2FNCYrjmbk8CVQYPsTqim9I8R54CGUf6w3fWwmEyZaXGO9bgcN%2BOCVksi5e35OSchC1qU632mD3mQoNR4JGY0CHuse6xtj%2B4N5JMnX%2BU%2FmbqB0RMlMPJAbx9lC4b0S8Kv8yrhe2Wn36S5SWiS36fnyw0CjySyRURERpwZzpSNROvn%2FjaoAtMgrkgJexsahK%2BLVocBxx%2FZ4OadBQ%2F5VnyxU9VByGQ9CiyrEiNPIgrWvzs%2FZ5K0%2B2dFJwhov%2F%2Bj6sI1g0tQaGmVu9MZWg6Dg9kt4fNqPRFrupTxiOZd%2FLIHn2wCCyjVoNLKNo3ZpJEX7IcF4Io6QzBWfRNaBZ48i66v36wviUlZOMgUOPerB10D5wqP8na0i7FFXG0BN4lUMCj9EzR%2Bwms4xsewQDjyIvzwDZRU8S1Qxw8siSZE9FLowo267VdTfGv0ecr1CbT12dlgtE5N3Vl92fhakewNwu96q7%2BBcLnf3g72QbksMK%2FXpr0GOqUBXDCWZhwRGpJP9Leagg5pNwFy5VQCr2IJZlZbWlEi09qCiNGxfuSe90lIntrLvbF%2FxrdNmVO%2FOZ%2BaNfOVyItWw2fXCUFpIi0Zm9rFIbc2gRkactg5Tk5rT6LI0mQydGmy3uJ49L8AmyyTtKnQYXNatmnhmWFfLZOT1Ip2L2kQaYKT1Q21AFGBFI6a1L7vTA9bg0cEhq4Y%2F3Isb4YSTSuYcgkMAwmG&X-Amz-Signature=543ad3655750f77de368af981f17cfd3eb7910ef9d84545fd47e225f8826c2c9&X-Amz-SignedHeaders=host&x-id=GetObject)


ΔW≈BA\Delta W \approx B A

- B∈Rd×rB \in \mathbb{R}^{d \times r}
- A∈Rr×kA \in \mathbb{R}^{r \times k}
- r≪min⁡(d,k)r \ll \min(d, k)（秩  遠小於原始矩陣維度）
  rr


  ![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/1c9ce5ad-ec87-4678-b178-dd3f83e53f2e/c01e2d9f-cff0-42fa-bc55-dac5b03b364a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB46666M4BMYU%2F20250210%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250210T083819Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJIMEYCIQC1RSvf0B6Y0lpU9w6ER1I8BJ5fl9QofXba0Mmz2sEA7AIhAMbiSMjMpj5p68iHvCMzbolnmJ1QZdQcLa2zzD9QBQNuKogECLn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMNjM3NDIzMTgzODA1IgyGlKEQ0rMj%2BlMqt6Aq3AP0AgHJl4Oiybzm8KkgqLpsgQf64RsP%2BvV75PWnZhktQ6faKRDxHnOzpRKIouhh75tU3lC4m%2FVen91I2NzTd57%2BgWh3vm8SpekVRocmsaQhOUMq1Zu5JJLlCtlxYtLhxnMtTe1XMi3LweRBCgADDOZQuIXMgdUu4JRgt5AVtraJEeUEDolanqyJq86BGcHonEBoGmye%2BGMoXE5x3yBgjphrcoKEcVyLtZBPFNcMbHMR5CVtWCEBYmIJ26WTRtaPwXnK7cAB1GZCGP5sl2QZu6FZFwG5nM9YTSgKwqnlVrJ8SQUvEFZKArOs3qLHhHpRXhWldTZfVNMfNH7wJiCB3QOfG5sSz90%2Faw7xZ0foK9sDUgBW14HbKcNWLRLsswQzMASPHN6YFUZp1sXG4oXjJIJoEi90aZRJfGfctvR%2FnPMU%2FqXkYoJZv0wu59YiZpW8vZD%2FMWg5QMHZoIi4%2BivJluuF6jZ5%2Bk5%2BZwiotgyNTMm0tKdcr2d7X2dUofdDF5ow%2FoNORcnEltPQzsx7KAP3ZULDegEVYfP00rP2yL%2BwqLlnIjiQpqQBDZ5TQ6mE8JhVQ1oHiVAzQ1nR4Cvo6%2BPT%2BCK%2BoPPzet8V0M00kmd749%2FFnNdhE%2BSNFgNcU%2BoCXDC%2F2Ka9BjqkAYHGMzQaem9nbCfUM2FY%2F%2Bh8Wc1TK34G1XrMXHiSzsEJ%2BwDRxjBE50ecKYA4sJ00PkIPjb%2Bd8rXAQ8IcEY5Qy9xoJtGyBk60eUsOmu19ZVQu8Nv%2FEOfIknxy3e7sY8NYhewwz1uriP%2ByyKmYMjuXYPl7%2FTB0yzwZk1Vj0bf7Y%2BLKzZpTnL3Akg1olHCM%2F3ysBBbL3NcGRkfKVmU9GAuHdfyd6skp&X-Amz-Signature=40f51f58eab6eac840fa4965835e6fcc78577d5478a7c1828a808d7abd7132fb&X-Amz-SignedHeaders=host&x-id=GetObject)


rr

![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/1c9ce5ad-ec87-4678-b178-dd3f83e53f2e/c01e2d9f-cff0-42fa-bc55-dac5b03b364a/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466TUFVGKV2%2F20250210%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250210T083807Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDOsD5gNIEAd04Kl5Qv6uG%2FI0CPMAEF3mn9se4win7XFgIgc6wUvheSk63nQeG3S%2FRpJ3BTfi%2Bphgg6AnadNarUPloqiAQIuf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDHDdddTA6tcguXPl%2ByrcA7EJ5jDHRtVgs2%2BvGWbp5Y02STnTxY%2BKWK%2FgHgVXM7A97KlBfzfX0ok1lZB4h0PjEhPQXZEGf4uNFel%2FoN0%2FZG2dYOvRAdR%2FfDjToutp8zOk%2Brwyo17bxq5mRyOvdOady9pmgt8pIR2YnIsTh5nJyK6BDFk1Ugj%2F83M%2Bfn35vtRbGVqUM45oeEKnSOytWPSmWA4FWI2rc4djwtQuieHEoQYooIq7mjFpMZ%2FTBzFzAyul8f8f%2B%2B%2BDSTnZfRHIbzxSur11JRLbXPvndulTZsF6UzyD02FaftCYZqacFHtuMmqBIu2P6O23ceeFdk%2FWrCc4%2BEqyMPN0EceI4xgY37Oyct8kBqgDsHUDxL0Kdx%2Bbh1qlq51KF2ib7mch%2FDuy%2FtOO%2Fjhg3htlUeJcw6OJbN4LY955m60llqLfRGSFJhFcLSZH6ri4XttgRCD6%2BKzezIGAqdXNmsWJG%2BMrjXY1i4k9oO%2BzSjoGwp3MzRwfpXlSim5WBzlNcdix1JU2rXdVOKH4nytu%2B4oUzJK8BhLyO11EU7SCjcwE%2Fjps%2Bm7M8e54gf84J1H0DQ%2BkDd2oKGZZcVaHXEIBGhtYZbZF%2FCkrtoO44k4V1SwrJcdMfuljSqVsCNUgeoPCebl6CCRD%2BxiDMP3Wpr0GOqUB6i%2B%2FUFut0ClCxUXWB%2F%2BtjHQzFQhyD%2B2dsgISfYMdnnqIxnTUdIJ1fZXCgn9R09R3EDy%2B6xfLtjFQ9UOZKFGAl4SH8FKqKHGtEkv%2FPJ9OlMyNsa9hjMJKf3z7YLzLhJJ31sm%2BU1v1%2Fo%2Bj3cbswfvAvV6d1G8ClqIOfXNA9ks4CwxhblbB43G%2FEFFPZEiX8gGpnwN5EKYA2BcH8BVwodUet2cVg2K5&X-Amz-Signature=d26fc9268d093d65ab8ebbe66fff3a58d81b5908f5bd922b7e43f6e6db78a34d&X-Amz-SignedHeaders=host&x-id=GetObject)

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
