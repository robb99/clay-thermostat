#!/usr/bin/env python3
"""
clay-thermostat - Climate control CLI for Home Assistant

A CLI tool to control thermostats via Home Assistant.
Allows getting current temperature, setting target temperature,
changing HVAC modes, and more.

Usage:
    python3 clay_thermostat.py status              # Show all thermostats
    python3 clay_thermostat.py temp                 # Get current temps
    python3 clay_thermostat.py set 72              # Set target temp (all)
    python3 clay_thermostat.py set 72 --room living_room  # Set specific
    python3 clay_thermostat.py mode cool           # Set mode
    python3 clay_thermostat.py modes               # List available modes
    python3 clay_thermostat.py list               # List all climate entities
"""

import argparse
import os
import sys
import json
import requests
from typing import Optional, List, Dict, Any

# Configuration
HA_URL = os.environ.get("HA_URL", "http://192.168.1.135:8123")
HA_TOKEN = os.environ.get("HA_TOKEN")

CONFIG_FILE = "config.yaml"


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment."""
    config = {"ha_url": HA_URL, "ha_token": HA_TOKEN}
    
    # Try to load from config file
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)
        except ImportError:
            pass
    
    # Environment variables override config file
    if os.environ.get("HA_URL"):
        config["ha_url"] = os.environ.get("HA_URL")
    if os.environ.get("HA_TOKEN"):
        config["ha_token"] = os.environ.get("HA_TOKEN")
    
    return config


def get_climate_entities(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all climate entities from Home Assistant."""
    if not config.get("ha_token"):
        print("Error: HA_TOKEN not configured. Set HA_TOKEN env var or config.")
        sys.exit(1)
    
    url = f"{config['ha_url']}/api/states"
    headers = {
        "Authorization": f"Bearer {config['ha_token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        states = response.json()
        
        # Filter for climate entities
        climate_entities = [
            state for state in states 
            if state["entity_id"].startswith("climate.")
        ]
        return climate_entities
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Home Assistant: {e}")
        sys.exit(1)


def get_thermostat_state(entity_id: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get detailed state for a specific thermostat."""
    if not config.get("ha_token"):
        return None
    
    url = f"{config['ha_url']}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {config['ha_token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def set_temperature(entity_id: str, temperature: float, config: Dict[str, Any]) -> bool:
    """Set target temperature for a thermostat."""
    if not config.get("ha_token"):
        print("Error: HA_TOKEN not configured")
        return False
    
    url = f"{config['ha_url']}/api/services/climate/set_temperature"
    headers = {
        "Authorization": f"Bearer {config['ha_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "entity_id": entity_id,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error setting temperature: {e}")
        return False


def set_hvac_mode(entity_id: str, mode: str, config: Dict[str, Any]) -> bool:
    """Set HVAC mode for a thermostat."""
    if not config.get("ha_token"):
        print("Error: HA_TOKEN not configured")
        return False
    
    # Validate mode
    valid_modes = ["off", "heat", "cool", "auto", "dry", "fan_only"]
    mode = mode.lower()
    if mode not in valid_modes:
        print(f"Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        return False
    
    url = f"{config['ha_url']}/api/services/climate/set_hvac_mode"
    headers = {
        "Authorization": f"Bearer {config['ha_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "entity_id": entity_id,
        "hvac_mode": mode
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error setting HVAC mode: {e}")
        return False


def format_temperature(temp: float) -> str:
    """Format temperature with degree symbol."""
    return f"{temp}°F"


def cmd_list(args, config: Dict[str, Any]) -> None:
    """List all climate/thermostat entities."""
    entities = get_climate_entities(config)
    
    if not entities:
        print("No climate entities found in Home Assistant.")
        return
    
    print("🏠 Climate Entities in Home Assistant")
    print("=" * 50)
    
    for entity in entities:
        entity_id = entity["entity_id"]
        state = entity["state"]
        attrs = entity.get("attributes", {})
        
        # Extract relevant info
        current_temp = attrs.get("current_temperature", "N/A")
        target_temp = attrs.get("temperature", "N/A")
        hvac_mode = attrs.get("hvac_mode", "N/A")
        humidity = attrs.get("current_humidity", None)
        friendly_name = attrs.get("friendly_name", entity_id)
        
        # Format output
        temp_str = format_temperature(current_temp) if current_temp != "N/A" else "N/A"
        target_str = format_temperature(target_temp) if target_temp != "N/A" else "N/A"
        
        print(f"\n{friendly_name}")
        print(f"  Entity: {entity_id}")
        print(f"  State: {state}")
        print(f"  Temperature: {temp_str} → {target_str}")
        print(f"  Mode: {hvac_mode}")
        if humidity:
            print(f"  Humidity: {humidity}%")


def cmd_status(args, config: Dict[str, Any]) -> None:
    """Show status of all thermostats."""
    entities = get_climate_entities(config)
    
    if not entities:
        print("No climate entities found.")
        return
    
    print("🌡️  Thermostat Status")
    print("-" * 40)
    
    for entity in entities:
        entity_id = entity["entity_id"]
        state = entity["state"]
        attrs = entity.get("attributes", {})
        
        current = attrs.get("current_temperature", "-")
        target = attrs.get("temperature", "-")
        mode = attrs.get("hvac_mode", "-")
        
        if current != "-":
            current = format_temperature(current)
        if target != "-":
            target = format_temperature(target)
        
        friendly = attrs.get("friendly_name", entity_id)
        print(f"{friendly}: {current} → {target} [{mode}]")


def cmd_temp(args, config: Dict[str, Any]) -> None:
    """Get current temperatures."""
    entities = get_climate_entities(config)
    
    if not entities:
        print("No climate entities found.")
        return
    
    for entity in entities:
        entity_id = entity["entity_id"]
        attrs = entity.get("attributes", {})
        
        current = attrs.get("current_temperature", "N/A")
        target = attrs.get("temperature", "N/A")
        
        if current != "N/A":
            current = format_temperature(current)
        if target != "N/A":
            target = format_temperature(target)
        
        friendly = attrs.get("friendly_name", entity_id)
        
        if args.json:
            print(json.dumps({
                "entity_id": entity_id,
                "friendly_name": friendly,
                "current_temperature": current,
                "target_temperature": target,
                "state": entity["state"]
            }))
        else:
            print(f"{friendly}: {current} (target: {target})")


def cmd_set(args, config: Dict[str, Any]) -> None:
    """Set target temperature."""
    entities = get_climate_entities(config)
    
    if not entities:
        print("No climate entities found.")
        return
    
    # Determine which entity(s) to control
    target_entities = []
    
    if args.entity:
        # Find specific entity
        for entity in entities:
            entity_id = entity["entity_id"]
            attrs = entity.get("attributes", {})
            friendly = attrs.get("friendly_name", entity_id).lower()
            
            if args.entity.lower() in friendly or args.entity.lower() in entity_id:
                target_entities.append(entity_id)
                break
        
        if not target_entities:
            print(f"Entity not found: {args.entity}")
            print("Use 'list' command to see available entities.")
            return
    else:
        # Use first entity or all
        if len(entities) == 1:
            target_entities = [entities[0]["entity_id"]]
        else:
            # Default to first climate entity
            target_entities = [entities[0]["entity_id"]]
    
    # Set temperature
    temperature = args.temperature
    
    for entity_id in target_entities:
        success = set_temperature(entity_id, temperature, config)
        if success:
            entity = next((e for e in entities if e["entity_id"] == entity_id), None)
            friendly = entity.get("attributes", {}).get("friendly_name", entity_id) if entity else entity_id
            print(f"✅ Set {friendly} to {format_temperature(temperature)}")
        else:
            print(f"❌ Failed to set temperature for {entity_id}")


def cmd_mode(args, config: Dict[str, Any]) -> None:
    """Set HVAC mode."""
    entities = get_climate_entities(config)
    
    if not entities:
        print("No climate entities found.")
        return
    
    mode = args.mode
    
    # Determine which entity(s) to control
    if args.entity:
        target_entities = []
        for entity in entities:
            entity_id = entity["entity_id"]
            attrs = entity.get("attributes", {})
            friendly = attrs.get("friendly_name", entity_id).lower()
            
            if args.entity.lower() in friendly or args.entity.lower() in entity_id:
                target_entities.append(entity_id)
                break
        
        if not target_entities:
            print(f"Entity not found: {args.entity}")
            return
    else:
        # Use first entity
        target_entities = [entities[0]["entity_id"]]
    
    # Set mode
    for entity_id in target_entities:
        success = set_hvac_mode(entity_id, mode, config)
        if success:
            entity = next((e for e in entities if e["entity_id"] == entity_id), None)
            friendly = entity.get("attributes", {}).get("friendly_name", entity_id) if entity else entity_id
            print(f"✅ Set {friendly} to {mode} mode")
        else:
            print(f"❌ Failed to set mode for {entity_id}")


def cmd_modes(args, config: Dict[str, Any]) -> None:
    """List available HVAC modes."""
    print("Available HVAC Modes:")
    print("  off     - System is off")
    print("  heat    - Heating only")
    print("  cool    - Cooling only")
    print("  auto    - Automatic (heat/cool)")
    print("  dry     - Dehumidification")
    print("  fan_only - Fan only, no heating/cooling")


def main():
    parser = argparse.ArgumentParser(
        description="Climate control CLI for Home Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all climate entities")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show thermostat status")
    
    # temp command
    temp_parser = subparsers.add_parser("temp", help="Get current temperatures")
    temp_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # set command
    set_parser = subparsers.add_parser("set", help="Set target temperature")
    set_parser.add_argument("temperature", type=float, help="Target temperature")
    set_parser.add_argument("--entity", "-e", help="Thermostat entity ID or name")
    
    # mode command
    mode_parser = subparsers.add_parser("mode", help="Set HVAC mode")
    mode_parser.add_argument("mode", help="HVAC mode (off/heat/cool/auto/dry/fan_only)")
    mode_parser.add_argument("--entity", "-e", help="Thermostat entity ID or name")
    
    # modes command
    modes_parser = subparsers.add_parser("modes", help="List available HVAC modes")
    
    args = parser.parse_args()
    config = load_config()
    
    if args.command == "list":
        cmd_list(args, config)
    elif args.command == "status":
        cmd_status(args, config)
    elif args.command == "temp":
        cmd_temp(args, config)
    elif args.command == "set":
        cmd_set(args, config)
    elif args.command == "mode":
        cmd_mode(args, config)
    elif args.command == "modes":
        cmd_modes(args, config)
    else:
        # Default to status
        cmd_status(args, config)


if __name__ == "__main__":
    main()
