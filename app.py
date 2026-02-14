import streamlit as st
from diplomacy import Game
from streamlit_image_coordinates import streamlit_image_coordinates
from scipy.spatial import distance
from PIL import Image, ImageDraw, ImageFont

# --- 1. SETUP & CONFIG ---
st.set_page_config(layout="wide", page_title="Diplomacy Order Manager")

# Initialize Game State
if 'game' not in st.session_state:
    st.session_state.game = Game()
    # Process to Spring 1901 to get starting positions
    st.session_state.game.set_orders('AUSTRIA', [])
    st.session_state.game.set_orders('ENGLAND', [])
    st.session_state.game.set_orders('FRANCE', [])
    st.session_state.game.set_orders('GERMANY', [])
    st.session_state.game.set_orders('ITALY', [])
    st.session_state.game.set_orders('RUSSIA', [])
    st.session_state.game.set_orders('TURKEY', [])

if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'selected_power' not in st.session_state:
    st.session_state.selected_power = None
if 'last_detected_province' not in st.session_state:
    st.session_state.last_detected_province = None
if 'map_version' not in st.session_state:
    st.session_state.map_version = 0

game = st.session_state.game

# --- 2. MAP COORDINATES ---
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

# Power colors for units
POWER_COLORS = {
    'AUSTRIA': '#FF0000',
    'ENGLAND': '#0000FF',
    'FRANCE': '#00BFFF',
    'GERMANY': '#000000',
    'ITALY': '#00FF00',
    'RUSSIA': '#FFFFFF',
    'TURKEY': '#FFFF00'
}

def get_closest_province(x, y):
    """Finds the province name closest to the clicked pixel."""
    coords = list(PROVINCE_CENTERS.values())
    names = list(PROVINCE_CENTERS.keys())
    
    if not coords:
        return None
    
    closest_index = distance.cdist([(x, y)], coords).argmin()
    return names[closest_index]

def parse_unit_string(unit_str):
    """Parse unit string like 'A PAR' or 'F LON' into type and location."""
    parts = unit_str.strip().split()
    if len(parts) >= 2:
        return parts[0], parts[1]  # type, location
    return None, None

def get_valid_destinations(unit_str, game):
    """Get all valid destinations for a unit."""
    try:
        unit_type, location = parse_unit_string(unit_str)
        if not location:
            return []
        
        # Get the map object from the game
        map_obj = game.map
        
        # Get adjacent provinces
        location_obj = map_obj.locs.get(location)
        if not location_obj:
            return []
        
        # Get all adjacent provinces
        adjacent = list(location_obj.abut)
        
        # Filter by unit type
        if unit_type == 'A':
            # Armies can only move to land provinces
            valid = [loc for loc in adjacent if not map_obj.locs.get(loc).is_sea()]
        else:  # Fleet
            # Fleets can move to coastal or sea provinces
            valid = [loc for loc in adjacent if map_obj.locs.get(loc).is_sea() or map_obj.locs.get(loc).is_coast()]
        
        return sorted(valid)
    except:
        return []

def get_supportable_units(unit_str, game, power_name):
    """Get all units that can be supported by this unit."""
    try:
        unit_type, location = parse_unit_string(unit_str)
        if not location:
            return []
        
        map_obj = game.map
        location_obj = map_obj.locs.get(location)
        if not location_obj:
            return []
        
        # Get adjacent provinces
        adjacent = list(location_obj.abut)
        
        supportable = []
        
        # Check all units in adjacent provinces
        for other_power_name in game.powers:
            other_power = game.get_power(other_power_name)
            for other_unit in other_power.units:
                other_type, other_loc = parse_unit_string(other_unit)
                if other_loc in adjacent:
                    supportable.append(other_unit)
        
        return supportable
    except:
        return []

def draw_units_on_map(base_map_path):
    """Draw all current units on the map."""
    # Load base map
    img = Image.open(base_map_path).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load a font, fall back to default if needed
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Get all units from all powers
    all_units = {}
    for power_name in game.powers:
        power = game.get_power(power_name)
        for unit in power.units:
            # unit is like "A PAR" or "F LON"
            unit_type, location = parse_unit_string(unit)
            if location and location in PROVINCE_CENTERS:
                all_units[unit] = {
                    'power': power_name,
                    'type': unit_type,
                    'location': location,
                    'coords': PROVINCE_CENTERS[location]
                }
    
    # Draw each unit
    for unit_str, unit_info in all_units.items():
        x, y = unit_info['coords']
        color = POWER_COLORS.get(unit_info['power'], '#808080')
        
        # Draw circle for unit
        radius = 18
        
        # Outline
        draw.ellipse([x-radius-2, y-radius-2, x+radius+2, y+radius+2], 
                     fill='#000000', outline='#000000')
        
        # Main circle
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                     fill=color, outline='#000000', width=2)
        
        # Draw unit type (A or F)
        unit_label = unit_info['type']
        
        # Get text size for centering
        bbox = draw.textbbox((0, 0), unit_label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw text with black outline for visibility
        outline_color = '#FFFFFF' if unit_info['power'] == 'GERMANY' else '#000000'
        text_color = '#000000' if unit_info['power'] in ['RUSSIA', 'TURKEY'] else '#FFFFFF'
        
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x != 0 or offset_y != 0:
                    draw.text((x - text_width//2 + offset_x, y - text_height//2 + offset_y), 
                             unit_label, font=font, fill=outline_color)
        
        draw.text((x - text_width//2, y - text_height//2), 
                 unit_label, font=font, fill=text_color)
    
    # Highlight selected unit
    if st.session_state.selected_unit and st.session_state.selected_unit in all_units:
        unit_info = all_units[st.session_state.selected_unit]
        x, y = unit_info['coords']
        # Draw selection ring
        for i in range(3):
            draw.ellipse([x-25-i, y-25-i, x+25+i, y+25+i], 
                        outline='#FFD700', width=2)
    
    # Combine overlay with base image
    combined = Image.alpha_composite(img, overlay)
    return combined.convert('RGB')

# --- 3. UI LAYOUT ---
st.title("🗺️ Diplomacy: Interactive Order Manager")

col_map, col_sidebar = st.columns([3, 1])

with col_sidebar:
    st.subheader("⚙️ Order Panel")
    
    # Display Active Selection and Order Options
    if st.session_state.selected_unit:
        st.success(f"**Selected:** {st.session_state.selected_unit}")
        st.caption(f"Power: {st.session_state.selected_power}")
        
        st.divider()
        
        # Get possible actions
        destinations = get_valid_destinations(st.session_state.selected_unit, game)
        supportable = get_supportable_units(st.session_state.selected_unit, game, st.session_state.selected_power)
        
        # Order type selection
        order_action = st.radio(
            "Choose action:",
            ["Hold", "Move", "Support", "Convoy"],
            key="order_action"
        )
        
        order_to_create = None
        
        if order_action == "Hold":
            st.info("Unit will hold position")
            if st.button("✓ Confirm Hold Order", type="primary", use_container_width=True):
                order_to_create = f"{st.session_state.selected_unit} H"
        
        elif order_action == "Move":
            if destinations:
                dest = st.selectbox(
                    "Move to:",
                    destinations,
                    key="move_dest"
                )
                if st.button("✓ Confirm Move Order", type="primary", use_container_width=True):
                    order_to_create = f"{st.session_state.selected_unit} - {dest}"
            else:
                st.warning("No valid destinations available")
        
        elif order_action == "Support":
            if supportable:
                support_unit = st.selectbox(
                    "Support unit:",
                    supportable,
                    key="support_unit"
                )
                
                # Get destinations for the supported unit
                support_destinations = get_valid_destinations(support_unit, game)
                
                support_action = st.radio(
                    "Support to:",
                    ["Hold position"] + [f"Move to {d}" for d in support_destinations],
                    key="support_action"
                )
                
                if st.button("✓ Confirm Support Order", type="primary", use_container_width=True):
                    if support_action == "Hold position":
                        order_to_create = f"{st.session_state.selected_unit} S {support_unit}"
                    else:
                        # Extract destination from "Move to XXX"
                        dest = support_action.replace("Move to ", "")
                        order_to_create = f"{st.session_state.selected_unit} S {support_unit} - {dest}"
            else:
                st.warning("No units available to support")
        
        elif order_action == "Convoy":
            st.warning("Convoy orders are complex - you may need to create them manually")
            # Simplified convoy interface
            unit_type, location = parse_unit_string(st.session_state.selected_unit)
            if unit_type == 'F':
                st.info("Select army to convoy and destination")
                # This would need more complex logic
            else:
                st.error("Only fleets can convoy")
        
        # Execute order if created
        if order_to_create:
            try:
                # Get current orders and add new one
                current_orders = list(game.get_orders(st.session_state.selected_power))
                
                # Remove any existing order for this unit
                current_orders = [o for o in current_orders if not o.startswith(st.session_state.selected_unit)]
                
                # Add new order
                current_orders.append(order_to_create)
                
                # Set all orders for this power
                game.set_orders(st.session_state.selected_power, current_orders)
                
                st.session_state.map_version += 1
                st.toast(f"✓ Order created: {order_to_create}")
                st.session_state.selected_unit = None
                st.session_state.selected_power = None
                st.rerun()
                
            except Exception as e:
                st.error(f"Invalid order: {e}")
                st.session_state.selected_unit = None
                st.session_state.selected_power = None
        
        st.divider()
        
        if st.button("❌ Cancel Selection", use_container_width=True):
            st.session_state.selected_unit = None
            st.session_state.selected_power = None
            st.rerun()
    
    else:
        st.info("👆 Click a unit on the map to select it")
    
    if st.session_state.last_detected_province:
        st.caption(f"Hovering: {st.session_state.last_detected_province}")
    
    st.divider()
    
    st.subheader("📋 Current Orders")
    
    # Display Orders grouped by Power
    orders_exist = False
    for power_name in game.powers:
        orders = game.get_orders(power_name)
        if orders:
            orders_exist = True
            with st.expander(f"**{power_name}**", expanded=False):
                for order in orders:
                    col_order, col_delete = st.columns([4, 1])
                    with col_order:
                        st.text(f"{order}")
                    with col_delete:
                        if st.button("🗑️", key=f"del_{power_name}_{order}"):
                            current_orders = list(game.get_orders(power_name))
                            current_orders.remove(order)
                            game.set_orders(power_name, current_orders)
                            st.session_state.map_version += 1
                            st.rerun()
    
    if not orders_exist:
        st.caption("No orders yet")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Process", type="primary", use_container_width=True):
            try:
                game.process()
                st.session_state.selected_unit = None
                st.session_state.selected_power = None
                st.session_state.map_version += 1
                st.success("Turn processed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.game = Game()
            st.session_state.selected_unit = None
            st.session_state.selected_power = None
            st.session_state.last_detected_province = None
            st.session_state.map_version = 0
            st.rerun()
    
    # Game Info
    st.divider()
    st.caption(f"**Phase:** {game.phase}")

with col_map:
    st.write(f"**Current Phase:** {game.phase}")
    
    # Create map with units drawn on it
    try:
        map_with_units = draw_units_on_map("map.png")
        
        # Save to temporary file with version to force refresh
        temp_map_path = f"temp_map_v{st.session_state.map_version}.png"
        map_with_units.save(temp_map_path)
        
        # Display the map and capture clicks
        coords = streamlit_image_coordinates(
            temp_map_path,
            key="map_interactive",
            width=800
        )
        
        # --- CLICK LOGIC ---
        if coords:
            # Scale coordinates from display size to original size
            img_width = map_with_units.width
            display_width = 800
            scale = img_width / display_width
            
            x = int(coords['x'] * scale)
            y = int(coords['y'] * scale)
            
            clicked_prov = get_closest_province(x, y)
            st.session_state.last_detected_province = clicked_prov
            
            if clicked_prov:
                # Find which unit (if any) is in clicked province
                clicked_unit = None
                clicked_power = None
                
                for power_name in game.powers:
                    power = game.get_power(power_name)
                    for unit in power.units:
                        unit_type, location = parse_unit_string(unit)
                        if location == clicked_prov:
                            clicked_unit = unit
                            clicked_power = power_name
                            break
                    if clicked_unit:
                        break
                
                # SELECT UNIT
                if clicked_unit:
                    st.session_state.selected_unit = clicked_unit
                    st.session_state.selected_power = clicked_power
                    st.toast(f"✓ Selected: {clicked_unit}")
                    st.rerun()
                else:
                    # Clicked on empty province - deselect if something was selected
                    if st.session_state.selected_unit:
                        st.session_state.selected_unit = None
                        st.session_state.selected_power = None
                        st.toast(f"Deselected")
                        st.rerun()
    
    except FileNotFoundError:
        st.error("⚠️ map.png not found! Please add the map image to the same directory as this script.")
    except Exception as e:
        st.error(f"Error rendering map: {e}")
        import traceback
        st.code(traceback.format_exc())

# Debug expander
with st.expander("🔧 Debug Info"):
    st.write("**All Units:**")
    for power_name in game.powers:
        power = game.get_power(power_name)
        if power.units:
            st.write(f"{power_name}: {list(power.units)}")