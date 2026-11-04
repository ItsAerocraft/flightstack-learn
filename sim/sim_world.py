import numpy as np

import xml.etree.ElementTree as ET
from pathlib import Path

from sim.sim_launch import wsl_run
from configs.config_params import GUST_INTENSITY


# paths into PX4 files (AI)
WORLDS_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\itsaerocraft\PX4-Autopilot\Tools\simulation\gz\worlds")
SERVER_CONFIG = Path(r"\\wsl.localhost\Ubuntu-24.04\home\itsaerocraft\PX4-Autopilot\src\modules\simulation\gz_bridge\server.config")

def write_world(wind_speed, wind_dir, name="flightstack", gust_scaled=0.0, surge_period=8.0, direction_swing_period=6.0):
    '''
    Writes a new Gazebo world file with a steady background wind and a
    gusting WindEffects plugin configured on top of it.

    Args:
        [wind_speed]: steady background wind magnitude (m s^-1).
        [wind_dir]: wind direction, ENU convention, 0 deg = toward east, 90 deg
            = toward north (deg).
        [name]: world name to write; output file is <name>.sdf.
        [gust_scaled]: standard deviation of the gust magnitude noise, as a
            fraction of wind_speed (unitless).
        [surge_period]: period of the sinusoidal gust magnitude surge (s).
        [direction_swing_period]: period of the sinusoidal gust direction
            swing (s).

    Returns:
        [name] of the world written, for use as the world argument to start_sim.

    Starts from the stock default.sdf (never modified), copies over any
    plugins from PX4's server.config other than WindEffects, then appends a
    freshly configured WindEffects plugin so gusting is reproducible from
    gz_seed.
    '''

    # retrieve stock sdf file
    stock_world_path = WORLDS_DIR / "default.sdf"
    tree = ET.parse(stock_world_path)
    root = tree.getroot()

    # find the root world in the sdf file
    world = root.find('world')

    wind_dir_rad = np.radians(wind_dir)
        
    wind_x = wind_speed * np.cos(wind_dir_rad)
    wind_y = wind_speed * np.sin(wind_dir_rad)
    wind_z = 0


    # change the attribute with set
    world.set('name', name)

    # create a new element called wind
    wind_element = ET.Element('wind')

    #create a new subelement of the element wind, called wind_components
    linear_velocity_subelement = ET.SubElement(wind_element, 'linear_velocity') 

    #XML reads from a string text, use dot notation
    linear_velocity_subelement.text = f"{wind_x} {wind_y} {wind_z}"

    #append the wind element and its subelements to the world file
    world.append(wind_element)

    try:
        server_tree = ET.parse(SERVER_CONFIG)
        server_root = server_tree.getroot()
        
        for plugin in server_root.findall(".//plugin"):
            # Skip the plugin whose name is gz::sim::systems::WindEffects, as we are changing them (AI)
            if plugin.get("name") == "gz::sim::systems::WindEffects":
                continue
        
            # Append the plugin to the world
            world.append(plugin)

    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Warning: Could not parse or find server config at {SERVER_CONFIG}: {e}")

    wind_effects = ET.SubElement(world, "plugin", {
        "filename": "gz-sim-wind-effects-system",
        "name": "gz::sim::systems::WindEffects"
    })

    # build the configured WindEffects with their respective subelements 
    # [AI directed me what to change, I wrote the change code] (AI)

    # force approximation scaling factor (drag k = 1)
    ET.SubElement(wind_effects, "force_approximation_scaling_factor").text = "1"
    
    # horizontal parent block
    horizontal = ET.SubElement(wind_effects, "horizontal")
    
    # magnitude Sub-block (surge tracking every 8 seconds + gust_scaled noise)
    magnitude = ET.SubElement(horizontal, "magnitude")
    ET.SubElement(magnitude, "time_for_rise").text = "1"
    
    mag_sin = ET.SubElement(magnitude, "sin")
    ET.SubElement(mag_sin, "amplitude_percent").text = str(GUST_INTENSITY)
    ET.SubElement(mag_sin, "period").text = str(surge_period)
    
    mag_noise = ET.SubElement(magnitude, "noise", {"type": "gaussian"})
    ET.SubElement(mag_noise, "mean").text = "0"
    ET.SubElement(mag_noise, "stddev").text = str(gust_scaled)
    
    # direction Sub-block
    direction = ET.SubElement(horizontal, "direction")
    ET.SubElement(direction, "time_for_rise").text = "1"
    
    dir_sin = ET.SubElement(direction, "sin")
    ET.SubElement(dir_sin, "amplitude").text = "15"
    ET.SubElement(dir_sin, "period").text = str(direction_swing_period)
    
    dir_noise = ET.SubElement(direction, "noise", {"type": "gaussian"})
    ET.SubElement(dir_noise, "mean").text = "0"
    ET.SubElement(dir_noise, "stddev").text = "2"


    tree.write(WORLDS_DIR / f"{name}.sdf") # write a NEW file and not overwrite the default file

    return name


# set_wind() written with AI assistance (Claude, Anthropic), Oct 2026.
def set_wind(wind_speed, wind_dir, world="flightstack"):
    '''
    Changes the steady wind in an already-running Gazebo world, for use after
    takeoff (e.g. from an on_airborne callback).

    Args:
        [wind_speed]: steady background wind magnitude (m s^-1).
        [wind_dir]: wind direction, same ENU convention as write_world, 0 deg
            = toward east, 90 deg = toward north (deg).
        [world]: name of the running world to target.

    Returns:
        None. Raises RuntimeError if the gz topic command is rejected.

    Publishes directly to the WindEffects plugin's /world/<world>/wind topic,
    which applies the new wind immediately rather than ramping it.
    '''
    wind_dir_rad = np.radians(wind_dir)
    wind_x = wind_speed * np.cos(wind_dir_rad)
    wind_y = wind_speed * np.sin(wind_dir_rad)

    # {{ }} are literal braces inside the f-string; the single quotes keep bash from touching them
    msg = f"linear_velocity: {{x: {wind_x}, y: {wind_y}, z: 0}}, enable_wind: true"
    result = wsl_run(f"gz topic -t /world/{world}/wind -m gz.msgs.Wind -p '{msg}'")

    if result.returncode != 0:
        raise RuntimeError(f"gz topic failed to set wind: {result.stderr.strip()}")

