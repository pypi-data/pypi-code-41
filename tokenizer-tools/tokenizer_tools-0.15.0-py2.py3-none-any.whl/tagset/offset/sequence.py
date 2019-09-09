import uuid

from tokenizer_tools.tagset.offset.span_set import SpanSet
from tokenizer_tools.tagset.offset.span import Span


class Sequence(object):
    def __init__(
        self, text, span_set: SpanSet = None, id=None, label=None, extra_attr=None
    ):
        # TODO:
        #   1. rename extra_attr to attr
        #   2. move label into attr
        #   3. span_set should include in some column data

        self.text = text
        self.span_set = span_set or SpanSet()
        self.id = id if id is not None else str(uuid.uuid4())
        self.label = label  # for feature usage
        self.extra_attr = extra_attr if extra_attr else {}

    def add_extra_attr(self, **kwargs):
        self.extra_attr = kwargs

    def add_span(self, span):
        pass

    def check_span_set(self):
        check_overlap, overlapped_result = self.span_set.check_overlap()
        check_match, mismatch_result = self.span_set.check_match(self.text)

        return check_overlap and check_match, overlapped_result, mismatch_result

    def __eq__(self, other):
        return (
            self.text == other.text
            and self.span_set == other.span_set
            and self.extra_attr == other.extra_attr
        )

    def __repr__(self):
        return "{}(text={!r}, span_set={!r}, id={!r}, label={!r}, extra_attr={!r})".format(
            self.__class__.__name__,
            self.text,
            self.span_set,
            self.id,
            self.label,
            self.extra_attr,
        )


if __name__ == "__main__":
    seq = Sequence("王小明在北京的清华大学读书。")
    seq.span_set.append(Span(0, 3, "PERSON", "王小明"))
    seq.span_set.append(Span(4, 6, "GPE", "北京"))
    seq.span_set.append(Span(7, 11, "ORG", "清华大学"))

    check_result = seq.check_span_set()
    print(check_result)
