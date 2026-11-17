# 🌾 AutoSkyBlock (MineScript Macro)
A MineScript macro for farming in SkyBlock.

> [!WARNING]
> ⚠️ **NOTE:** We take NO responsibility for account bans, server rule violations, or any consequences resulting from the use of this code. You use this script entirely at your own risk. Automating gameplay may violate the Terms of Service of many Minecraft servers — use it responsibly and only where permitted.

> [!IMPORTANT]
> 🚧 **Project Status: Experimental / Work in Progress** 🚧
> 
> This project is currently in its **early testing phase**. The "Garden" farming feature is just the starting point. More features, automations, and stability improvements will be added in the future. Expect bugs, and use with caution.

---

**AutoSkyBlock** is a simple **MineScript** automation macro primarily designed for farming in **Hypixel SkyBlock Garden** (or similar SkyBlock setups). It handles navigation, harvesting, and moving between rows automatically using a zig-zag pattern. 

## ✨ Features

- **Hotkey controlled** — start and stop with a single key press.
- **Automatic warp recovery** — warps back to the garden if you're not there.
- **Zig-zag farming pattern** — harvests row by row with configurable timings.
- **Threaded execution** — the key listener runs separately so you can stop the script at any time.

## 📋 Requirements

- [MineScript](https://github.com/maxsupermanhd/minescript) (Python API for Minecraft)
- A Minecraft instance with MineScript installed

## 🎮 Controls

| Key | Action |
|-----|--------|
| `=` | Start the macro |
| `-` | Stop the macro |

## ⚙️ Configuration

All tunable values are at the top of `garden.py`:

```python
movingkeys    = "LA"     # movement keys (informational)
movingforvard = 1.94     # seconds to move forward to next row
movingtime    = 23       # seconds to harvest a full row (each direction)
startmove     = 0.5      # startup delay
loopnumber    = 19       # number of rows to farm
safezonemove  = 0.3      # short safety move near row edges
