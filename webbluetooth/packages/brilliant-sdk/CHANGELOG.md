## 1.1.0

* Rebundles `brilliant-msg` 2.1.0 — the Halo firmware 0.8.8 true-up. `RxTap` now emits Halo's native tap kind (`single`/`double`/`triple`) directly instead of inferring it from timing, and the `tap.lua` and `sprite.lua` device libraries are updated to match
* `brilliant-msg` dependency floor raised to `^2.1.0`

Note: `brilliant-sdk` bundles `brilliant-ble` and `brilliant-msg` into its `dist/` output, so picking up a dependency update requires a new release of this package rather than just a re-install.

Releases before 1.1.0 predate this changelog; see the `brilliant-ble` and `brilliant-msg` changelogs for the corresponding history.
