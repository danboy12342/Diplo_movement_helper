import streamlit as st
import diplomacy
from streamlit_image_coordinates import streamlit_image_coordinates
from scipy.spatial import distance
import os

# --- 1. SETUP & CONFIG ---
st.set_page_config(layout="wide")

# Initialize Game State
if 'game' not in st.session_state:
    st.session_state.game = diplomacy.Game()
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None # Stores the unit currently being moved
if 'orders_log' not in st.session_state:
    st.session_state.orders_log = {} # Stores pending orders

game = st.session_state.game

# --- 2. MAP COORDINATES (The "Hard" Part) ---
# You need to map pixel coordinates to Province names for your specific image.
# Open your map in Paint/Photoshop, hover over centers, and write down X,Y.
# This is a TINY sample for demonstration. You must fill this out!
PROVINCE_CENTERS = {
    "LON": (340, 230), "LVP": (310, 180), "EDI": (310, 130),
    "PAR": (360, 360), "BRE": (290, 350), "MAR": (390, 480),
    "BUR": (410, 360), "PIC": (360, 320), "BEL": (410, 310),
    "ENG": (280, 280), "MAO": (150, 400), "SPA": (250, 500)
    # ... You need to add the rest of the 75 provinces ...
}

def get_closest_province(x, y):
    """Finds the province name closest to the clicked pixel."""
    coords = list(PROVINCE_CENTERS.values())
    names = list(PROVINCE_CENTERS.keys())
    
    if not coords: return None
    
    # specific map logic: find index of closest point
    closest_index = distance.cdist([(x, y)], coords).argmin()
    return names[closest_index]

# --- 3. UI LAYOUT ---
st.title("Diplomacy: Point & Click Interface")

col_map, col_sidebar = st.columns([3, 1])

with col_map:
    # Load your map image
    # For this code to work, put a file named 'map.png' in your folder
    # or use a URL.
    map_path = "map.png" 
    
    # If you don't have a map image yet, we handle that gracefully
    if not os.path.exists(map_path):
        st.error("Please add a 'map.png' file to your directory to use Point-and-Click.")
    else:
        st.write(f"**Phase:** {game.phase}")
        
        # This component renders the image and returns click coordinates
        # key="map" ensures it doesn't reload unnecessarily
        coords = streamlit_image_coordinates(map_path, key="map_click", width=800)

        # --- THE CLICK LOGIC ---
        if coords:
            x, y = coords['x'], coords['y']
            clicked_prov = get_closest_province(x, y)
            
            if clicked_prov:
                # Logic: State Machine
                
                # STATE A: Nothing Selected -> Select a Unit
                if st.session_state.selected_unit is None:
                    # Check if a unit exists in that province
                    unit_in_prov = None
                    for unit in game.get_units():
                        # unit string format is usually "A PAR" or "F LON"
                        if unit.split()[1] == clicked_prov:
                            unit_in_prov = unit
                            break
                    
                    if unit_in_prov:
                        st.session_state.selected_unit = unit_in_prov
                        st.toast(f"Selected: {unit_in_prov}")
                    else:
                        st.toast(f"No unit in {clicked_prov}")

                # STATE B: Unit Selected -> Select Destination
                else:
                    unit = st.session_state.selected_unit
                    target_prov = clicked_prov
                    
                    # Basic Move Order
                    # (You can add buttons to toggle Support/Convoy modes later)
                    order_str = f"{unit} - {target_prov}"
                    
                    # Save the order
                    try:
                        game.set_order(unit, order_str)
                        st.toast(f"Order Created: {order_str}")
                        # Deselect after ordering
                        st.session_state.selected_unit = None
                    except Exception as e:
                        st.error(f"Invalid Move: {e}")
                        st.session_state.selected_unit = None

with col_sidebar:
    st.subheader("Current Orders")
    
    # Display Active Selection
    if st.session_state.selected_unit:
        st.info(f"ordering: **{st.session_state.selected_unit}**")
        if st.button("Cancel Selection"):
            st.session_state.selected_unit = None
            st.rerun()

    # Display Orders grouped by Power
    for power in game.powers:
        orders = game.get_orders(power)
        if orders:
            with st.expander(power, expanded=True):
                for order in orders:
                    st.write(f"- {order}")

    st.divider()
    
    if st.button("Adjudicate Turn", type="primary"):
        game.process()
        st.session_state.selected_unit = None
        st.rerun()
        
    if st.button("Reset Game"):
        st.session_state.game = diplomacy.Game()
        st.rerun()

# --- 4. DEBUG INFO (Optional) ---
# Helps you build your coordinate list!
if coords:
    st.caption(f"Last Click: x={coords['x']}, y={coords['y']} -> {get_closest_province(coords['x'], coords['y'])}")