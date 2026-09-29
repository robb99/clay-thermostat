# clay-thermostat 🌡️

Climate control CLI for Home Assistant. Control your thermostats from the command line.

## Features

- 🌡️ **Get current temperature** - View current and target temps
- 🎯 **Set target temperature** - Adjust heating/cooling setpoints
- 🔄 **Control HVAC modes** - Switch between heat, cool, auto, off
- 📋 **List climate entities** - See all thermostats in your home
- 💧 **View humidity** - Check current humidity levels
- 🔗 **Target specific thermostats** - Control by name or entity ID

## Requirements

- Python 3.7+
- Home Assistant instance
- Long-lived access token

## Installation

```bash
# Clone or copy to your tools directory
git clone https://github.com/robb99/clay-thermostat.git
cd clay-thermostat
pip install -r requirements.txt
```

## Configuration

### Option 1: Environment Variables

```bash
export HA_URL="http://192.168.1.135:8123"
export HA_TOKEN="your_long_lived_access_token"
```

### Option 2: Config File

Create `config.yaml`:

```yaml
ha_url: "http://192.168.1.135:8123"
ha_token: "your_long_lived_access_token"
```

### Getting a Home Assistant Token

1. Log into Home Assistant
2. Go to your profile (click your username)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "clay-thermostat")
6. Copy the token and add it to your config

## Usage

```bash
# List all climate/thermostat entities
python3 clay_thermostat.py list

# Show thermostat status (default)
python3 clay_thermostat.py status

# Get current temperatures
python3 clay_thermostat.py temp

# Set target temperature (all thermostats)
python3 clay_thermostat.py set 72

# Set temperature for specific thermostat
python3 clay_thermostat.py set 72 --entity living_room

# Set HVAC mode
python3 clay_thermostat.py mode cool
python3 clay_thermostat.py mode heat --entity bedroom
python3 clay_thermostat.py mode off

# List available HVAC modes
python3 clay_thermostat.py modes
```

## Examples

### Check Current Temps
```bash
$ python3 clay_thermostat.py temp
Living Room Thermostat: 72°F (target: 70°F)
Upstairs Thermostat: 74°F (target: 73°F)
```

### Set Temperature for Movie Night
```bash
python3 clay_thermostat.py set 68 --entity living_room
```

### Switch to Cooling
```bash
python3 clay_thermostat.py mode cool
```

### Turn Off HVAC
```bash
python3 clay_thermostat.py mode off
```

## Integration with Other Clay Tools

Combine with other clay tools for automated climate control:

```bash
# Set temperature based on weather
TEMPS=$(python3 tools/clay_weather.py --current-temp)
python3 clay_thermostat.py set $TEMPS

# Include in morning briefing
python3 clay_thermostat.py status
```

## HVAC Modes

| Mode | Description |
|------|-------------|
| off | System is off |
| heat | Heating only |
| cool | Cooling only |
| auto | Automatic (heat/cool) |
| dry | Dehumidification |
| fan_only | Fan only |

## Files

- `clay_thermostat.py` - Main CLI tool
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Related Tools

- [clay-scenes](https://github.com/robb99/clay-scenes) - Scene management
- [clay-sensor-monitor](https://github.com/robb99/clay-sensor-monitor) - Sensor monitoring
- [clay-weather](https://github.com/robb99/clay-weather) - Weather integration
