import numpy as np

import xml.etree.ElementTree as ET
from pathlib import Path

from sim.sim_launch import wsl_run

WORLDS_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\itsaerocraft\PX4-Autopilot\Tools\simulation\gz\worlds")

def write_world(wind_speed, wind_dir, name="flightstack"):

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


    tree.write(WORLDS_DIR / f"{name}.sdf") # write a NEW file and not overwrite the default file

    return name


# set_wind() written with AI assistance (Claude, Anthropic), Oct 2026.
def set_wind(wind_speed, wind_dir, world="flightstack"):
    """Change the wind in the running Gazebo world (used after takeoff).

    Same ENU convention as write_world: wind_dir in deg, 0 = toward east, 90 = toward north.
    Gazebo's WindEffects plugin listens on /world/<world>/wind and applies the new
    wind straight away; raises if gz rejects the message.
    """
    wind_dir_rad = np.radians(wind_dir)
    wind_x = wind_speed * np.cos(wind_dir_rad)
    wind_y = wind_speed * np.sin(wind_dir_rad)

    # {{ }} are literal braces inside the f-string; the single quotes keep bash from touching them
    msg = f"linear_velocity: {{x: {wind_x}, y: {wind_y}, z: 0}}, enable_wind: true"
    result = wsl_run(f"gz topic -t /world/{world}/wind -m gz.msgs.Wind -p '{msg}'")

    if result.returncode != 0:
        raise RuntimeError(f"gz topic failed to set wind: {result.stderr.strip()}")

