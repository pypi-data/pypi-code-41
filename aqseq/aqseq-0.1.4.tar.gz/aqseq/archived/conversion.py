import jdna
import re


def extract_sequence_id_from_benchling_weblink(link):
    m = re.search("/seq-(\w+)-", link)
    if m is not None:
        return "seq_{}".format(m.group(1))


def benchling_annotation_to_jdna_feature(seq, annotation):
    """
    Converts a benchling annotation to a jDNA feature

    :param seq: jdna sequence
    :param annotation: benchling Annotation
    :return: jDNA feature
    """
    feature = jdna.core.Feature(
        annotation.name,
        type=annotation.type,
        strand=annotation.strand,
        color=annotation.color,
    )
    seq.add_feature(feature=feature, i=annotation.start, j=annotation.end - 1)
    return feature


def jdna_feature_to_benchling_annotation(feature, start, end):
    """
    Converts a jDNA feature to a benchling annotation

    :param feature: jDNA feature
    :param start: start of the feature
    :param end: end of the feature
    :return: benchling Annotation
    """
    return benchapi.Annotation(
        name=feature.name,
        start=start,
        end=end + 1,
        strand=feature.strand,
        type=feature.type,
        color=feature.color,
    )


def benchling_to_jdna(benchling_sequence):
    """
    Converts a benchling sequence to a jDNA sequence

    :param benchling_sequence: benchling DNASequence
    :return: jDNA sequence
    """
    seq = jdna.Sequence(sequence=benchling_sequence.bases.upper())
    if benchling_sequence.isCircular:
        seq.make_cyclic()
    for a in benchling_sequence.annotations:
        try:
            benchling_annotation_to_jdna_feature(seq, a)
        except:
            print("Could not add feature {}".format(a["name"]))
    return seq


def jdna_to_benchling(seq):
    """
    Converts a jDNA sequence to a benchling DNASequence

    :param seq: jDNA sequence
    :return: benchling DNASequence
    """
    annotations = []
    for feature, pos in seq.get_features().items():
        annotations.append(jdna_feature_to_benchling_annotation(feature, *pos[0]))

    return benchapi.DNASequence(
        bases=str(seq),
        name=seq.name,
        isCircular=seq.is_cyclic(),
        annotations=annotations,
    )


def coral_feature_to_benchling_annotation(feature):
    strand = feature.strand
    if strand == 0:
        strand = -1
    return benchapi.Annotation(
        name=feature.name,
        start=feature.start,
        end=feature.stop,
        strand=strand,
        type=feature.feature_type,
        color=feature.qualifiers["ApEinfo_fwdcolor"],
    )


def benchling_annotation_to_coral_feature(annotation):
    raise NotImplementedError


def benchling_to_coral(dna0):
    raise NotImplementedError


def coral_to_benchling(dna):
    return benchapi.DNASequence(
        name=dna.name,
        bases=str(dna),
        circular=dna.circular,
        annotations=[coral_feature_to_benchling_annotation(a) for a in dna.features],
    )
