# anlanroom：small1 单次交互机关

实现沿用 `Content/AnlanBP/BP_AnlanCombination.uasset`，关卡中的控制器仍叫 `BP_AnlanCombination`。蓝图名称保留，玩法已改为：只有 small1，交互一次就启动。

靠近 `anlan_intersmall1` 按一次 **E**，`anlan_inter1` 默认在 2 秒内绕世界竖直 Z 轴顺时针旋转 90°。不需要 small2，不再等待第二个激活状态。旋转期间重复输入不会重置进度；完成后不再触发，重新运行关卡会重置状态。

## Actor 绑定与参数

选中关卡中的 `BP_AnlanCombination`，在 Details 的“机关绑定与设置”分类修改：

| 变量 | 当前绑定或默认值 | 含义 |
| --- | --- | --- |
| `TriggerActor1` | `anlan_intersmall1` | 唯一的交互 Actor |
| `TargetActor` | `anlan_inter1` | 旋转目标 Actor |
| `RotationDegrees` | 90 | 旋转角度，正值为俯视顺时针 |
| `RotationDuration` | 2 | 旋转时长，单位秒 |
| `InteractionDistance` | 350 | 允许交互的距离，单位厘米 |

引用直接绑定 Actor。修改原 Actor 的 mesh、材质仍可使用原绑定；替换整个 Actor 后用吸管重新指定引用。目标网格组件需要保持 Movable。

旧版 `TriggerActor2` 和 `Activated2` 保留在“旧版未使用”分类，不再参与交互、旋转或提示；`TriggerActor2` 不再暴露为实例可编辑参数。可以没有 small2 Actor，本次没有删除用户场景中的模型。

距离是玩家 Actor 原点到 small1 Actor 原点的三维距离，不要求看向目标。旋转保留目标 Pitch、Roll、位置和缩放，围绕目标原有 Actor 原点进行。

## 蓝图流程与提示

- `EvaluateInteraction` 仅检查 small1、目标和玩家是否有效，计算到 small1 的距离；在范围内且未激活时选择索引 1。
- E 的 Pressed 调用 `InteractNearest`，再调用 `TryActivateTrigger`。只有索引 1、距离满足、尚未激活且未完成时，设置 `Activated1` 并立即调用 `TryStartRotation`。
- `TryStartRotation` 只要求 `Activated1` 为 true，记录目标当前旋转、清零时间并开启 Tick。
- `AdvanceTargetRotation` 使用 Ease In Out 平滑更新 Yaw。到位后标记 Completed，清除 IsRotating 并关闭 Tick。
- 提示复用 `WBP_FlipInteraction`，第二行留空。靠近时显示“E 启动机关”，旋转时显示“机关正在旋转”，完成后显示“机关已完成”；每 0.1 秒更新范围显隐。
- EndPlay 移除本控制器的提示。状态仅保存在当前运行，不写入 SaveGame。

## 验证与备份

Unreal Engine 5.8.3 中，11 个图表编译为 0 错误、0 警告。后台验证覆盖单次交互立即启动、没有 small2 引用时仍可运行、第二个索引无效、距离限制、重复输入保护、90° 到位、姿态与位置保留以及提示显隐和清理。结果见 [AnlanCombinationValidation.json](AnlanCombinationValidation.json)。

后台验证使用 NullRHI 并直接调用交互函数，没有验证 GPU 画面和实体 E 键。

修改前蓝图备份：`Saved/CodexAnlan/Backups/BeforeSingleTrigger/BP_AnlanCombination.uasset`。初次放置控制器前的关卡备份仍在 `Saved/CodexAnlan/Backups/BeforeCombination/anlanroom.umap`。
