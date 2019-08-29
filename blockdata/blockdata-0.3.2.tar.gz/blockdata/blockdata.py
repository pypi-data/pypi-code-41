class Block(object):
    def __init__(self, start:int, end:int, orientation:bool, zero_index=True):
        """Creates a new Block from start and end coordinates and its orientation.

        Parameters
        ----------
        start : int
            Starting coordinate
        end : int
            End coordinate
        orientation : bool
            `True` if in the forward direction, otherwise, `False`.
        zero_index : bool, optional
            `True` if the coordinates follow zero-based notation of
            inclusive start and exclusive end values.
            `False` if coordinates follow one-basednotation of
            inclusive start and end values, by default True

        Raises
        ------
        ValueError
            Raises a ValueError when the `start` value is greater than or
            equal to the end value.

        """
        if zero_index:
            if start >= end:
                raise ValueError(
                    'Start value must always be less than end. '
                    'Set `orientation` to `False` to indicate '
                    'reverse direction.')
        else:
            if start > end:
                raise ValueError(
                    'Start value must always be less than or equal to end. '
                    'Set `orientation` to `False` to indicate '
                    'reverse direction.')
        self.start = start
        self.end = end
        self.orientation = orientation
        self.zero_index = zero_index

    @classmethod
    def encode(cls, vec:list):
        """Encodes an ordered list of positions into one or more blocks

        Parameters
        ----------
        vec : list of int
            Ordered list of positions

        Returns
        -------
        list of Block
            List of Block objects. Each Block is the compressed representation
            of a series of contiguous positions.
        """
        blocks = []
        if len(vec) == 0:
            return blocks
        start = vec[0]
        offset = 0
        for i, v in enumerate(vec):
            if i == 0:
                continue
            if vec[i-1] + 1 == v:
                offset += 1          
            elif vec[i-1] - 1 == v:
                offset -= 1          
            else:
                if offset >= 0:
                    blocks.append(
                        cls(start, start+offset+1, True))
                else:
                    blocks.append(
                        cls(start+offset, start+1, False))
                start = v
                offset = 0
                orientation = None

        if offset >= 0:
            blocks.append(
                cls(start, start+offset+1, True))
        else:
            blocks.append(
                cls(start+offset, start+1, False))
        return blocks
    
    def decode(self):
        """Decodes the current Block object into an ordered list of positions.

        Returns
        -------
        list of int
            Ordered list of positions
        """
        if self.zero_index:
            if not self.orientation:
                return list(reversed(range(self.start, self.end, 1)))
            return list(range(self.start, self.end, 1))
        # one-based, start and end inclusive
        if not self.orientation:
            return list(reversed(range(self.start, self.end+1, 1)))
        return list(range(self.start, self.end+1, 1))

    def zero_to_one(self):
        """Converts the Block from a zero-based, start-inclusive, and
        end-exclusive format to a one-based, start-inclusive, and end-inclusive
        format.

        Returns
        -------
        Block
            Block object using one-based, start-inclusive, and end-inclusive
            format.

        Raises
        ------
        Exception
            Raises an Exception if the current Block already follows
            one-based notation.
        """
        if not self.zero_index:
            raise Exception(f'{self} is already in one-based notation.')
        return type(self)(
            self.start+1, self.end, self.orientation, zero_index=False)

    def one_to_zero(self):
        """Converts the Block from a one-based, start-inclusive, and
        end-inclusive format to a zero-based, start-inclusive, and
        end-exclusive format 

        Returns
        -------
        Block
            Block object using zero-based, start-inclusive, and end-exclusive
            format.

        Raises
        ------
        Exception
            Raises an Exception if the current Block already follows
            zero-based notation.
        """
        if self.zero_index:
            raise Exception(f'{self} is already in zero-based notation.')
        return type(self)(
            self.start-1, self.end, self.orientation, zero_index=True)

    def to_string(self, str_format=None, formatters=None):
        """Converts Block into a string representation.
        
        Parameters
        ----------
        str_format : str, optional
            String formatting pattern using {name} placeholders.
            Placeholder names must be "start", "end", "orientation", or
            "zero_type". By default None.
        formatters : dict, optional
            Dictionary of functions/callables that is used to format
            values, by default None
        
        Returns
        -------
        str
            String-formatted representation of the Block
        """
        if not str_format:
            return self.__str__()
        d = {
            'start': self.start,
            'end': self.end,
            'orientation': self.orientation,
            'zero_index': self.zero_index,
        }
        if formatters:
            for k, fn in formatters.items():
                if k not in d.keys():
                    raise ValueError(
                        'Formatter key must be "start", '
                        '"end", "orientation", or "zero_index".')
                d[k] = fn(d[k])
        return str_format.format(
            start=d['start'],
            end=d['end'],
            orientation=d['orientation'],
            zero_index=d['zero_index']
        )

    def __repr__(self):
        return (
            f'Block({self.start}, {self.end}, {self.orientation}, '
            f'zero_index={self.zero_index})'
        )

    def __str__(self):
        c = '+' if self.orientation else '-'
        return f'{self.start}:{self.end}:{c}'

    def __eq__(self, other):
        if (self.zero_index == True) and (other.zero_index == False):
            return (
                (type(self).__name__ == type(other).__name__) and
                (self.start+1 == other.start) and
                (self.end == other.end) and
                (self.orientation == other.orientation)
            )
        elif (self.zero_index == False) and (other.zero_index == True):
            return (
                (type(self).__name__ == type(other).__name__) and
                (self.start == other.start+1) and
                (self.end == other.end) and
                (self.orientation == other.orientation)
            )
        return (
            (type(self).__name__ == type(other).__name__) and
            (self.start == other.start) and
            (self.end == other.end) and
            (self.orientation == other.orientation)
        )


class GenomeBlock(Block):
    def __init__(
        self, chrom:str, start:int, end:int, orientation:bool,
        zero_index=True
    ):
        """Creates a new GenomeBlock from chromosome/scaffold name, 
        start and end coordinates and its orientation.

        Parameters
        ----------
        chrom: str
            Chromosome or scaffold name
        start : int
            Starting coordinate
        end : int
            End coordinate
        orientation : bool
            `True` if in the forward direction, otherwise, `False`.
        zero_index : bool, optional
            `True` if the coordinates follow zero-based notation of
            inclusive start and exclusive end values.
            `False` if coordinates follow one-basednotation of
            inclusive start and end values, by default True

        Raises
        ------
        ValueError
            Raises a ValueError when the `start` value is greater than or
            equal to the end value.

        """
        super().__init__(start, end, orientation, zero_index=zero_index)
        self.chrom = chrom

    @classmethod
    def encode(cls, chrom:str, vec:list):
        """Encodes an ordered list of positions into one or more GenomeBlocks.

        Parameters
        ----------
        vec : list of int
            Ordered list of positions

        Returns
        -------
        list of Block
            List of Block objects. Each Block is the compressed representation
            of a series of contiguous positions.
        """
        return [
            cls(chrom, b.start, b.end, b.orientation, b.zero_index)
            for b in Block.encode(vec)]
    
    def decode(self):
        """Decodes the current GenomeBlock object into an ordered list of
        positions.

        Returns
        -------
        list of int
            Ordered list of positions
        """
        return (self.chrom, super().decode())

    def zero_to_one(self):
        """Converts the GenomeBlock from a zero-based, start-inclusive, and
        end-exclusive format to a one-based, start-inclusive, and end-inclusive
        format.

        Returns
        -------
        GenomeBlock
            GenomeBlock object using one-based, start-inclusive,
            and end-inclusive format.

        Raises
        ------
        Exception
            Raises an Exception if the current GenomeBlock already follows
            one-based notation.
        """
        if not self.zero_index:
            raise Exception(f'{self} is already in one-index notation.')
        return type(self)(
            self.chrom, self.start+1, self.end, self.orientation, 
            zero_index=False)

    def one_to_zero(self):
        """Converts the GenomeBlock from a one-based, start-inclusive, and
        end-inclusive format to a zero-based, start-inclusive, and
        end-exclusive format 

        Returns
        -------
        GenomeBlock
            GenomeBlock object using zero-based, start-inclusive,
            and end-exclusive format.

        Raises
        ------
        Exception
            Raises an Exception if the current GenomeBlock already follows
            zero-based notation.
        """
        if self.zero_index:
            raise Exception(f'{self} is already in zero-index notation.')
        return type(self)(
            self.chrom, self.start-1, self.end, self.orientation, 
            zero_index=True)

    def to_string(self, str_format=None, formatters=None):
        """Converts Block into a string representation.
        
        Parameters
        ----------
        str_format : str, optional
            String formatting pattern using {name} placeholders.
            Placeholder names must be "start", "end", "orientation", or
            "zero_type". By default None.
        formatters : dict, optional
            Dictionary of functions/callables that is used to format
            values, by default None
        
        Returns
        -------
        str
            String-formatted representation of the Block
        """

        if not str_format:
            return self.__str__()
        d = {
            'chrom': self.chrom,
            'start': self.start,
            'end': self.end,
            'orientation': self.orientation,
            'zero_index': self.zero_index,
        }
        if formatters:
            for k, fn in formatters.items():
                if k not in d.keys():
                    raise ValueError(
                        'Formatter key must be "chrom", "start", '
                        '"end", "orientation", or "zero_index".')
                d[k] = fn(d[k])
        return str_format.format(
            chrom=d['chrom'],
            start=d['start'],
            end=d['end'],
            orientation=d['orientation'],
            zero_index=d['zero_index']
        )

    def __repr__(self):
        return (
            f'GenomeBlock({self.chrom}, {self.start}, {self.end}, '
            f'{self.orientation}, zero_index={self.zero_index})'
        )

    def __str__(self):
        c = '+' if self.orientation else '-'
        return f'{self.chrom}:{self.start}:{self.end}:{c}'

    def __eq__(self, other):
        if (self.zero_index == True) and (other.zero_index == False):
            return (
                (type(self).__name__ == type(other).__name__) and
                (self.chrom == other.chrom) and
                (self.start+1 == other.start) and
                (self.end == other.end) and
                (self.orientation == other.orientation)
            )
        elif (self.zero_index == False) and (other.zero_index == True):
            return (
                (type(self).__name__ == type(other).__name__) and
                (self.chrom == other.chrom) and
                (self.start == other.start+1) and
                (self.end == other.end) and
                (self.orientation == other.orientation)
            )
        return (
            (type(self).__name__ == type(other).__name__) and
            (self.chrom == other.chrom) and
            (self.start == other.start) and
            (self.end == other.end) and
            (self.orientation == other.orientation)
        )