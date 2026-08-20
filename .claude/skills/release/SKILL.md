---
name: release
description: Publish brilliant_sdk packages to PyPI, npm and pub.dev. Use when releasing or publishing any brilliant-ble / brilliant-msg / brilliant-sdk / simple_brilliant_app / halo-emulator package, or when checking which packages are ahead of their registry.
---

# Releasing brilliant_sdk packages

Three independent ecosystems live in this monorepo: `python/` (PyPI), `webbluetooth/`
(npm) and `flutter/` (pub.dev). Each has its own versions and its own publish
mechanics. A release round usually touches only a subset.

## The rule that matters most

**Local checkouts do not resolve dependencies the way users do.** The uv workspace,
the npm `node_modules` symlinks, and the Flutter `pubspec_overrides.yaml` files all
point sibling packages at *local source*. So a package can call an API that exists
only in its unreleased sibling, pass every local test, and still fail instantly for
anyone installing from a registry.

This has already shipped broken releases. Treat "tests pass locally" as **no
evidence at all** about whether a release will install and run.

## 1. Work out what actually needs publishing

Compare each package's manifest version against its registry:

```bash
# PyPI — the JSON API lags after a publish; prefer a real resolve to confirm
curl -s https://pypi.org/pypi/<name>/json | python3 -c "import json,sys;print(json.load(sys.stdin)['info']['version'])"
npm view <name> version
curl -s https://pub.dev/api/packages/<name> | python3 -c "import json,sys;print(json.load(sys.stdin)['latest']['version'])"
```

Publish only packages whose manifest is ahead. Meta-packages usually need nothing:
the Python and Dart ones resolve dependencies at install time, so an existing range
already picks up a new sibling. **npm is different — see section 4.**

## 2. Check for unreleased API in dependencies

For every package about to be published, diff each *dependency* against what is
actually on the registry. A dependency whose source has moved ahead without a
version bump is the failure mode this repo has hit before.

```bash
# unpack the published artifact, then diff against local source
diff -ru <unpacked-published>/<module> <local>/src/<module> -x __pycache__
```

If a dependency has gained API, **release the dependency first and raise the
consumer's floor in the same change**. A floor of `>=3.0.0` is a promise that the
package works against 3.0.0 — not merely that it works against whatever you have
installed.

## 3. The pre-publish gate: resolve at declared minimums

This catches floor-too-low bugs deterministically, before anything is uploaded.

**Python** — build the wheel, install it into a scratch project resolved at minimums,
then exercise the API:

```bash
uv build --package <name>
# in a scratch dir OUTSIDE the repo:
uv init && uv add --refresh --resolution lowest <name>==<version>
uv sync --resolution lowest
./.venv/bin/python -c "import <module>; ..."   # exercise connect()/the new API
```

Note `--resolution lowest-direct` only lowers *direct* dependencies; use `lowest` to
lower transitives too. Also pass the flag to `uv run`, or invoke `.venv/bin/python`
directly — `uv run` silently re-resolves to highest otherwise.

**Dart** — this check must run in a **scratch app outside the repo**. Inside the
monorepo `pubspec_overrides.yaml` substitutes local paths and defeats it entirely.

**npm** — install the packed tarball into a scratch project and confirm the declared
`main`, `module` and `types` files all exist in the installed package.

## 4. npm: dependencies resolve at install time — keep the floors honest

`brilliant-msg` and `brilliant-sdk` mark their siblings as `external` in
`vite.config.ts`, so they are resolved from `node_modules` rather than baked into the
bundle. Consequences:

- Declared ranges are **real**. If a package calls new sibling API, raise its floor.
- Build order still matters for local verification: `brilliant-ble` → `brilliant-msg`
  → `brilliant-sdk`.
- `dist/` is gitignored and **not** committed. Always `npm run build` before
  publishing; a stale `dist/` will otherwise ship silently.
- Keep the TypeScript devDependency **pinned to an exact version** across all three
  packages. A caret once let one package resolve a newer minor, which changed
  declaration output and type-checking behaviour for that package alone.
- Declaration output is pinned with `dts({ entryRoot: 'src' })`. Without it, a
  `paths` alias that pulls a sibling's sources into the program shifts declarations
  into a nested directory and silently breaks the declared `types` entry. If
  `dist/index.d.ts` ever goes missing, check that first.

## 5. Publish order

Always dependency-first, so a consumer never lands on a registry before the version
it requires:

- **PyPI**: `brilliant-ble` → `brilliant-msg` → `brilliant-sdk`. `halo-emulator` is
  independent (it imports `brilliant-msg` only for the optional Lua-stdlib adapter).
- **npm**: `brilliant-ble` → `brilliant-msg` → `brilliant-sdk`.
- **pub.dev**: `brilliant_ble` → `brilliant_msg` → `brilliant_sdk` →
  `simple_brilliant_app`.

## 6. Mechanics

**PyPI** — `uv publish` does not read `~/.pypirc`; pass the token explicitly with
`--token`. Inspect the built wheel before uploading (`unzip -l`) to confirm data
files are present and no `__pycache__` crept in.

**npm** — requires a granular access token with 2FA bypass. Verify with
`npm whoami`; an `E401` means the token expired, not that config is missing. Check
the tarball contents with `npm pack --dry-run`.

**pub.dev** — use `flutter pub publish`, not `dart pub publish`. Run `--dry-run`
first and expect zero warnings; the `pubspec_overrides.yaml` *hints* are normal in
this monorepo (the file is gitignored and never reaches the tarball). If resolution
fails immediately after publishing a dependency, `dart pub cache repair` flushes the
stale local cache.

**Working tree** — publish from a clean tree. `pub publish` packs the working
directory, so uncommitted edits anywhere under a package (including `example/`) end
up in the tarball. Stash unrelated changes first.

## 7. Versioning

- New public API on a package → **minor** bump, and raise consumers' floors to match.
- Removing or changing existing public API → **major**.
- Changing how a package is *packaged* (for example, making a bundled dependency
  external) is breaking for anyone loading the UMD build via a plain `<script>` tag,
  even when ESM consumers see no difference. Prefer a major bump and say so plainly
  in the changelog.
- Never edit historical changelog entries; they described the versions they shipped
  with. Add a new entry instead.
- Python `__version__` is derived from installed package metadata, so it needs no
  manual update — never reintroduce a hardcoded version string.

## 8. After publishing

Verify from a scratch project outside the repo — a fresh install of each published
package, plus an import and a real call. If hardware is available, connect to a
device and read `frame.FIRMWARE_VERSION`; `connect()` is where dependency-resolution
bugs surface first.
