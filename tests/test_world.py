import pytest
import xml.etree.ElementTree as ET
from pathlib import Path


WORLDS_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\itsaerocraft\PX4-Autopilot\Tools\simulation\gz\worlds")

from sim.sim_world import write_world

def test_write_world_wind_generation():
    test_speed = 3.0
    test_dir_deg = 90.0
    test_world_name = "testing_world"
    
    write_world(test_speed, test_dir_deg, test_world_name)
    
    generated_world_path = WORLDS_DIR / f"{test_world_name}.sdf"
    tree = ET.parse(generated_world_path)
    root = tree.getroot()
    
    world = root.find("world")

    # verify world name is indeed test_world_name and not default
    assert world.get("name") == test_world_name
    
    linear_velocity_text = root.find(".//world/wind/linear_velocity").text
    
    # Convert the string for three components into their respective ones
    float_components = [float(val) for val in linear_velocity_text.split()]
    
    # x, y, z (cos, sin, 0)
    assert float_components[0] == pytest.approx(0.0, abs=1e-9)
    assert float_components[1] == pytest.approx(test_speed, abs=1e-9)
    assert float_components[2] == pytest.approx(0.0, abs=1e-9)


def test_stock_world_is_unchanged():
    stock_world_path = WORLDS_DIR / "default.sdf"
    
    tree = ET.parse(stock_world_path)
    root = tree.getroot()
    
    assert root.find("world/wind") is None

def test_write_world_plugin_and_gust_verification():
    test_speed = 3.0
    test_dir_deg = 90.0
    test_world_name = "testing_world"
    test_gust_scaled = 0.45
    
    write_world(test_speed, test_dir_deg, name=test_world_name, gust_scaled=test_gust_scaled)
    
    generated_world_path = WORLDS_DIR / f"{test_world_name}.sdf"
    tree = ET.parse(generated_world_path)
    root = tree.getroot()
    world = root.find("world")
    

    plugins = world.findall(".//plugin")
    
    # check that there are exactly 14 <plugin> elements under world
    assert len(plugins) == 14, f"Expected exactly 14 plugins under world, found {len(plugins)}"
        
    # check that exactly one is WindEffects, and its magnitude noise/stddev parses to 0.45
    wind_effects_plugins = [p for p in plugins if p.get("name") == "gz::sim::systems::WindEffects"]
    assert len(wind_effects_plugins) == 1, f"Expected exactly 1 WindEffects plugin, found {len(wind_effects_plugins)}"
    
    wind_effects = wind_effects_plugins[0]
    stddev_element = wind_effects.find("./horizontal/magnitude/noise/stddev")
    assert stddev_element is not None, "Could not find standard deviation tag inside magnitude noise block"
    
    assert float(stddev_element.text) == pytest.approx(test_gust_scaled)