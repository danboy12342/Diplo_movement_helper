import streamlit as st
from diplomacy import Game
from PIL import Image, ImageDraw, ImageFont

# --- SETUP & CONFIG ---
st.set_page_config(layout="wide", page_title="Diplomacy Order Entry")

# Initialize Game State
if 'game' not in st.session_state:
    st.session_state.game = Game()
    # Initialize all powers to get starting positions
    for power in ['AUSTRIA', 'ENGLAND', 'FRANCE', 'GERMANY', 'ITALY', 'RUSSIA', 'TURKEY']:
        st.session_state.game.set_orders(power, [])

if 'order_inputs' not in st.session_state:
    st.session_state.order_inputs = {power: "" for power in ['AUSTRIA', 'ENGLAND', 'FRANCE', 'GERMANY', 'ITALY', 'RUSSIA', 'TURKEY']}

game = st.session_state.game

# --- MAP COORDINATES ---
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

# Power colors
POWER_COLORS = {
    'AUSTRIA': '#FF0000',
    'ENGLAND': '#0000FF',
    'FRANCE': '#00BFFF',
    'GERMANY': '#000000',
    'ITALY': '#00FF00',
    'RUSSIA': '#FFFFFF',
    'TURKEY': '#FFFF00'
}

def parse_unit_string(unit_str):
    """Parse unit string like 'A PAR' or 'F LON' into type and location."""
    parts = unit_str.strip().split()
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None

def draw_units_on_map(base_map_path="map.png"):
    """Draw all current units on the map."""
    img = Image.open(base_map_path).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Get all units
    for power_name in game.powers:
        power = game.get_power(power_name)
        color = POWER_COLORS.get(power_name, '#808080')
        
        for unit in power.units:
            unit_type, location = parse_unit_string(unit)
            if location and location in PROVINCE_CENTERS:
                x, y = PROVINCE_CENTERS[location]
                
                # Draw unit circle
                radius = 18
                draw.ellipse([x-radius-2, y-radius-2, x+radius+2, y+radius+2], 
                           fill='#000000', outline='#000000')
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill=color, outline='#000000', width=2)
                
                # Draw unit type
                bbox = draw.textbbox((0, 0), unit_type, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                outline_color = '#FFFFFF' if power_name == 'GERMANY' else '#000000'
                text_color = '#000000' if power_name in ['RUSSIA', 'TURKEY'] else '#FFFFFF'
                
                # Text outline
                for ox in [-1, 0, 1]:
                    for oy in [-1, 0, 1]:
                        if ox != 0 or oy != 0:
                            draw.text((x - text_width//2 + ox, y - text_height//2 + oy), 
                                    unit_type, font=font, fill=outline_color)
                
                draw.text((x - text_width//2, y - text_height//2), 
                         unit_type, font=font, fill=text_color)
    
    combined = Image.alpha_composite(img, overlay)
    return combined.convert('RGB')

# --- UI LAYOUT ---
st.title("🗺️ Diplomacy: Manual Order Entry")

col_map, col_orders = st.columns([3, 2])

with col_map:
    st.subheader(f"Current Board - {game.phase}")
    
    try:
        map_with_units = draw_units_on_map()
        st.image(map_with_units, use_container_width=True)
    except FileNotFoundError:
        st.error("⚠️ map.png not found! Please add the map image to the same directory.")
    except Exception as e:
        st.error(f"Error rendering map: {e}")

with col_orders:
    st.subheader("📝 Enter Orders")
    
    st.caption("Enter one order per line. Examples:")
    st.code("""A PAR - BUR
F LON - NTH
A MUN S A BER - SIL
A ROM H""", language=None)
    
    tabs = st.tabs(["🔴 Austria", "🔵 England", "🟦 France", "⚫ Germany", "🟢 Italy", "⚪ Russia", "🟡 Turkey"])
    
    power_names = ['AUSTRIA', 'ENGLAND', 'FRANCE', 'GERMANY', 'ITALY', 'RUSSIA', 'TURKEY']
    
    for i, (tab, power) in enumerate(zip(tabs, power_names)):
        with tab:
            # Show current units
            power_obj = game.get_power(power)
            if power_obj.units:
                with st.expander("📍 Current Units", expanded=True):
                    for unit in sorted(power_obj.units):
                        st.text(f"  {unit}")
            
            # Order input
            current_orders = game.get_orders(power)
            default_text = "\n".join(current_orders) if current_orders else ""
            
            orders_text = st.text_area(
                f"Orders for {power}:",
                value=st.session_state.order_inputs.get(power, default_text),
                height=150,
                key=f"orders_{power}",
                placeholder="Enter orders, one per line..."
            )
            
            st.session_state.order_inputs[power] = orders_text
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✓ Submit Orders", key=f"submit_{power}", use_container_width=True):
                    orders_list = [line.strip() for line in orders_text.split('\n') if line.strip()]
                    try:
                        game.set_orders(power, orders_list)
                        st.success(f"✓ {len(orders_list)} orders submitted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col2:
                if st.button(f"Clear", key=f"clear_{power}", use_container_width=True):
                    st.session_state.order_inputs[power] = ""
                    game.set_orders(power, [])
                    st.rerun()
    
    st.divider()
    
    # Process controls
    st.subheader("⚙️ Game Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Process Turn", type="primary", use_container_width=True):
            try:
                # Show what happened
                with st.spinner("Processing turn..."):
                    game.process()
                    st.success(f"✓ Turn processed! Now: {game.phase}")
                    # Clear order inputs for next turn
                    st.session_state.order_inputs = {p: "" for p in power_names}
                    st.rerun()
            except Exception as e:
                st.error(f"Error processing: {e}")
    
    with col2:
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.game = Game()
            st.session_state.order_inputs = {p: "" for p in power_names}
            for power in power_names:
                st.session_state.game.set_orders(power, [])
            st.rerun()
    
    # Show all submitted orders
    st.divider()
    st.subheader("📋 Submitted Orders")
    
    all_orders = {}
    for power in power_names:
        orders = game.get_orders(power)
        if orders:
            all_orders[power] = orders
    
    if all_orders:
        for power, orders in all_orders.items():
            with st.expander(f"{power} ({len(orders)} orders)", expanded=False):
                for order in orders:
                    st.text(f"  • {order}")
    else:
        st.info("No orders submitted yet")

# Debug section
with st.expander("🔧 Debug Info"):
    st.write(f"**Phase:** {game.phase}")
    st.write("**All Units:**")
    for power in power_names:
        power_obj = game.get_power(power)
        if power_obj.units:
            st.write(f"**{power}:** {', '.join(sorted(power_obj.units))}")