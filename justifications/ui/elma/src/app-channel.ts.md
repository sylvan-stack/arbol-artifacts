---
role: authored
---
# Justifications

## AppChannel

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

## AppChannel.call

Reason: Sync the published shared design and connect tab entry and Refresh to `app.readVigor({})` through the 30-second App channel. Coalesce reads in flight, validate the reply, retain the last answer on failure and discard replies after disposal. Report a missing host method in the browser or on an older host. Serves BKD-3.18.

Origins: BKD-3.18 · Intention i-ea002c00 · 2026-11-12

## <before AppChannel>

Removed: Use the shared selector in the Elma renderer and route choices through the native app channel.

Removed by Intention i-0dec02d0 · 2026-11-11

## <before RootMethod>

Removed: Wire the shared header to the window Trunk and retain it on dispatch replay

Removed by Intention i-3d376ddd · 2026-11-11

## AppChannel.callRoot

Removed: Wire the shared header to the window Trunk and retain it on dispatch replay

Removed by Intention i-3d376ddd · 2026-11-11

## AppMethod

Reason: Sync the published shared design and connect tab entry and Refresh to `app.readVigor({})` through the 30-second App channel. Coalesce reads in flight, validate the reply, retain the last answer on failure and discard replies after disposal. Report a missing host method in the browser or on an older host. Serves BKD-3.18.

Origins: BKD-3.18 · Intention i-ea002c00 · 2026-11-12

## RootMethod

Removed: Wire the shared header to the window Trunk and retain it on dispatch replay

Removed by Intention i-3d376ddd · 2026-11-11

## isRootChoice

Removed: Wire the shared header to the window Trunk and retain it on dispatch replay

Removed by Intention i-3d376ddd · 2026-11-11

## <before TrunkMethod>

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

## AppChannel.currentTrunk

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

## AppChannel.trunkSelector

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

## TrunkMethod

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

## isTrunkCode

Reason: Wire the shared header to the window Trunk and retain it on dispatch replay

Origins: BKD-0.11, BKD-1.7, BKD-3.16 · Intention i-3d376ddd · 2026-11-11

