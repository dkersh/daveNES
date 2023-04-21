import json
import pytest
import numpy as np
import sys
sys.path.append('C:/Users/David/Documents/Coding/daveNES/src')
import cpu

json_test = 'C:/Users/David/Documents/Coding/daveNES/tests/ProcessorTests-main/nes6502/v1/0a.json'
test_range = range(10000) # number of tests in a json

@pytest.fixture
def get_json(json_filename: str = json_test) -> dict:
    with open(json_filename) as f:
        test = json.load(f)

    print(test[0]['name'])
    print(test[0]['initial'])
    print(test[0]['final'])
    for l in test[0]['cycles']:
        print(f'addr: 0x{l[0]:04x} | value: 0x{l[1]:04x} | {l[2]}')

    return test

def init_daveNES(test):
    daveNES = cpu.MOS6502(debug = False)
    daveNES.initialise_RAM()

    # Load test program
    for val in test['initial']['ram']:
        print(f'{val[0]}, {val[1]}')
        daveNES.ram.memory[val[0]] = np.uint8(val[1])
    daveNES.r_program_counter = test['initial']['pc']
    daveNES.r_stack_pointer = test['initial']['s']
    daveNES.r_accumulator = test['initial']['a']
    daveNES.r_index_X = test['initial']['x']
    daveNES.r_index_Y = test['initial']['y']
    daveNES.value_to_status(test['initial']['p'])

    return daveNES

@pytest.mark.parametrize('i', test_range)
def test_daveNES(get_json, i):
    print(f'ind: {i}')
    test = get_json[i]
    daveNES = init_daveNES(test)

    daveNES.step_program()

    assert test['final']['pc'] == daveNES.r_program_counter
    assert test['final']['s'] == daveNES.r_stack_pointer
    assert test['final']['a'] == daveNES.r_accumulator
    assert test['final']['x'] == daveNES.r_index_X
    assert test['final']['y'] == daveNES.r_index_Y