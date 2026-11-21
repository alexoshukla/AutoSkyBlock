# 🌾 AutoSkyBlock (MineScript Macro)

> [!WARNING]
> ⚠️ **NOTE:** We take NO responsibility for account bans, server rule violations, or any consequences resulting from the use of this code. You use this script entirely at your own risk. Automating gameplay may violate the Terms of Service of many Minecraft servers — use it responsibly and only where permitted.

> [!IMPORTANT]
> 🚧 **Project Status: Experimental / Work in Progress** 🚧
> 
> This project is currently in its **early testing phase**. The "Garden" farming feature is just the starting point. More features (like Mining) will be added in the future. Expect bugs, and use with caution.

---

**AutoSkyBlock** is an advanced **MineScript** automation macro designed for **Hypixel SkyBlock**. It uses a coordinate-based navigation system to farm efficiently and supports multiple customizable profiles via a JSON configuration.

## ✨ Features

- **Multi-Profile Support:** Create, manage, and switch between different farming profiles (e.g., Wheat, Carrot) directly from an in-game menu.
- **Coordinate-Based Movement:** Instead of hardcoded timings, the bot moves to precise X, Y, Z coordinates, making it resilient to lag and speed changes.
- **In-Game UI Menu:** A fully interactive chat menu to select modes, start/stop macros, and record coordinates without editing code.
- **Dynamic Directional Movement:** Calculates the player's Yaw to press the correct movement keys (W, A, S, D) to reach the target, without moving the mouse.
- **Auto-Warp & Fly Disable:** Automatically travels from Lobby -> SkyBlock -> Garden, and toggles sneak to disable fly mode before farming.
- **Modular Architecture:** Code is split into `main.py` (manager) and `farms/` (specific farm logic), making it easy to add new features.

## 📋 Requirements

- [MineScript](https://github.com/maxsupermanhd/minescript) (Python API for Minecraft)
- A Minecraft instance with MineScript installed

## 🎮 How to Use (In-Game Menu)

1. Run the script in your Minecraft client. To do this, you have to copy the project files to your `minescript` folder and type `\main` in your chat.
2. An interactive menu will appear in the chat.
3. **Controls:**
   - `[Up/Down Arrow]`: Navigate through the menu.
   - `[=]`: Select / Start / Confirm.
   - `[-]`: Go back / Stop / Delete profile / Exit script.

### 🛠️ Creating a New Profile

1. In the main menu, select **Garden Farm** and press `[=]`.
2. Select **`[+] Add New Profile`** and press `[=]`.
3. Choose a hotbar slot (`1-9`) for your farming tool.
4. Move your character to the **start** of the row and press `/` to record the coordinate.
5. Move your character to the **end** of the row and press `/` again.
6. Repeat steps 4 and 5 for as many rows as you want to farm.
7. Press `[=]` to save the profile.

## ⚙️ Configuration (`garden_config.json`)

The script automatically generates and manages `farms/garden_config.json`. If you prefer to edit it manually, it looks like this:

```json
{
    "active_profile": "profile_1",
    "profiles": {
        "profile_1": {
            "hotbar_slot": 3,
            "waits": {
                "lobby": 2,
                "skyblock": 3,
                "garden": 3
            },
            "reached_threshold": 0.25,
            "farming_rows": [
                [[49.5, 71.0, -46.5], [49.3, 71.0, 142.5]],
                [[54.5, 71.0, 142.4], [54.3, 71.0, -46.7]]
            ]
        }
    }
}
