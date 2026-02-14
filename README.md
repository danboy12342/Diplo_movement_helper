# Diplomacy: Manual Order Entry

The simplest way to track Diplomacy games in person. Just type orders and watch the board update.

## 🚀 Setup

```bash
pip install -r requirements.txt
streamlit run diplomacy_manual.py
```

Make sure `map.png` is in the same directory.

## 🎮 How to Use

### Simple Workflow

1. **View the board** - See all units on the map
2. **Type orders** - Use the tabs for each power, type orders in plain text
3. **Submit orders** - Click "Submit Orders" for each power
4. **Process turn** - Click "Process Turn" to see units move

That's it!

### Order Format Examples

```
A PAR - BUR          (Move army from Paris to Burgundy)
F LON - NTH          (Move fleet from London to North Sea)
A MUN S A BER - SIL  (Army in Munich supports Berlin to Silesia)
F BRE S F MAO - ENG  (Fleet in Brest supports Mid-Atlantic to English Channel)
A ROM H              (Army in Rome holds)
```

### Power Colors on Map

- 🔴 Austria (Red)
- 🔵 England (Blue)
- 🟦 France (Light Blue)
- ⚫ Germany (Black)
- 🟢 Italy (Green)
- ⚪ Russia (White)
- 🟡 Turkey (Yellow)

## ✨ Features

- ✅ **Visual board state** - See all units on the map
- ✅ **Manual order entry** - Type orders the traditional way
- ✅ **Auto-update** - Map refreshes after processing
- ✅ **Unit reference** - Each tab shows current units for that power
- ✅ **Order review** - See all submitted orders before processing
- ✅ **Clean interface** - No complex dropdowns or clicking

## 💡 Tips

- You can edit orders before submitting - just change the text and click Submit again
- Use the "Current Units" section in each tab to see what you have
- Orders persist until you process the turn or clear them
- The game validates orders when processing - invalid orders are ignored

## 🎯 Why This Approach?

Manual order entry is actually **faster** for experienced players:
- Type orders naturally like you would on paper
- No clicking around the map
- Easy to copy/paste orders
- Familiar format for Diplomacy veterans

Perfect for in-person games where everyone calls out their orders! 🎲