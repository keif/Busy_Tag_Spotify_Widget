# BusyTag Config Examples

Reference configurations for the BusyTag device.

## Structure Overview

All configs must include these fields:
- `version`: Config version (use 3)
- `image`: Filename of image to display
- `show_after_drop`: Show image after file drop
- `allow_usb_msc`: Allow USB mass storage
- `allow_file_server`: Enable file server
- `disp_brightness`: Display brightness (0-100)
- `solid_color`: Object with `led_bits` and `color`
- `activate_pattern`: Enable/disable LED patterns
- `pattern_repeat`: How many times to repeat pattern (0 = infinite)
- `custom_pattern_arr`: Array of pattern objects

## LED Control

### led_bits
Bitfield for which LEDs to control (0-127):
- 127 = all 7 LEDs (binary: 1111111)
- 0 = no LEDs

### color
Hex color string without # prefix (e.g., "FF0000" for red, "EF932C" for orange)

## Examples

### default_structure.json
Default config structure from device reset (LEDs off)

### solid_color_orange.json
Solid orange color for all LEDs (matching Parliament album example)

### pattern_example.json
Example with custom LED pattern (cycling colors)
