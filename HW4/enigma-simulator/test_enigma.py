import pytest 
from machine import Enigma
from components import *

# should get 100% branch coverage
    # coverage run -m pytest
    # coverage report
    # coverage html
        # creates html page, yellow is partial branches and what part wasn't covered
# test for bugs/bad inputs too
    # TypeError checks? Inputs of None

@pytest.fixture()
def enigma_instance():
    return Enigma('XYZ', [('A', 'B'), ('Q', 'R')])

class TestEnigma():
    
    def test_init(self, enigma_instance):
        # test to make sure len(key) == 3
        with pytest.raises(ValueError):
            shortkey_enigma = Enigma('AB')
        # checking default key and rotor_order
        assert enigma_instance.key == 'XYZ'
        assert enigma_instance.rotor_order == ['I', 'II', 'III']
        assert True == isinstance(enigma_instance.reflector, Reflector) 
        assert True == isinstance(enigma_instance.plugboard, Plugboard)

    def test_repr(self, enigma_instance):
        assert enigma_instance.__repr__() == f"Keyboard <-> Plugboard <->  Rotor {enigma_instance.rotor_order[0]} <-> Rotor  {enigma_instance.rotor_order[1]} <-> Rotor  {enigma_instance.rotor_order[2]} <-> Reflector \nKey:  + {enigma_instance.key}"

    def test_encipher(self, enigma_instance):
        # instantiate enigma w/ key
        key = enigma_instance.key
        enigma_instance.set_rotor_position(key)
        message = 'TEST THIS'
        # encode message
        cipher = enigma_instance.encipher(message)
        # reset the rotors to original position
        enigma_instance.set_rotor_position(key)
        # decrypt message
        decrypt = enigma_instance.encipher(cipher)
        assert 'TESTTHIS' == decrypt
        

    # same as encipher
    def test_decipher(self, enigma_instance):
        key = enigma_instance.key
        enigma_instance.set_rotor_position(key)
        message = 'JASON'
        cipher = enigma_instance.decipher(message)
        enigma_instance.set_rotor_position(key)
        decrypt = enigma_instance.decipher(cipher)
        assert message == decrypt

    def test_encode_decode_letter(self, enigma_instance):
        # check if letter in a-zA-Z
        with pytest.raises(ValueError) as err:
            enigma_instance.encode_decode_letter('1')
        assert err.type is ValueError
        # 'A' in swaps, so will switch to 'B' before encoding
            # init ret 'Q', so should swap to 'R' based on swaps array
            # simultaneously testing for lower case input
                # function should use .upper() to change it
        final_letter = enigma_instance.encode_decode_letter('a')
        assert final_letter == 'R'
    
    def test_set_rotor_position(self, enigma_instance, capsys):
        key = enigma_instance.key
        bad_key = 'AB'
        enigma_instance.set_rotor_position(key, True)
        # snapshots what is in stdout
        output = capsys.readouterr()
        assert output.out == 'Rotor position successfully updated. Now using ' + key + '.\n'

        enigma_instance.set_rotor_position(bad_key)
        output = capsys.readouterr()
        assert output.out == 'Please provide a three letter position key such as AAA.\n'

    def test_set_rotor_order(self, enigma_instance):
        assert True == isinstance(enigma_instance.l_rotor, Rotor)
        assert True == isinstance(enigma_instance.m_rotor, Rotor)
        assert True == isinstance(enigma_instance.r_rotor, Rotor)
        assert enigma_instance.m_rotor.prev_rotor == enigma_instance.r_rotor
        assert enigma_instance.l_rotor.prev_rotor == enigma_instance.m_rotor
        
    def test_set_plugs(self, enigma_instance, capsys):
        swaps = [('S', 'T')]
        enigma_instance.set_plugs(swaps, printIt=True)
        output = capsys.readouterr()
        assert output.out == 'Plugboard successfully updated. New swaps are:\n' + 'A <-> B\n' + 'Q <-> R\n' + 'S <-> T\n'
        assert enigma_instance.plugboard.swaps == {'A':'B', 'B':'A', 'Q':'R', 'R':'Q', 'S':'T', 'T':'S'}
        # testing replace=True, printIt=False
        new_swaps = ['AB']
        enigma_instance.set_plugs(new_swaps, True)
        assert enigma_instance.plugboard.swaps == {'A':'B', 'B':'A'} 
        enigma_instance.set_plugs([], True)
        assert enigma_instance.plugboard.swaps == {} 



    def test_palindrome(self):
        message = 'ABCDCBA'
        enigma_instance = Enigma('XYZ')
        cipher = enigma_instance.encipher(message)
        assert cipher[::-1] != cipher

    def test_same_message(self):
        message = 'SAME'
        enigma_instance = Enigma('XYZ')
        cipher = enigma_instance.encipher(message)
        cipher2 = enigma_instance.encipher(message)
        assert cipher != cipher2

   


class TestRotor():

    def test_init(self):
        # test bad rotor_num
        with pytest.raises(ValueError):
            bad_rotor_num = Rotor('X', 'A')
        # test good rotor_num
        rotor_num = 'I'
        window_letter = 'a'
        rotor_instance = Rotor(rotor_num, window_letter)
        assert rotor_instance.rotor_num == rotor_num
        assert rotor_instance.wiring == ROTOR_WIRINGS[rotor_num] 
        assert rotor_instance.notch == ROTOR_NOTCHES[rotor_num] 
        assert rotor_instance.window == window_letter.upper()
        assert rotor_instance.offset == ALPHABET.index(rotor_instance.window)
        assert rotor_instance.next_rotor == None
        assert rotor_instance.prev_rotor == None
       
    def test_repr(self):
        rotor_instance = Rotor('I', 'A')
        assert rotor_instance.__repr__() == f"Wiring:\n{rotor_instance.wiring}\nWindow: {rotor_instance.window}"

    def test_step(self):
        next_rotor = Rotor('I', 'Q')
        rotor_instance = Rotor('II', 'E', next_rotor)
        new_offset = (rotor_instance.offset + 1)%26
        new_window = ALPHABET[new_offset]
        next_new_offset = (rotor_instance.next_rotor.offset + 1)%26
        next_new_window = ALPHABET[next_new_offset]
        rotor_instance.step()
        assert new_offset == rotor_instance.offset
        assert new_window == rotor_instance.window
        assert next_new_offset == rotor_instance.next_rotor.offset
        assert next_new_window == rotor_instance.next_rotor.window
        # test elif
        next_rotor2 = Rotor('V', 'Z')
        rotor_instance2 = Rotor('III', 'X', next_rotor2)
        rotor_instance2.step()

    def test_encode_letter(self, capsys):
        prev_rotor = Rotor('I', 'A')
        next_rotor = Rotor('III', 'C')

        rotor_instance = Rotor('II', 'B', next_rotor, prev_rotor)

        result = rotor_instance.encode_letter(1, False, printit=True)
        output_letter = rotor_instance.wiring['backward'][(1 + rotor_instance.offset)%26]
        output_index = (ALPHABET.index(output_letter) - rotor_instance.offset)%26
        output = capsys.readouterr()
        assert output.out == 'Rotor ' + rotor_instance.rotor_num + ': input = ' + ALPHABET[(rotor_instance.offset + 1)%26] + ', output = ' + output_letter + '\n'
        assert result == rotor_instance.prev_rotor.encode_letter(output_index, False)

        result2 = rotor_instance.encode_letter(35, False, True)
        output_letter2 = rotor_instance.wiring['backward'][(35 + rotor_instance.offset)%26]
        output_index2 = (ALPHABET.index(output_letter2) - rotor_instance.offset)%26
        assert result2 == rotor_instance.prev_rotor.encode_letter(output_index2, False)

        result3 = next_rotor.encode_letter('x', return_letter=True)
        index = ALPHABET.index('X')
        output_letter3 = next_rotor.wiring['forward'][(index + next_rotor.offset)%26]
        output_index3 = (ALPHABET.index(output_letter3) - next_rotor.offset)%26
        assert result3 == ALPHABET[output_index3]

    def test_change_setting(self):
        rotor_instance = Rotor('I', 'A')
        window = rotor_instance.window
        offset = rotor_instance.offset
        # test lowercase input
        rotor_instance.change_setting('b')
        assert rotor_instance.window == 'B'
        assert rotor_instance.offset == ALPHABET.index(rotor_instance.window)


    def test_mult_step(self):
        key = 'KEY'
        enigma_instance = Enigma(key)
        # make all 3 rotors step
        enigma_instance.r_rotor.step() 
        new_windows = enigma_instance.l_rotor.window + enigma_instance.m_rotor.window + enigma_instance.r_rotor.window
        offsets = [enigma_instance.l_rotor.offset, enigma_instance.m_rotor.offset, enigma_instance.r_rotor.offset] #offsets should increase by 1
        test_window = ""
        check_window = ""
        for offset in offsets:
            test_window += ALPHABET[offset]
            revert = (offset - 1)%26
            check_window += ALPHABET[revert]

        assert new_windows == test_window
        assert check_window == key # reverting each rotor back one should equal the starting point

    


class TestReflector():

    def test_init(self):
        reflector_instance = Reflector()
        assert reflector_instance.wiring == {'A':'Y', 'B':'R', 'C':'U', 'D':'H', 'E':'Q', 'F':'S', 'G':'L', 'H':'D',
                       'I':'P', 'J':'X', 'K':'N', 'L':'G', 'M':'O', 'N':'K', 'O':'M', 'P':'I',
                       'Q':'E', 'R':'B', 'S':'F', 'T':'Z', 'U': 'C', 'V':'W', 'W':'V', 'X':'J',
                       'Y':'A', 'Z':'T'
                      }
    
    def test_repr(self):
        reflector_instance = Reflector()
        assert reflector_instance.__repr__() == f"Reflector wiring: \n{reflector_instance.wiring}"


    

class TestPlugboard():

    def test_init(self):
        swaps = ['AB', 'XR']
        plugboard_instance = Plugboard(swaps)
        assert plugboard_instance.swaps['A'] == 'B'
        assert plugboard_instance.swaps['B'] == 'A'
        assert plugboard_instance.swaps['X'] == 'R'
        assert plugboard_instance.swaps['R'] == 'X'
        plugboard_instance2 = Plugboard(None)
        assert plugboard_instance2.swaps == {}

    def test_repr(self):
        swaps = ['AB']
        plugboard_instance = Plugboard(swaps)
        output = plugboard_instance.__repr__() 
        assert output == "A <-> B"

    def test_update_swaps(self, capsys):
        plugboard_instance = Plugboard(None)
        new_swaps = ['AB']
        plugboard_instance.update_swaps(new_swaps)
        assert plugboard_instance.swaps == {'A':'B', 'B':'A'}

        plugboard_instance.update_swaps(['CD'])
        assert plugboard_instance.swaps == {'A':'B', 'B':'A', 'C':'D', 'D':'C'}

        too_many_swaps = ['AB', 'CD', 'EF', 'GH', 'IJ', 'KL', 'MN']
        plugboard_instance.update_swaps(too_many_swaps, True)
        output = capsys.readouterr()
        assert output.out == 'Only a maximum of 6 swaps is allowed.\n'

        plugboard_instance.update_swaps(None, True)
        assert plugboard_instance.swaps == {}
