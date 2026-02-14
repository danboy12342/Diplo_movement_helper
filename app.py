import streamlit as st
from diplomacy import Game
from streamlit_image_coordinates import streamlit_image_coordinates
from scipy.spatial import distance
from PIL import Image, ImageDraw, ImageFont
import io

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
if 'order_type' not in st.session_state:
    st.session_state.order_type = "MOVE"  # MOVE, SUPPORT, CONVOY, HOLD
if 'last_detected_province' not in st.session_state:
    st.session_state.last_detected_province = None

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
    st.subheader("⚙️ Controls")
    
    # Order Type Selection
    order_type = st.radio(
        "Order Type:",
        ["MOVE", "SUPPORT", "CONVOY", "HOLD"],
        index=["MOVE", "SUPPORT", "CONVOY", "HOLD"].index(st.session_state.order_type)
    )
    st.session_state.order_type = order_type
    
    st.divider()
    
    # Display Active Selection
    if st.session_state.selected_unit:
        st.success(f"**Selected:** {st.session_state.selected_unit}")
        st.caption(f"Order type: {st.session_state.order_type}")
        
        if st.button("❌ Cancel Selection"):
            st.session_state.selected_unit = None
            st.rerun()
    else:
        st.info("Click a unit to select it")
    
    if st.session_state.last_detected_province:
        st.metric("Last Detected", st.session_state.last_detected_province)
    
    st.divider()
    
    st.subheader("📋 Current Orders")
    
    # Display Orders grouped by Power
    orders_exist = False
    for power_name in game.powers:
        orders = game.get_orders(power_name)
        if orders:
            orders_exist = True
            color = POWER_COLORS.get(power_name, '#808080')
            st.markdown(f"**{power_name}**")
            for order in orders:
                st.text(f"  • {order}")
    
    if not orders_exist:
        st.caption("No orders yet")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Process", type="primary", use_container_width=True):
            try:
                game.process()
                st.session_state.selected_unit = None
                st.success("Turn processed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.game = Game()
            st.session_state.selected_unit = None
            st.session_state.last_detected_province = None
            st.rerun()
    
    # Game Info
    st.divider()
    st.caption(f"**Phase:** {game.phase}")
    st.caption(f"**Year:** {game.get_current_phase().split()[1] if len(game.get_current_phase().split()) > 1 else 'N/A'}")

with col_map:
    st.write(f"**Current Phase:** {game.phase}")
    
    # Create map with units drawn on it
    try:
        map_with_units = draw_units_on_map("map.png")
        
        # Convert PIL image to bytes for streamlit
        buf = io.BytesIO()
        map_with_units.save(buf, format='PNG')
        byte_im = buf.getvalue()
        
        # Display the map and capture clicks
        coords = streamlit_image_coordinates(
            byte_im,
            key="map_interactive",
            width=800
        )
        
        # --- CLICK LOGIC ---
        if coords:
            # Get the image dimensions to scale coordinates
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
                
                # STATE MACHINE
                if st.session_state.selected_unit is None:
                    # SELECT UNIT
                    if clicked_unit:
                        st.session_state.selected_unit = clicked_unit
                        st.toast(f"✓ Selected: {clicked_unit}")
                        st.rerun()
                    else:
                        st.toast(f"No unit in {clicked_prov}")
                
                else:
                    # CREATE ORDER
                    selected_unit = st.session_state.selected_unit
                    
                    # Find which power owns the selected unit
                    unit_power = None
                    for power_name in game.powers:
                        power = game.get_power(power_name)
                        if selected_unit in power.units:
                            unit_power = power_name
                            break
                    
                    if not unit_power:
                        st.error("Could not find power for selected unit")
                        st.session_state.selected_unit = None
                    else:
                        order_str = None
                        
                        # Build order based on type
                        if st.session_state.order_type == "MOVE":
                            order_str = f"{selected_unit} - {clicked_prov}"
                        
                        elif st.session_state.order_type == "HOLD":
                            order_str = f"{selected_unit} H"
                        
                        elif st.session_state.order_type == "SUPPORT":
                            # Support requires another unit - check if one exists at clicked location
                            if clicked_unit:
                                # Support format: "A PAR S A MAR - BUR"
                                # We'll make it simple: support the unit to hold
                                order_str = f"{selected_unit} S {clicked_unit}"
                            else:
                                st.warning("Support requires a unit at target location")
                        
                        elif st.session_state.order_type == "CONVOY":
                            # Convoy is complex - simplified version
                            order_str = f"{selected_unit} C A ??? - {clicked_prov}"
                            st.warning("Convoy orders need manual editing - this is a placeholder")
                        
                        if order_str:
                            try:
                                # Get current orders and add new one
                                current_orders = list(game.get_orders(unit_power))
                                
                                # Remove any existing order for this unit
                                current_orders = [o for o in current_orders if not o.startswith(selected_unit)]
                                
                                # Add new order
                                current_orders.append(order_str)
                                
                                # Set all orders for this power
                                game.set_orders(unit_power, current_orders)
                                
                                st.toast(f"✓ Order: {order_str}")
                                st.session_state.selected_unit = None
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Invalid order: {e}")
                                st.session_state.selected_unit = None
    
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
    
    if st.session_state.last_detected_province:
        st.write(f"**Last Detected:** {st.session_state.last_detected_province}")
        st.write(f"**Province Center:** {PROVINCE_CENTERS.get(st.session_state.last_detected_province)}")