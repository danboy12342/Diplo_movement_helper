# Diplomacy Interactive Order Manager

A simplified point-and-click interface for managing Diplomacy game orders in person.

## get going
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place your map:**
   - Make sure `map.png` is in the same directory as `diplomacy_app_simple.py`

3. **Run the app:**
   ```bash
   streamlit run diplomacy_app_simple.py
   ```


### Simple Workflow

1. **Click a unit** on the map (the colored circles)
   - A gold ring appears around the selected unit
   - The Order Panel opens in the sidebar

2. **Choose what to do** using the dropdown menus:
   - **Hold** - Unit stays in place (just click confirm)
   - **Move** - Select destination from dropdown of valid provinces
   - **Support** - Select which unit to support and what action to support
   - **Convoy** - Simplified convoy interface (for fleets)

3. **Confirm the order** - Click the confirm button

4. **Repeat** for all units

5. **Process the turn** - Click "▶️ Process" when ready

That's it! No more double-clicking or selecting modes first.

### Power Colors

- 🔴 **Austria** - Red
- 🔵 **England** - Blue
- 🟦 **France** - Light Blue
- ⚫ **Germany** - Black
- 🟢 **Italy** - Green
- ⚪ **Russia** - White
- 🟡 **Turkey** - Yellow

### Features

- ✅ **Smart dropdowns** - Only shows valid options for each unit
- ✅ **Visual feedback** - Selected units highlighted with gold ring
- ✅ **Order management** - Delete orders with trash button
- ✅ **Auto-validation** - Can't create invalid orders
- ✅ **Province detection** - Shows which province you're hovering

### Controls

- **Click unit** - Select/deselect
- **Click empty space** - Deselect current unit
- **Cancel Selection** - Deselect button in sidebar
- **🗑️** - Delete individual orders
- **Process** - Adjudicate the current turn
- **Reset** - Start a new game from Spring 1901


### Dropdown shows no options?
- This means the unit has no valid moves from its current position
- Try a different unit or use "Hold"

### Orders not working?
- Make sure you click "Confirm" after selecting from dropdowns
- Check that you selected a valid option
- Fleets can only move to coastal/sea provinces
- Armies can only move to land provinces