---
layout: post
title: "RLHF ，policy gradient ， actor-critic PPO相關介紹"
categories: ['NotionExport']
math: true
date: 2025-02-21 10:00:00 +0800
---

### RL 主要組件：

1. Actor（行為者）：我們可以調整的部分，透過調整 Policy 來最大化 Reward。
1. Env（環境）：系統給定，無法控制。
1. Reward Function（獎勵函數）：也是事先給定的，無法調整。
唯一可調整的是 Actor，透過 Policy 來提高 Reward！



---

## 🎮 RL 在遊戲中的應用

在遊戲中，整個學習過程不斷循環，直到遊戲結束，每一次完整的遊戲過程稱為 「Episode」。

我們的目標是讓 Actor 最大化遊戲過程中的 Reward，定義如下：



R=∑t=1TrtR = \sum_{t=1}^{T} r_t



🔹 Actor 具有隨機性，我們只能計算它的期望值：



Rˉ(θ)=∑τR(τ)pθ(τ)=Eτ∼pθ(τ)[R(τ)]\bar{R}(\theta) = \sum_{\tau} R(\tau) p_{\theta}(\tau) = E_{\tau \sim p_{\theta}(\tau)}\left[R(\tau)\right]



其中：

- τ為一個可能的 trajectory（軌跡）。
- 計算出所有可能的 τ 出現的機率，並加權平均其 total reward，即為期望值。
👉 我們透過 Policy Gradient 方法來最大化這個期望值！



---

## 📈 Policy Gradient 方法

既然我們知道期望值的計算方式，我們可以利用 Gradient Ascent（梯度上升） 來優化 Reward Function。

🔹 簡單來說，就是在參數更新時改為「加」而不是「減」！



---

## 🔥 PPO（Proximal Policy Optimization）

PPO 是 Policy Gradient 方法的進一步優化，主要透過 數學推導與 Importance Sampling 來得到一個新的 Objective Function：



Jθ′(θ)=E(st,at)∼πθ′[Pθ(at∣st)Pθ′(at∣st)Aθ′(st,at)]J^{\theta'}(\theta) = E_{(s_t, a_t) \sim \pi_{\theta'}} \left[ \dfrac{P_\theta(a_t \vert s_t)}{P_{\theta'}(a_t \vert s_t)} A^{\theta'}(s_t, a_t) \right]



進一步，加入 約束項 (constraint)，形成 PPO 目標函數：



JPPOθ′(θ)=Jθ′(θ)−βKL(θ,θ′)J_{PPO}^{\theta'}(\theta) = J^{\theta'}(\theta) - \beta KL(\theta, \theta')



其中：

- Pθ(at∣st)Pθ′(at∣st)\dfrac{P_\theta(a_t \vert s_t)}{P_{\theta'}(a_t \vert s_t)} 是 重要性加權 (Importance Sampling)，確保策略更新時的穩定性。
- 加入 KL 散度 (KL Divergence) 作為正則化項，防止 Policy 更新過大。
📌 這樣可以確保 Actor 的策略更新不會偏離太遠，提升學習的穩定性！



---

### 🖼️ 相關圖示：

📌 PPO 方法的梯度更新過程示意圖：

![image]({{ site.baseurl }}/images/19ffbb85-7f9e-8056-99b9-e201ad4765af.png)

📌 Policy Gradient 的更新方式：

![image]({{ site.baseurl }}/images/19ffbb85-7f9e-80dd-a436-c4ce833be2bd.png)



---

## 🏁 總結：

- RL 三大組件：Actor（可調整）、Env（不可控）、Reward Function（不可控）。
- Policy Gradient 方法：透過梯度上升來優化策略，最大化 Reward。
- PPO：在 Policy Gradient 的基礎上，加入 Importance Sampling 和 KL 散度，提升學習穩定性。
🎯 這些概念是強化學習中最核心的內容，掌握後就能理解 PPO 如何在 AI 訓練中發揮作用！

📺 參考影片：

- [RL 課程影片 1](https://www.youtube.com/watch?v=z95ZYgPgXOY&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_)
- [RL 課程影片 3](https://www.youtube.com/watch?v=OAKAZhFmYoI&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_&index=3)
