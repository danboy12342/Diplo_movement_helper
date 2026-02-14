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
if 'last_detected_province' not in st.session_state:
    st.session_state.last_detected_province = None
if 'last_coords' not in st.session_state:
    st.session_state.last_coords = None

game = st.session_state.game

# --- 2. MAP COORDINATES ---
# These coordinates are mapped to the "GuyWithCoolArt" style map you provided.
# If clicks are slightly off, you can tweak the numbers manually.
PROVINCE_CENTERS = {
    # ENGLAND
    "LON": (220, 305), "LVP": (200, 160), "EDI": (225, 110),
    "CLY": (190, 80),  "YOR": (230, 200), "WAL": (180, 280),

    # FRANCE
    "PAR": (240, 480), "BRE": (170, 450), "MAR": (260, 600),
    "PIC": (250, 420), "BUR": (290, 480), "GAS": (210, 560),

    # GERMANY
    "BER": (520, 390), "MUN": (460, 500), "KIE": (480, 340),
    "RUH": (400, 430), "PRU": (580, 350), "SIL": (550, 440),

    # ITALY
    "ROM": (430, 780), "VEN": (430, 680), "NAP": (470, 850),
    "PIE": (350, 640), "TUS": (400, 730), "APU": (500, 780),

    # AUSTRIA
    "VIE": (560, 590), "BUD": (630, 640), "TRI": (530, 690),
    "GAL": (680, 520), "TYR": (500, 580), "BOH": (520, 530),

    # TURKEY
    "CON": (850, 820), "ANK": (950, 800), "SMY": (930, 900),
    "SYR": (1050, 880), "ARM": (1100, 750),

    # RUSSIA
    "MOS": (900, 400), "SEV": (950, 600), "WAR": (680, 430),
    "STP": (850, 250), "UKR": (800, 530), "LVN": (700, 350),
    "FIN": (750, 200),

    # NEUTRALS
    "NOR": (500, 180), "SWE": (580, 220), "DEN": (470, 300),
    "HOL": (360, 350), "BEL": (320, 390), "SPA": (160, 680),
    "POR": (90, 650),  "TUN": (350, 950), "GRE": (670, 840),
    "SER": (640, 740), "BUL": (730, 760), "RUM": (750, 650),

    # SEAS (Water)
    "NTH": (350, 250), "ENG": (200, 350), "IRI": (120, 250),
    "NAO": (50, 150),  "NWG": (500, 50),  "BAR": (900, 50),
    "BAL": (600, 300), "BOT": (650, 200), "SKA": (550, 250),
    "HEL": (420, 300), "BLA": (900, 700), "AEG": (750, 920),
    "EAS": (900, 1000), "ION": (600, 950), "ADR": (520, 800),
    "TYS": (400, 850), "LYO": (300, 750), "WES": (250, 850),
    "MAO": (50, 550),  "NAF": (200, 950)
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
        # Show phase and detected province prominently
        col_phase, col_detected = st.columns(2)
        with col_phase:
            st.write(f"**Phase:** {game.phase}")
        with col_detected:
            if st.session_state.last_detected_province:
                # Get the province center for visual feedback
                prov_center = PROVINCE_CENTERS.get(st.session_state.last_detected_province, (0, 0))
                st.write(f"**Detected:** :blue-background[{st.session_state.last_detected_province}] @ ({prov_center[0]}, {prov_center[1]})")
        
        # This component renders the image and returns click coordinates
        # key="map" ensures it doesn't reload unnecessarily
        coords = streamlit_image_coordinates(map_path, key="map_click", width=800)

        # --- THE CLICK LOGIC ---
        if coords:
            x, y = coords['x'], coords['y']
            clicked_prov = get_closest_province(x, y)
            
            # Store the detected province for display
            st.session_state.last_detected_province = clicked_prov
            st.session_state.last_coords = (x, y)
            
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
    
    # Show detection status box
    if st.session_state.last_detected_province:
        with st.container(border=True):
            st.write("**Last Detection:**")
            st.metric(label="Province", value=st.session_state.last_detected_province)
            if st.session_state.last_coords:
                st.caption(f"Click coords: ({st.session_state.last_coords[0]}, {st.session_state.last_coords[1]})")
                actual_center = PROVINCE_CENTERS.get(st.session_state.last_detected_province, (0, 0))
                st.caption(f"Province center: ({actual_center[0]}, {actual_center[1]})")

    st.divider()

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
        st.session_state.last_detected_province = None
        st.session_state.last_coords = None
        st.rerun()

# --- 4. DEBUG INFO (Optional) ---
# Helps you build your coordinate list!
with st.expander("🔧 Debug Info", expanded=False):
    if st.session_state.last_coords and st.session_state.last_detected_province:
        st.write(f"**Last Click:** x={st.session_state.last_coords[0]}, y={st.session_state.last_coords[1]}")
        st.write(f"**Detected Province:** {st.session_state.last_detected_province}")
        st.write(f"**Province Center:** {PROVINCE_CENTERS.get(st.session_state.last_detected_province)}")
        
        # Show distance calculation
        actual_center = PROVINCE_CENTERS.get(st.session_state.last_detected_province, (0, 0))
        dist = distance.euclidean(st.session_state.last_coords, actual_center)
        st.write(f"**Distance from center:** {dist:.1f} pixels")