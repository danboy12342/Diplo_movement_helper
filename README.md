# Diplomacy Interactive Order Manager

A point-and-click interface for managing Diplomacy game orders in person.

## get going

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place your map:**
   - Make sure `map.png` is in the same directory as `app.py`

3. **Run the app:**
   ```bash
   streamlit run diplomacy_app_fixed.py
   ```

## 🎮 How to Use

### Giving Orders

1. **Select a unit:** Click on any colored circle on the map
   - A gold ring will appear around the selected unit
   - Unit info shows in the sidebar

2. **Choose order type:** Use the radio buttons in the sidebar:
   - **MOVE** - Move unit to a destination
   - **SUPPORT** - Support another unit (click the unit to support)
   - **CONVOY** - Convoy orders
   - **HOLD** - Unit holds its position

3. **Click destination:** 
   - For MOVE: Click the province you want to move to
   - For SUPPORT: Click the unit you want to support
   - For HOLD: The order is created immediately

4. **View orders:** All current orders appear in the sidebar organized by power

5. **Process turn:** Click the "Process" button when ready to resolve orders

### Power Colors

- 🔴 **Austria** - Red
- 🔵 **England** - Blue
- 🟦 **France** - Light Blue
- ⚫ **Germany** - Black
- 🟢 **Italy** - Green
- ⚪ **Russia** - White
- 🟡 **Turkey** - Yellow

### Controls

- **Cancel Selection** - Deselect the currently selected unit
- **Process** - Adjudicate the current turn
- **Reset** - Start a new game from Spring 1901


## 📝 Files

- `diplomacy_app_fixed.py` - Main application
- `map.png` - The Diplomacy game map
- `requirements.txt` - Python dependencies
