# Name: Test Tiles for House Placement
# Description: Displays valid tiles for house placement with color customization UI
# Usage: Stand where you want to place a house and run the script
# Author: Dozen
# Version: 3.0.0 - Enhanced with UI Color Customization
# Credits: Original concept by Reetus for ClassicAssist

import API
import time
import threading
import json
import os
from typing import List, Tuple, Optional, Set, Dict

# ===== Constants =====
class TileColors:
    """Constants for tile highlight hues."""
    INVALID = 38      # Red - Impassable or road
    BORDER = 1259    # Orange - Border issue  
    VALID = 64   # Green - Valid placement

# House sizes and their dimensions
HOUSE_SIZES: Dict[str, int] = {
    "7x7": 7,
    "29x29": 29
}

# Maximum allowed square size to prevent performance issues
MAX_SQUARE_SIZE = 24

# ===== Configuration =====
# Set remove_display to True to remove the display.
remove_display: bool = False

# Size of the square area to check around the player
square_size: int = 12

# Height tolerance for valid placement (z-height difference allowed)
height_tolerance: int = 2

# Time in seconds before the display is automatically removed
display_duration: int = 60

# Configuration file path
CONFIG_FILE = "Data/house_placement_config.json"

# Global tracker for marked tiles
marked_tiles_global = []

# Default color configuration
DEFAULT_COLORS = {
    "valid": 64,      # Green
    "invalid": 38,    # Red
    "border": 1259,   # Orange
    "7x7": 888,        # Yellow
    "29x29": 40       # Dark red (Castle)
}

# Roads list - graphic IDs that are impassable roads
Roads: Set[int] = {
    0x0071, 0x0078, 0x00E8, 0x00EB, 0x07AE, 0x07B1, 0x3FF4, 0x3FF8, 0x3FFB,
    0x0442, 0x0479, 0x0501, 0x0510, 0x0009, 0x0015, 0x0150, 0x015C, 0x170, 0x72, 0x73,
    0x74, 0x75, 0x76, 0x77, 0x79, 0x7A, 0x7C, 0x7D, 0x7E, 0x82, 0x83, 0x85, 0x86,
    0x87, 0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x16f
}

# ===== Configuration Management =====
class ConfigManager:
    """Manages color configuration persistence."""
    
    @staticmethod
    def load_colors() -> Dict[str, int]:
        """Load colors from config file or return defaults."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get("colors", DEFAULT_COLORS.copy())
        except Exception as e:
            API.SysMsg(f"Warning: Could not load config: {str(e)}")
        return DEFAULT_COLORS.copy()
    
    @staticmethod
    def save_colors(colors: Dict[str, int]) -> bool:
        """Save colors to config file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            config = {"colors": colors}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            API.SysMsg(f"Error: Could not save config: {str(e)}")
            return False

# ===== UI Functions =====
def show_color_customization_menu():
    """Show the color customization menu."""
    colors = ConfigManager.load_colors()
    
    gump = API.CreateGump(True, True)
    gump.SetRect(200, 200, 500, 550)
    gump.CenterXInViewPort()
    gump.CenterYInViewPort()
    
    # Background
    bg = API.CreateGumpColorBox(0.85, "#0a0a0a")
    bg.SetRect(0, 0, 500, 550)
    gump.Add(bg)
    
    # Title
    title = API.CreateGumpTTFLabel("House Placement Scanner", 26, "#FFD700", "alagard")
    title.SetRect(20, 15, 460, 40)
    gump.Add(title)
    
    # === SCAN OPTIONS ===
    scan_header = API.CreateGumpTTFLabel("Scan Options", 18, "#FFD700", "alagard")
    scan_header.SetRect(30, 70, 440, 30)
    gump.Add(scan_header)
    
    # Option 1: Tile Scan
    opt1_label = API.CreateGumpTTFLabel("1. Run Tile Scan", 16, "#FFFFFF", "alagard")
    opt1_label.SetRect(40, 110, 300, 25)
    gump.Add(opt1_label)
    opt1_desc = API.CreateGumpTTFLabel("Scan and mark individual tile validity", 12, "#AAAAAA", "alagard")
    opt1_desc.SetRect(40, 135, 300, 20)
    gump.Add(opt1_desc)
    
    opt1_btn = API.CreateSimpleButton("Start Scan", 140, 35)
    opt1_btn.SetRect(340, 110, 140, 35)
    gump.Add(opt1_btn)
    
    def on_scan_click():
        try:
            API.SysMsg("Starting tile scan...", 88)
            # Reload colors fresh from config
            fresh_colors = ConfigManager.load_colors()
            # Ensure defaults are set
            if "border" not in fresh_colors:
                fresh_colors["border"] = 1259
            if "valid" not in fresh_colors:
                fresh_colors["valid"] = 64
            if "invalid" not in fresh_colors:
                fresh_colors["invalid"] = 38
            # Run scan in background thread to avoid blocking UI
            scan_thread = threading.Thread(target=run_tile_scan, args=(fresh_colors,))
            scan_thread.daemon = True
            scan_thread.start()
        except Exception as e:
            API.SysMsg(f"Error starting scan: {str(e)}", 33)
    
    API.AddControlOnClick(opt1_btn, on_scan_click)
    
    # Option 2: Check 7x7
    opt2_label = API.CreateGumpTTFLabel("2. Check 7x7 House", 16, "#FFFFFF", "alagard")
    opt2_label.SetRect(40, 165, 300, 25)
    gump.Add(opt2_label)
    opt2_desc = API.CreateGumpTTFLabel("Find and highlight valid 7x7 placement", 12, "#AAAAAA", "alagard")
    opt2_desc.SetRect(40, 190, 300, 20)
    gump.Add(opt2_desc)
    
    opt2_btn = API.CreateSimpleButton("Check 7x7", 140, 35)
    opt2_btn.SetRect(340, 165, 140, 35)
    gump.Add(opt2_btn)
    
    def on_7x7_click():
        try:
            API.SysMsg("Checking for 7x7 placement...", 88)
            scan_thread = threading.Thread(target=check_house_size, args=(colors, 7, "7x7"))
            scan_thread.daemon = True
            scan_thread.start()
        except Exception as e:
            API.SysMsg(f"Error: {str(e)}", 33)
    
    API.AddControlOnClick(opt2_btn, on_7x7_click)
    
    # Option 3: Check Castle
    opt3_label = API.CreateGumpTTFLabel("3. Check Castle (29x29)", 16, "#FFFFFF", "alagard")
    opt3_label.SetRect(40, 220, 300, 25)
    gump.Add(opt3_label)
    opt3_desc = API.CreateGumpTTFLabel("Find and highlight valid castle placement", 12, "#AAAAAA", "alagard")
    opt3_desc.SetRect(40, 245, 300, 20)
    gump.Add(opt3_desc)
    
    opt3_btn = API.CreateSimpleButton("Check Castle", 140, 35)
    opt3_btn.SetRect(340, 220, 140, 35)
    gump.Add(opt3_btn)
    
    def on_castle_click():
        try:
            API.SysMsg("Checking for castle placement...", 88)
            scan_thread = threading.Thread(target=check_house_size, args=(colors, 29, "29x29"))
            scan_thread.daemon = True
            scan_thread.start()
        except Exception as e:
            API.SysMsg(f"Error: {str(e)}", 33)
    
    API.AddControlOnClick(opt3_btn, on_castle_click)
    
    # === UTILITIES ===
    util_header = API.CreateGumpTTFLabel("Utilities", 18, "#FFD700", "alagard")
    util_header.SetRect(30, 290, 440, 30)
    gump.Add(util_header)
    
    # Clear Markers
    clear_btn = API.CreateSimpleButton("Clear All Markers", 200, 35)
    clear_btn.SetRect(40, 330, 200, 35)
    gump.Add(clear_btn)
    
    def on_clear_click():
        clear_all_markers()
    
    API.AddControlOnClick(clear_btn, on_clear_click)
    
    # Customize Colors
    color_btn = API.CreateSimpleButton("Customize Colors", 200, 35)
    color_btn.SetRect(280, 330, 200, 35)
    gump.Add(color_btn)
    
    def on_color_click():
        show_manual_color_editor(colors)
    
    API.AddControlOnClick(color_btn, on_color_click)
    
    # === COLOR INFO ===
    info_header = API.CreateGumpTTFLabel("Current Color Settings", 16, "#FFD700", "alagard")
    info_header.SetRect(30, 390, 440, 25)
    gump.Add(info_header)
    
    color_info = API.CreateGumpTTFLabel(
        f"Valid: {colors.get('valid', 64)} | Invalid: {colors.get('invalid', 38)} | Border: {colors.get('border', 1259)}\n"
        f"7x7: {colors.get('7x7', 46)} | Castle: {colors.get('29x29', 40)}",
        12, "#CCCCCC", "alagard"
    )
    color_info.SetRect(40, 420, 440, 45)
    gump.Add(color_info)
    
    # Close button
    close_btn = API.CreateSimpleButton("Close", 150, 40)
    close_btn.SetRect(175, 490, 150, 40)
    gump.Add(close_btn)
    
    def on_close():
        clear_all_markers()
        try:
            if not gump.IsDisposed:
                gump.Dispose()
        except:
            pass
        API.Stop()
    
    API.AddControlOnClick(close_btn, on_close)
    API.AddControlOnDisposed(gump, lambda: (clear_all_markers(), API.Stop()))
    
    API.AddGump(gump)

def show_manual_color_editor(colors: Dict[str, int]):
    """Show manual color editor for individual tile types."""
    try:
        gump = API.CreateGump(True, True)
        gump.SetRect(150, 100, 600, 700)
        gump.CenterXInViewPort()
        
        # Background
        bg = API.CreateGumpColorBox(0.85, "#0f0f0f")
        bg.SetRect(0, 0, 600, 700)
        gump.Add(bg)
        
        # Title
        title = API.CreateGumpTTFLabel("Tile Color Editor", 22, "#FFD700", "alagard")
        title.SetRect(20, 15, 560, 30)
        gump.Add(title)
        
        # Instructions
        instr = API.CreateGumpTTFLabel(
            "Enter hue values (0-65535) for each tile type.",
            12, "#CCCCCC", "alagard"
        )
        instr.SetRect(20, 45, 560, 30)
        gump.Add(instr)
        
        # Scroll area with controls
        scroll = API.CreateGumpScrollArea(20, 80, 560, 550)
        gump.Add(scroll)
        
        text_controls = {}
        y = 0
        
        color_items = [
            ("Valid Tiles", "valid"),
            ("Invalid Tiles", "invalid"),
            ("Border Issues", "border"),
            ("7x7 Houses", "7x7"),
            ("29x29 Castles", "29x29")
        ]
        
        for label, key in color_items:
            # Label
            lbl = API.CreateGumpTTFLabel(label, 14, "#FFFFFF", "alagard")
            lbl.SetRect(10, y, 350, 25)
            scroll.Add(lbl)
            
            # Textbox for hue value
            current_hue = colors.get(key, DEFAULT_COLORS.get(key, 0))
            txt = API.CreateGumpTextBox(str(current_hue), 100, 25)
            txt.SetRect(380, y, 100, 25)
            txt.NumbersOnly = True
            text_controls[key] = txt
            scroll.Add(txt)
            
            # Info
            info = API.CreateGumpTTFLabel("(0-65535)", 11, "#888888", "alagard")
            info.SetRect(490, y, 70, 25)
            scroll.Add(info)
            
            y += 35
        
        # Save button
        save_btn = API.CreateSimpleButton("Save Colors", 150, 35)
        save_btn.SetRect(150, 650, 150, 35)
        gump.Add(save_btn)
        
        def on_save():
            try:
                new_colors = {}
                for key, ctrl in text_controls.items():
                    if ctrl.IsDisposed:
                        continue
                    text_val = ctrl.Text if ctrl.Text else "0"
                    val = int(text_val)
                    if 0 <= val <= 65535:
                        new_colors[key] = val
                    else:
                        API.SysMsg(f"Invalid hue for {key}: {val} (must be 0-65535)")
                        return
                
                if ConfigManager.save_colors(new_colors):
                    API.SysMsg("Colors saved successfully!")
                    if not gump.IsDisposed:
                        gump.Dispose()
            except Exception as e:
                API.SysMsg(f"Error saving colors: {str(e)}")
        
        API.AddControlOnClick(save_btn, on_save)
        
        # Cancel button
        cancel_btn = API.CreateSimpleButton("Cancel", 150, 35)
        cancel_btn.SetRect(320, 650, 150, 35)
        gump.Add(cancel_btn)
        
        def on_cancel():
            try:
                if not gump.IsDisposed:
                    gump.Dispose()
            except:
                pass
        
        API.AddControlOnClick(cancel_btn, on_cancel)
        
        API.AddGump(gump)
    except Exception as e:
        API.SysMsg(f"Error creating color editor: {str(e)}")

# ===== Core Tile Functions =====
def clear_all_markers():
    """Clear all marked tiles."""
    global marked_tiles_global
    try:
        count = len(marked_tiles_global)
        API.SysMsg(f"Clearing {count} marked tiles...", 88)
        for x, y in marked_tiles_global:
            try:
                remove_tile(x, y)
            except Exception as e:
                API.SysMsg(f"Error removing tile ({x},{y}): {str(e)}", 33)
        marked_tiles_global = []
        API.SysMsg(f"Cleared {count} markers.", 88)
    except Exception as e:
        API.SysMsg(f"Error clearing markers: {str(e)}", 33)

def is_valid_coordinate(x: int, y: int) -> bool:
    """Check if coordinates are within map bounds."""
    MIN_COORD = 0
    MAX_COORD = 7168
    return MIN_COORD <= x <= MAX_COORD and MIN_COORD <= y <= MAX_COORD

def get_landtile(x: int, y: int) -> Optional[object]:
    """Get LandTile object at (x, y) on current map."""
    try:
        return API.GetTile(x, y)
    except Exception:
        return None

def get_tile_data(x: int, y: int) -> Tuple[Optional[object], bool, bool]:
    """Cache tile, statics, and multi data to reduce API calls.
    
    Returns:
        Tuple of (tile, has_impassable, has_multi)
    """
    try:
        tile = get_landtile(x, y)
        statics = API.GetStaticsAt(x, y) or []
        
        # Check for multis in a small area around the coordinate
        multis = API.GetMultisInArea(x, y, x, y) or []
        
        has_impassable = any(
            getattr(s, "Impassible", False) or getattr(s, "IsImpassible", False) 
            for s in statics
        )
        
        # Check for multis
        has_multi = False
        if multis:
            if isinstance(multis, list):
                has_multi = len(multis) > 0
            else:
                has_multi = multis is not None
        
        return tile, has_impassable, has_multi
    except Exception as e:
        return None, False, False

def mark_tile(x: int, y: int, hue: int) -> None:
    """Mark a tile with a specific hue on the map."""
    try:
        API.MarkTile(x, y, hue)
    except Exception as e:
        pass

def remove_tile(x: int, y: int) -> None:
    """Remove a marked tile."""
    try:
        API.RemoveMarkedTile(x, y)
    except Exception as e:
        API.SysMsg(f"Error removing tile at ({x}, {y}): {str(e)}")

def is_valid_placement(x: int, y: int, player_z: int) -> Tuple[bool, bool]:
    """Check if a tile is valid for house placement.
    
    Returns:
        Tuple of (is_valid, is_border_issue)
    """
    if not is_valid_coordinate(x, y):
        return False, False
        
    tile, has_impassable, has_multi = get_tile_data(x, y)
    if not tile:
        return False, False
        
    z = getattr(tile, 'Z', 0)
    tile_id = getattr(tile, 'Graphic', None)
    
    # DEBUG: Log what we're checking
    debug_info = f"({x},{y}): z={z}, tile_id={tile_id}, impass={has_impassable}, multi={has_multi}"
    
    if tile_id and tile_id in Roads:
        # API.SysMsg(f"DEBUG {debug_info} -> INVALID (road)", 33)
        return False, False
        
    if has_impassable:
        # API.SysMsg(f"DEBUG {debug_info} -> INVALID (impassable)", 33)
        return False, False
        
    if has_multi:
        # API.SysMsg(f"DEBUG {debug_info} -> INVALID (has multi)", 33)
        return False, False
        
    if not (player_z - height_tolerance) <= z <= (player_z + height_tolerance):
        # API.SysMsg(f"DEBUG {debug_info} -> BORDER (z mismatch, player_z={player_z})", 33)
        return False, True
        
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if not is_valid_coordinate(nx, ny):
            return False, True
            
        adj_tile, adj_impassable, adj_multi = get_tile_data(nx, ny)
        
        # Check if adjacent tile has a multi (house buffer rule)
        if adj_multi:
            return False, True
        
        if adj_impassable:
            return False, True
            
        if adj_tile:
            adj_z = getattr(adj_tile, 'Z', 0)
            if abs(adj_z - z) > height_tolerance:
                return False, True
    
    # If we get here, tile is VALID
    # API.SysMsg(f"DEBUG {debug_info} -> VALID", 88)
    return True, False

def check_valid_house_area(px: int, py: int, pz: int, size: int) -> bool:
    """Check if a square area of given size is valid for house placement.
    
    Args:
        px, py: Top-left corner coordinates
        pz: Player Z coordinate
        size: Size of the square area to check
        
    Returns:
        True if entire area is valid for placement
    """
    valid_tiles = []
    invalid_tiles = []
    for x in range(px, px + size):
        for y in range(py, py + size):
            is_valid, is_border = is_valid_placement(x, y, pz)
            if not is_valid:
                # Found invalid tile, this area won't work
                invalid_tiles.append((x, y, is_border))
                if len(invalid_tiles) <= 3:  # Only log first 3 to avoid spam
                    API.SysMsg(f"  Tile ({x},{y}) INVALID (border={is_border})", 33)
                return False
            else:
                valid_tiles.append((x, y))
    
    # If we get here, all tiles were valid - THIS SHOULD NOT HAPPEN if no green tiles visible!
    API.SysMsg(f"WARNING: Found valid {size}x{size} at ({px},{py}) with {len(valid_tiles)} tiles", 88)
    API.SysMsg(f"  First 5 tiles: {valid_tiles[:5]}", 88)
    API.SysMsg(f"  Player Z: {pz}, checking first tile in detail...", 88)
    
    # Double-check the first tile
    first_x, first_y = valid_tiles[0]
    tile = get_landtile(first_x, first_y)
    if tile:
        z = getattr(tile, 'Z', 0)
        tile_id = getattr(tile, 'Graphic', None)
        API.SysMsg(f"  First tile ({first_x},{first_y}): z={z}, graphic={tile_id}", 88)
    
    return True

def run_tile_scan(colors: Dict[str, int]) -> None:
    """Run the basic tile validity scan without house checking."""
    global marked_tiles_global
    API.SysMsg("Starting tile scan...", 88)
    API.SysMsg(f"Using colors - Valid:{colors.get('valid')}, Invalid:{colors.get('invalid')}, Border:{colors.get('border')}", 88)
    marked_tiles = []
    try:
        API.SysMsg("Getting player info...", 88)
        player = API.Player
        if not player:
            API.SysMsg("Error: Could not get player information", 33)
            return
        
        API.SysMsg(f"Player at {player.X}, {player.Y}, {player.Z}", 88)
            
        px, py, pz = player.X, player.Y, player.Z
        API.SysMsg(f"Starting scan at {px},{py},{pz} with square_size={square_size}", 88)
        valid_count = 0
        invalid_count = 0
        border_count = 0
        
        # Track which tiles are part of valid house areas
        house_area_tiles = {}

        # First pass: Mark individual tile validity
        API.SysMsg("Marking individual tiles...", 88)
        for xx in range(-abs(square_size), square_size + 1):
            for yy in range(-abs(square_size), square_size + 1):
                x = px + xx
                y = py + yy
                
                if not is_valid_coordinate(x, y):
                    continue
                
                coord = (x, y)
                
                # Check individual tile validity
                is_valid, is_border = is_valid_placement(x, y, pz)
                
                if not is_valid:
                    if is_border:
                        border_color = colors.get("border", TileColors.BORDER)
                        mark_tile(x, y, border_color)
                        border_count += 1
                    else:
                        invalid_color = colors.get("invalid", TileColors.INVALID)
                        mark_tile(x, y, invalid_color)
                        invalid_count += 1
                else:
                    valid_color = colors.get("valid", TileColors.VALID)
                    mark_tile(x, y, valid_color)
                    valid_count += 1
                
                marked_tiles.append((x, y))
        
        API.SysMsg(f"Tiles marked: Valid={valid_count}, Invalid={invalid_count}, Border={border_count}", 88)
        
        # Store all marked tiles globally for cleanup
        marked_tiles_global = marked_tiles[:]

        total_tiles = valid_count + invalid_count + border_count
        API.SysMsg(f"Tile scan complete:")
        API.SysMsg(f"  Valid: {valid_count} | Invalid: {invalid_count} | Border: {border_count} | Total: {total_tiles}")
        API.SysMsg(f"Use 'Check 7x7' or 'Check Castle' to find house placements.")

    except Exception as e:
        API.SysMsg(f"Error in tile scan: {str(e)}", 33)
        for x, y in marked_tiles:
            remove_tile(x, y)

def check_house_size(colors: Dict[str, int], size: int, size_name: str) -> None:
    """Check for a single valid house placement of given size."""
    global marked_tiles_global
    marked_tiles = marked_tiles_global[:] if marked_tiles_global else []
    
    try:
        player = API.Player
        if not player:
            API.SysMsg("Error: Could not get player information", 33)
            return
        
        px, py, pz = player.X, player.Y, player.Z
        API.SysMsg(f"Searching for {size_name} placement at {px},{py},{pz}...", 88)
        found = False
        
        for xx in range(-abs(square_size), square_size + 1):
            if found:
                break
            for yy in range(-abs(square_size), square_size + 1):
                x = px + xx
                y = py + yy
                
                if not is_valid_coordinate(x, y):
                    continue
                
                # Check if this could be top-left of a valid house area
                if check_valid_house_area(x, y, pz, size):
                    house_color = colors.get(size_name, DEFAULT_COLORS.get(size_name, 46))  # Default to yellow (46)
                    API.SysMsg(f"DEBUG: check_valid_house_area returned TRUE for ({x},{y})", 88)
                    API.SysMsg(f"Painting {size_name} border at ({x},{y}) with color {house_color}...", 88)
                    # Paint only the border of this ONE area
                    border_count = 0
                    for hx in range(x, x + size):
                        for hy in range(y, y + size):
                            # Only paint border tiles (edges)
                            if hx == x or hx == x + size - 1 or hy == y or hy == y + size - 1:
                                try:
                                    mark_tile(hx, hy, house_color)
                                    border_count += 1
                                    # Add to marked tiles if not already tracked
                                    if (hx, hy) not in marked_tiles:
                                        marked_tiles.append((hx, hy))
                                except Exception as e:
                                    API.SysMsg(f"Error marking tile ({hx},{hy}): {str(e)}", 33)
                    API.SysMsg(f"Found {size_name} placement at ({x}, {y}), painted {border_count} border tiles with hue {house_color}", 88)
                    found = True
                    break
        
        if not found:
            API.SysMsg(f"No valid {size_name} placements found", 33)
        
        # Update global tracker
        marked_tiles_global = marked_tiles[:]

    except Exception as e:
        API.SysMsg(f"Error checking {size_name}: {str(e)}", 33)

def main() -> None:
    """Main function - show customization menu."""
    try:
        show_color_customization_menu()
        # Keep processing callbacks for UI interaction
        while True:
            try:
                API.ProcessCallbacks()
                time.sleep(0.1)
            except:
                break
    except Exception as e:
        API.SysMsg(f"Fatal error: {str(e)}")

# Run the script
main()
