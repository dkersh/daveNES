import json
import pytest
import numpy as np
import sys
#sys.path.append('C:/Users/David/Documents/Coding/daveNES/src')
#sys.path.append('/Users/davidkersh/Documents/Other_Work/Coding/daveNES/src')
import cpu.cpu as cpu

num_of_tests = 500
sbc_opcodes = ['e9', 'e5', 'f5', 'ed', 'fd', 'f9', 'e1', 'f1']
json_test = lambda x: f'C:/Users/David/Documents/Coding/daveNES/tests/ProcessorTests-main/nes6502/v1/{x}.json'
all_json_files = [json_test(c) for c in sbc_opcodes]

json_files_reshaped = np.repeat(all_json_files, num_of_tests)
inds = np.ravel([np.arange(num_of_tests).tolist() for i in range(len(all_json_files))])

def get_json(json_filename: str = json_test) -> dict:
    """Load a json test file.

    Args:
        json_filename (str, optional): json input file. Defaults to json_test, a lambda function which takes a str as input.

    Returns:
        dict: loaded json object.
    """
    with open(json_filename) as f:
        test = json.load(f)

    return test

def init_daveNES(test: dict):
    """Initialises daveNES object and loads the test parameters into the appropriate
    registers and memory locations.

    Args:
        test (dict): json test

    Returns:
        daveNES: Initialised daveNES object.
    """
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

@pytest.mark.parametrize("json_filename, i", zip(json_files_reshaped, inds))
def test_SBC(i, json_filename):
    """Unit test for daveNES. Iterates over the json file. Decorated with a pytest
    parametrize so as to iterate over the whole list of json test files.

    Args:
        i (int): Iterate of json
        json_filename (str): unit test file.
    """
    print(f'ind: {i}, filename: {json_filename}')
    test = get_json(json_filename)[i]
    daveNES = init_daveNES(test)

    daveNES.step_program()

    assert test['final']['pc'] == daveNES.r_program_counter
    assert test['final']['s'] == daveNES.r_stack_pointer
    assert test['final']['a'] == daveNES.r_accumulator
    assert test['final']['x'] == daveNES.r_index_X
    assert test['final']['y'] == daveNES.r_index_Y

    # and the registers
    assert f'{test["final"]["p"]:08b}' == "".join(str(int(daveNES.r_status[k])) for k in daveNES.r_status.keys())[::-1]