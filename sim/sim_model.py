# write_model() written with AI assistance (Claude, Anthropic), Oct 2026.
# I asked for help writing it and for an explanation of how it works, because I
# didn't know how to change the drone's parameters locally from Python.

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# PX4's Gazebo models folder inside WSL, reached from Windows
MODELS_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\itsaerocraft\PX4-Autopilot\Tools\simulation\gz\models")


def write_model(mass_factor, inertia_factor, name="x500_mc"):
    '''
    Writes a scaled copy of the PX4 x500 Gazebo model, with the base_link
    body's mass and inertia multiplied by the given factors and wind forces
    enabled.

    Args:
        [mass_factor]: multiplier applied to the stock base_link mass (unitless).
        [inertia_factor]: multiplier applied to the stock ixx/iyy/izz inertia
            tensor diagonal (unitless).
        [name]: model name to write; files are written to <name>_base (body)
            and <name> (motor assembly pointed at that body).

    Returns:
        [name] of the model written, for use as the model argument to start_sim.

    Reads the stock x500 / x500_base files (never modified) and writes new
    copies; PX4 still flies the result with stock x500 tuning, which creates
    the model mismatch used to test parameter sensitivity.
    '''
    stock_base = MODELS_DIR / "x500_base"
    stock_top = MODELS_DIR / "x500"
    new_base = MODELS_DIR / f"{name}_base"
    new_top = MODELS_DIR / name

    # parse the stock base model structure
    tree = ET.parse(stock_base / "model.sdf")
    root = tree.getroot()

    # find the inertial properties element block nested directly inside the base_link link tag
    inertial = root.find(".//link[@name='base_link']/inertial")
    

    # scale the mass, by conversion into string
    mass = inertial.find("mass")
    mass.text = str(float(mass.text) * mass_factor)

    # scale each diagonal inertia tensor matrix value (ixx, iyy, izz)
    for axis in ("ixx", "iyy", "izz"):
        el = inertial.find(f"inertia/{axis}")
        el.text = str(float(el.text) * inertia_factor)

    # locate the base_link element block to append wind testing elements
    base_link_element = root.find(".//link[@name='base_link']")
    enable_wind_subelement = base_link_element.find("enable_wind")
    enable_wind_subelement = ET.SubElement(base_link_element, 'enable_wind')
    enable_wind_subelement.text = "true"


    # WRITING BACK TO FOLDER (AI)
    new_base.mkdir(parents=True, exist_ok=True)
    tree.write(new_base / "model.sdf", xml_declaration=True, encoding="utf-8")
    shutil.copy(stock_base / "model.config", new_base / "model.config")


    # MOTOR INTERFACE (AI)

    # Parse the top-level main motor configuration definition assembly
    tree = ET.parse(stock_top / "model.sdf")
    root = tree.getroot()

    uri_element = root.find(".//include/uri")
    if uri_element is not None:
        uri_element.text = f"model://{name}_base"

    new_top.mkdir(parents=True, exist_ok=True)
    tree.write(new_top / "model.sdf", xml_declaration=True, encoding="utf-8")
    shutil.copy(stock_top / "model.config", new_top / "model.config")

    return name
