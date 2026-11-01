import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from sim.sim_model import MODELS_DIR, write_model

MASS_FACTOR_T = 1.2
INERTIA_FACTOR_T = 0.8

def test_write_model_scaled_values():
    write_model(MASS_FACTOR_T, INERTIA_FACTOR_T)

    # locate the generated base model SDF
    new_sdf_path = MODELS_DIR / "x500_mc_base" / "model.sdf"

    # parse the modified tree
    tree = ET.parse(new_sdf_path)
    root = tree.getroot()

    # find the mass and izz elements in the root
    mass_element = root.find(".//link[@name='base_link']/inertial/mass")
    izz_element = root.find(".//link[@name='base_link']/inertial/inertia/izz")  

    assert mass_element is not None
    assert izz_element is not None

    assert float(mass_element.text) == pytest.approx(2 * MASS_FACTOR_T)
    assert float(izz_element.text) == pytest.approx(0.04 * INERTIA_FACTOR_T)

def test_stock_model_mass_unaffected():
    # locate the original template base model SDF
    stock_sdf_path = MODELS_DIR / "x500_base" / "model.sdf"
    
    # parase the stock XML tree
    tree = ET.parse(stock_sdf_path)
    root = tree.getroot()
    
    mass_element = root.find(".//link[@name='base_link']/inertial/mass")
    
    assert mass_element is not None
    
    assert float(mass_element.text) == pytest.approx(2.0)



def test_write_model_enables_wind_on_base_link():
    test_mass_factor = 1.0
    test_inertia_factor = 1.0
    test_model_name = "x500_mc"
    
    write_model(test_mass_factor, test_inertia_factor, test_model_name)
    
    # parse the model
    generated_model_path = MODELS_DIR / f"{test_model_name}_base" / "model.sdf"
    
    tree = ET.parse(generated_model_path)
    root = tree.getroot()
    
    enable_wind_text = root.find(".//link[@name='base_link']/enable_wind").text
    
    # check that it matches the string value rule required by Gazebo
    assert enable_wind_text == "true"