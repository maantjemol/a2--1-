import numpy as np
import typing

class IntelDevice:
    def __init__(self, width:int, height:int, enc_locations: typing.List[str], enc_codes:typing.List[str], caesar_shift: int):
        """
        The IntelDevice object, containing all information and functions required for encoding and decoding messages,
        processing raw encoded locations, efficiently searching for locations based on codes and returning encoded
        answers.  

        :param width: The width (number of columns) of the 2D distance/location grid (self.loc_grid) that we have to fill in
        :param height: The height (number of rows) of the 2D distance/location grid (self.loc_grid) that we have to fill in
        :param enc_locations: A list of encoded location names that correspond to the locations in self.loc_grid
        :param enc_codes: A list of encoded codes (ints) that have to be entered into self.loc_grid
        :param caesar_shift: The caesar shift constant used to encode messages. You may assume this will always be in the set 
                             {0,1,...,26}. We do NOT use modulo calculations for our caesar cipher. 

        You do not need to change this function
        """

        self.width = width
        self.height = height
        self.enc_locations = enc_locations
        self.enc_codes = enc_codes
        self.caesar_shift = caesar_shift

        self.loc_grid = np.zeros((height, width))
        self.coordinate_to_location = dict() # maps locations (y,x) to their names 
        self.scanned_cells = 0


    def encode_message(self, msg:str) -> str:
        """
        A function that encodes a given string using a simplified form of caesar cipher (without using modulo). Every character of the string will be 
        transformed into the ordinal/numerical representation and encoded by shifting the number with self.caesar_shift 
        (through addition). Afterward, the shifted numbers are transformed into bitstring representation.

        For example, suppose we want to encode the message 'hello' with a caesar shift of 5. 
        The corresponding encoded message (output of this function) would be '1101101 1101010 1110001 1110001 1110100'. Note that the 
        number of bitstrings separated by spaces is equal to the number of characters of the string 'hello'. 
        Let's look at the first character 'h'. Its ordinal representation is 104. We shift its representation by 5, giving us 109. 
        109 is then transformed into a bitstring, which gives us 1101101 (the first bitstring in the encoded message). 

        Hints: the following built-in Python functions may be of use
          - ord(x): takes a character x as input and returns the ordinal representation
          - '{0:b}'.format(x): transforms a number x into a bitstring

        :param msg: The input message (string) that should be encoded
        
        Returns: the encoded message
        """

        bit_string = ""
        for letter in msg:
            bit_string += '{0:b} '.format(ord(letter) + self.caesar_shift)
        return bit_string[:-1]

    
    def decode_message(self, msg: str) -> str:
        """
        A function that decodes an encoded message (the reverse of the function above). For example, given the encoded message 
        '1101101 1101010 1110001 1110001 1110100' (with the caesar shift self.caeser_shift=5), this function should return the decoded 
        message, which is 'hello'. 

        :param msg: The encoded message (string) that should be decoded
        
        Returns: the decoded message
        """

        original_msg = ""
        for i in msg.split(" "):
          original_msg += chr(int(i, 2) - self.caesar_shift)
        return original_msg


    def fill_coordinate_to_loc(self):
        """
        Function that fills the data structure self.coordinate_to_location. It maps every (y,x) tuple in self.loc_grid
        to the corresponding decoded location (determined from self.enc_locations). The list of encoded locations wrap
        around the rows of self.loc_grid from left to right and top to bottom. For example, if we have a 2x2 loc_grid and 
        self.enc_locations = [self.encode_message('a'), self.encode_message('b'), self.encode_message('c'), self.encode_message('d')], 
        then the mapping should be:
          (0,0) -> 'a'
          (0,1) -> 'b'
          (1,0) -> 'c'
          (1,1) -> 'd'

        The function does not return anything. It simply fills the self.coordinate_to_location data structure with the right mapping.
        """

        x = 0
        for i in range(self.height):
            for j in range(self.width):
                loc = self.enc_locations[x]
                self.coordinate_to_location[(i, j)] = self.decode_message(loc)
                x += 1

            

    def fill_loc_grid(self):
        """
        Function that fills the data structure self.loc_grid with the codes found in self.enc_codes. Note that
        these codes have to be decoded using self.decode_message(). The encoded codes wrap around self.loc_grid 
        from left to right, and from top to bottom. For example, if we have 
        self.enc_codes = [self.encode_message('10'), self.encode_message('15'), self.encode_message('11'), self.encode_message('16')],
        the following loc_grid should be created/filled in:
          [[10,15],
           [11,16]]

        The function does not return anything. It simply fills the self.loc_grid data structure with the decoded codes.
        """

        x = 0
        for i in range(self.height):
            for j in range(self.width):
                p = self.decode_message(self.enc_codes[x])
                self.loc_grid[i][j] = p
                x += 1


    def divconq_search(self, value: int, x_from: int, x_to: int, y_from: int, y_to: int) -> typing.Tuple[int, int]:
        """
        The divide and conquer search function. The function searches for value in a subset of self.loc_grid.
        More specifically, we only search in the x-region from x_from up to (and including) x_from and the y-region
        from y_from up to (and including) y_to. At the initial function call, x_from=0, x_to=self.width-1, y_from=0, y_to=self.height-1 ,
        meaning that we search over the entire 2d grid self.loc. 
        This function recursively calls itself on smaller subproblems (subsets/subrectangles of the 2d grid) and combines the solutions
        to these subproblems in order to find the solution to the complete initial problem.

        Note: this function should be more efficient than a naive search that iterates over every cell until the value is found. 
        Thus, make sure design a proper divide and conquer strategy for this. A too simplistic strategy (search over every cell in the grid) 
        will not lead to a passing grade. Please consult the TAs before handing in the assignment whether your approach is good. 

        :param value: The value that we are searching for in the subrectangle specified by (x_from, x_to, y_from, y_to)
        :param x_from: The leftmost x coordinate of the subrectangle that we are searching over
        :param x_to: The rightmost x coordinate of the subrectangle we are searching over
        :param y_from: The topmost y coordinate of the subrectangle we are searching over
        :param y_to: The bottom y coordinate of the subrectangle we are searching over

        Note that the following two constraints hold:
          1. x_from <= x_to
          2. y_from <= y_to

        Returns:
          None if the value does not occur in the subrectangle we are searching over
          A tuple (y,x) specifying the location where the value was found (if the value occurs in the subrectangle)
        """
        # Check for cases where no matching value can be found:
        #   - the search range is empty (x_from > x_to or y_from > y_to)
        #   - the value we are searching for is greater than the largest value in the search range.
        if (x_from > x_to or y_from > y_to or
            value > self.loc_grid[(y_to, x_to)] or
            value < self.loc_grid[(y_from, x_from)]):
            # Return None to indicate that the value was not found in the search range.
            return None

        # Calculate the midpoint of the search range.
        x_mid = (x_from + x_to) // 2
        y_mid = (y_from + y_to) // 2
        mid_value = self.loc_grid[(y_mid, x_mid)]

        # print(
        # f"""
        #     x_from = {x_from}
        #     x_to = {x_to}    
        #     y_from = {y_from}
        #     y_to = {y_to}    
        #     x_mid = {x_mid}
        #     y_mid = {y_mid}  
        #     value = {value}
        #     mid_value = {mid_value}
        # """
        # )

        
        # Check if the midpoint value is the same as the value we are searching for.
        if mid_value == value:
            self.scanned_cells += 1
            # Return a tuple containing the x and y coordinates of the matching value.
            return (y_mid, x_mid)

        # Check if there are any further subranges to search. This prevents looping
        if (x_from == x_to and  y_from == y_to):
            # Return None to indicate that the value was not found in the search range.
            return None
        
        # If the midpoint value is greater than the search value, 
        # recursively search the sub-range to the top left of the midpoint.
        if value < mid_value:
            self.scanned_cells += (x_to - x_from) * (y_to - y_from)
            result = self.divconq_search(value, x_from, x_to, y_from, y_mid -1)
            if result is not None:
                return result
                
            result = self.divconq_search(value, x_from, x_mid - 1, y_mid, y_to)
            if result is not None:
                return result

        # If the midpoint value is less than the search value,
        # recursively search the sub-ranges to the right and below the midpoint.
        else: # value > mid_value
            self.scanned_cells += (x_to - x_from) * (y_to - y_from)
            result = self.divconq_search(value, x_mid + 1, x_to, y_from, y_mid)
            if result is not None:
                return result
                
            result = self.divconq_search(value, x_from, x_to, y_mid + 1, y_to)
            if result is not None:
                return result
            
        # If the value was not found in any of the recursive searches, return None.
        return None
    
    def divconq_search_shit(self, value: int, x_from: int, x_to: int, y_from: int, y_to: int) -> typing.Tuple[int, int]:
        """
        The divide and conquer search function. The function searches for value in a subset of self.loc_grid.
        More specifically, we only search in the x-region from x_from up to (and including) x_from and the y-region
        from y_from up to (and including) y_to. At the initial function call, x_from=0, x_to=self.width-1, y_from=0, y_to=self.height-1 ,
        meaning that we search over the entire 2d grid self.loc. 
        This function recursively calls itself on smaller subproblems (subsets/subrectangles of the 2d grid) and combines the solutions
        to these subproblems in order to find the solution to the complete initial problem.

        Note: this function should be more efficient than a naive search that iterates over every cell until the value is found. 
        Thus, make sure design a proper divide and conquer strategy for this. A too simplistic strategy (search over every cell in the grid) 
        will not lead to a passing grade. Please consult the TAs before handing in the assignment whether your approach is good. 

        :param value: The value that we are searching for in the subrectangle specified by (x_from, x_to, y_from, y_to)
        :param x_from: The leftmost x coordinate of the subrectangle that we are searching over
        :param x_to: The rightmost x coordinate of the subrectangle we are searching over
        :param y_from: The topmost y coordinate of the subrectangle we are searching over
        :param y_to: The bottom y coordinate of the subrectangle we are searching over

        Note that the following two constraints hold:
          1. x_from <= x_to
          2. y_from <= y_to

        Returns:
          None if the value does not occur in the subrectangle we are searching over
          A tuple (y,x) specifying the location where the value was found (if the value occurs in the subrectangle)
        """
        # Check for cases where no matching value can be found:
        #   - the search range is empty (x_from > x_to or y_from > y_to)
        #   - the value we are searching for is greater than the largest value in the search range.

        for i in range(len(self.loc_grid)):
            for j in range(len(self.loc_grid[i])):
                if self.loc_grid[i][j] == value:
                    self.scanned_cells += 1
                    return (i, j)
        return None

        

    def start_search(self, value) -> str:
        """
        Non-recursive function that starts the recursive divide and conquer search function above. You can assume
        that self.coordinate_to_location and self.loc_grid have already been filled before this function is called (so 
        make sure not to call them again in this function). 
        
        :param value: The value that we are searching for in self.loc_grid

        Returns:
          None if the value does not occur in self.loc_grid
          The encoded location of where the value was found. Note that the location is not the (y,x) tuple but the
          corresponding name of the location (encoded with self.encode_message). 
        """

        # process raw locations with caesar shift, 
        # construct the loc_grid and start the search
        result = self.divconq_search(value, x_from=0, x_to=self.loc_grid.shape[1]-1, y_from=0, y_to=self.loc_grid.shape[0]-1)

        if result is None:
            return result
        else:
            return self.encode_message(self.coordinate_to_location[result]), self.scanned_cells

    def start_shit_search(self, value) -> str:
        """
        Non-recursive function that starts the recursive divide and conquer search function above. You can assume
        that self.coordinate_to_location and self.loc_grid have already been filled before this function is called (so 
        make sure not to call them again in this function). 
        
        :param value: The value that we are searching for in self.loc_grid

        Returns:
          None if the value does not occur in self.loc_grid
          The encoded location of where the value was found. Note that the location is not the (y,x) tuple but the
          corresponding name of the location (encoded with self.encode_message). 
        """

        # process raw locations with caesar shift, 
        # construct the loc_grid and start the search
        result = self.divconq_search_shit(value, x_from=0, x_to=self.loc_grid.shape[1]-1, y_from=0, y_to=self.loc_grid.shape[0]-1)

        if result is None:
            return result
        else:
            return self.encode_message(self.coordinate_to_location[result]), self.scanned_cells
        