---
layout: post
title: "RLHF ，policy gradient ， actor-critic PPO相關介紹"
categories: ['NotionExport']
math: true
date: 2025-02-20 10:00:00 +0800
---

[https://www.youtube.com/watch?v=z95ZYgPgXOY&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_](https://www.youtube.com/watch?v=z95ZYgPgXOY&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_)

[https://www.youtube.com/watch?v=OAKAZhFmYoI&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_&index=3](https://www.youtube.com/watch?v=OAKAZhFmYoI&list=PLJV_el3uVTsODxQFgzMzPLa16h6B8kWM_&index=3)



在RL內有三個component：

- Actor
- Env
- Reward Function
其中Env與Reward Function是無法控制的，屬於事先給定，只有Actor是我們可以調整的，透過調整Policy來提高得到的Reward。

Policy ⇒ 調整actor 的策略

以遊戲為例：

整個過程一直循環，直到遊戲結束，一場遊戲稱為『episode』，整個遊戲過程的reward以R來表示，即R=\sum_{t=1}^Tr_t，actor的目的就是得到最大的reward。

Actor本身是有隨機性的，只能計算它的期望值：



$$

\bar{R}\theta=\sum\tau R(\tau)p_\theta(\tau)=E_{\tau \sim p_\theta(\tau)}\left[R(\tau)\right]

$$

- 在給定θ的情況下的R期望值是多少
- 窮舉所有可能的trajectory-τ，根據θ計算某一個τ出現的機率，計算這個τ的total reward，再weighted fair這個τ出現的機率，就是期望值
- 從pθ(τ)這個分佈中sample一個trajectory-τ，計算R(τ)的期望值


Policy Gradient

- 知道期望值怎麼計算之後就可以利用Gradient Ascent來最大化reward function，只是單純在更新參數的時候由減調整為加


![image]({{ site.baseurl }}/images/19ffbb85-7f9e-80dd-a436-c4ce833be2bd.png)



PPO

- 再經過一對數學推導和加上Importance Sampling後 得到一個新的object function
J^{\theta'}(\theta) = E_{(s_t, a_t) \sim \pi_{\theta'}} \left[ \dfrac{P_\theta(a_t \vert s_t)}{P_{\theta'}(a_t \vert s_t)} A^{\theta'}(s_t, a_t) \right]

- 把上述 公式加入一個constrain(約束項) 就是ppo了
J_{PPO}^{\theta'}(\theta) = J^{\theta'}(\theta) - \beta KL(\theta, \theta')



![image]({{ site.baseurl }}/images/19ffbb85-7f9e-8056-99b9-e201ad4765af.png)
