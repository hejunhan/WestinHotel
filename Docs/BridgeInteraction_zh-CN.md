# hejunhan 关卡：锁交互与桥旋转

已在 `Content/Level/hejunhan.umap` 配置锁与桥的交互。实现保存在原有蓝图 `Content/BrigeBP/BP-BridgeControl.uasset` 中，关卡内控制器的标签为 `BP_BridgeControl`。该 BP 现在包含用户添加的 `SM_PasswordLock` 网格组件，每个实例自身就是一个锁机关；多个实例可以共同控制唯一的桥。

## 操作

1. 打开 `Content/Level/hejunhan` 关卡。
2. 运行游戏，控制角色靠近带锁网格的 `BP_BridgeControl`，距离该 BP 的 Actor 原点不超过 350 厘米。屏幕左下角会显示“旋转桥”和“E 旋转桥”。有多个 BP 时只显示范围内最近实例的提示。
3. 按 **E**：`Bridge` 在 2 秒内平滑顺时针旋转 90°。
4. 旋转期间提示切换为“桥正在旋转”，再次按 E 会被忽略；完成后恢复“E 旋转桥”，可再次交互，再转 90°。离开范围后提示隐藏。

这里的顺时针指从上方俯视，绕世界竖直 Z 轴增加 Yaw。桥保留原有 Pitch、Roll 和 Actor 原点位置，围绕自身现有原点旋转。

用户已在关卡中添加 PlayerStart。如果出生位置不在锁附近，可以在锁旁使用编辑器的“从此处运行 / Play From Here”，再靠近锁测试。运行窗口需要获得键盘焦点。

## 多个机关与一座桥

直接在关卡复制 `BP-BridgeControl` 实例并放到新的机关位置。每个实例会把 `LockActor` 绑定为 Self，不再搜索外部锁，也不需要给每个锁设置 Actor Tag。其他机关或外部锁模型不会因为带有旧锁标签而被该 BP 绑定。

唯一的桥保留 Actor Tag `WH_hejunhan_Bridge`，网格组件设置为 Movable。多个 BP 都找到这座桥。不要给第二个 Actor 设置相同的桥标签。

同一个 E 键事件允许传递到多个 BP，每个 BP 重新查询范围内最近的锁实例，只有选中的实例接受交互；等距时使用查询列表中的第一个。提示也只由该实例显示，因此相邻机关不会重复触发或叠加提示。距离从 BP Actor 原点计算，放置机关时应让原点靠近锁网格。

旋转开始时，触发实例在桥的 Actor Tags 中加入临时标记 `WH_BridgeRotating`。所有实例共享这个忙碌状态，另一个锁不能同时旋转该桥。完成时只移除这个临时标记，保留桥原有标签；正在旋转的实例销毁或结束运行时也会释放它。空闲实例不能释放其他实例的旋转状态。

## 调整参数

打开 `BP-BridgeControl`，在 **类默认值 / Class Defaults** 修改以下变量，然后编译并保存：

| 变量 | 默认值 | 含义 |
| --- | --- | --- |
| `RotationDegrees` | 90 | 每次旋转的角度，正值为俯视顺时针 |
| `RotationDuration` | 2 | 旋转时长，单位秒 |
| `InteractionDistance` | 350 | 角色与锁之间允许交互的距离，单位厘米 |
| `LockActorTag` | `WH_hejunhan_Lock` | 旧版兼容变量，当前不再用于绑定锁 |
| `BridgeActorTag` | `WH_hejunhan_Bridge` | 用于运行时寻找桥的 Actor Tag |
| `BridgeBusyTag` | `WH_BridgeRotating` | 多实例共享的临时忙碌标记，所有实例应使用相同值 |

桥的 Static Mesh Component 已设置为 **Movable**。桥标签应只对应一个目标 Actor；更换桥时同步调整 Actor Tags。这里使用 Actor 的 Tags，不是 Component Tags。`LockActor`、`BridgeActor`、最近锁引用和旋转状态由运行逻辑赋值。

## 蓝图逻辑

- `BeginPlay` 调用 `ResolveBridgeActors`，将锁绑定为 Self，并在当前游戏世界按标签寻找唯一的桥，然后启用玩家 0 的输入，关闭空闲 Tick。
- E 键的 Pressed 连接 `InteractLock`，不消耗输入。该函数调用 `FindNearestBridgeLock`，确认自身是最近的有效范围内实例，再检查本实例旋转状态、目标有效性、玩家距离和共享桥忙碌标记；通过后获取共享忙碌标记，记录桥起始角度并启用 Tick。
- `AdvanceBridgeRotation` 按 Delta Seconds 累积时间，通过 Ease In Out 插值更新 Yaw；到达目标角度后调用 `StopBridgeRotation`，清除旋转状态并关闭 Tick。
- `ConfigureBridgeActors` 保留为设置引用的辅助函数；正常运行使用新的 Self 绑定流程，目标缺失时交互安全退出。
- `EnsureBridgePromptUI` 直接复用项目现成的 `DSH_交互/V42_翻板按钮交互/Runtime/UI/WBP_FlipInteraction`，创建桥的独立实例并添加到视口，不修改原控件资产。提示保持其现有左下角排版。
- `RefreshBridgePrompt` 由绑定到控制器的循环计时器每 0.1 秒调用，检查自身是否为最近锁以及锁、桥、角色与距离，更新文字和显隐。旋转提示读取桥上的共享忙碌标记，因此换到另一处锁时也能显示“桥正在旋转”。使用 Hit Test Invisible，提示不拦截操作；空闲时仍不启用 Actor Tick。
- `StopBridgeRotation` 先调用 `ReleaseBridgeBusy` 释放由本实例持有的共享忙碌状态，再清除本实例旋转状态并停止 Tick。
- `EndPlay` 先停止并释放本实例的旋转，再调用 `RemoveBridgePrompt` 移除自身控件实例；计时器随控制器生命周期结束。

## 验证记录

使用本机 Unreal Engine **5.8.3** 编译和后台 Play/Simulate 验证：

- 12 个蓝图图表均为 0 错误、0 警告。
- 110 项运行检查通过，包括运行时自身锁绑定、用户锁网格组件保留、距离限制、重复触发保护、90° 到位、第二次旋转、时间步过大时不超调、目标缺失处理，以及保留桥原点与 Pitch/Roll。提示检查覆盖原 Widget 类复用、加入视口、范围显隐、旋转状态文字、目标缺失隐藏、真实计时器自动隐藏和控件移除。
- 在 PIE 中临时生成额外两个 BP 实例，验证多个锁绑定同一桥、重叠范围只接受最近锁、另一个锁不能打断旋转、完成后另一个锁可继续触发、共享忙碌标记正确释放，以及销毁旋转实例时清理标记和提示。测试实例没有写入关卡。
- 实际游戏 Tick 产生中间角度并在 2 秒游戏时间到达 90°，完成后关闭 Tick。

后台验证使用 NullRHI，并直接调用交互函数；**没有验证 GPU 画面或实体键盘 E 输入**。请按上面的操作步骤在编辑器窗口确认画面和按键体验。

精简验证结果保存在 [BridgeInteractionValidation.json](BridgeInteractionValidation.json)。完整脚本、日志与运行结果位于本机 `Saved/CodexBridge/`，该目录不进入 Git。

修改前的原始关卡和蓝图备份位于 `Saved/CodexBridge/Backups/20261005-222348/`。
添加提示前的桥蓝图另备份于 `Saved/CodexBridge/Backups/BeforePrompt/`。
本次调整多机关之前的用户蓝图另备份于 `Saved/CodexBridge/Backups/BeforeMultiLock/`。本次没有修改关卡，保留用户添加的 PlayerStart、Plane、灯光及 BP 内组件。
