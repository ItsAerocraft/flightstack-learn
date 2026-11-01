import numpy as np
import pytest
from flight.flight_state import State 

def test_state_initialization():
    # A new State() has all-NaN pos and vel
    a = State()
    assert np.isnan(a.pos).all()
    assert np.isnan(a.vel).all()
    assert np.isnan(a.t)
    assert a.n_updates == 0

def test_state_independent_arrays():
    # Two State() objects don't share an array, which shows that default_factory works in creating independent arrays
    a = State()
    b = State()
    
    a.pos[0] = 42.0
    assert np.isnan(b.pos[0])

def test_state_slots():
    # Setting a misspelled attribute raises AttributeError due to slots=True
    a = State()
    with pytest.raises(AttributeError):
        a.poss = np.array([1.0, 2.0, 3.0])  # Misspelled attribute a.poss
