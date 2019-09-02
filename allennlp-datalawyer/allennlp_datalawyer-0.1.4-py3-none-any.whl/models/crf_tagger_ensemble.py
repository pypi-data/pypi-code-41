from typing import Dict, List, Any

from overrides import overrides
import torch
import numpy as np

from allennlp.common.checks import ConfigurationError
from allennlp_datalawyer.models.ensemble import Ensemble
from allennlp.models.archival import load_archive
from allennlp.models.model import Model
from allennlp.models.crf_tagger import CrfTagger
from allennlp.common import Params
from allennlp.data import Vocabulary
from allennlp.training.metrics import CategoricalAccuracy, SpanBasedF1Measure


@Model.register("crf_tagger-ensemble")
class CrfTaggerEnsemble(Ensemble):
    """
    This class ensembles the output from multiple CrfTagger models.

    It combines results from the submodels by averaging the start and end span probabilities.
    """

    def __init__(self, submodels: List[CrfTagger]) -> None:
        super().__init__(submodels)
        self.vocab = submodels[0].vocab
        self.metrics = {
            "accuracy": CategoricalAccuracy(),
            "accuracy3": CategoricalAccuracy(top_k=3)
        }
        self._verbose_metrics = submodels[0]._verbose_metrics
        self.label_namespace = submodels[0].label_namespace
        self.label_encoding = submodels[0].label_encoding
        self.calculate_span_f1 = submodels[0].calculate_span_f1
        if self.calculate_span_f1:
            if not self.label_encoding:
                raise ConfigurationError("calculate_span_f1 is True, but "
                                         "no label_encoding was specified.")
            self._f1_metric = SpanBasedF1Measure(self.vocab,
                                                 tag_namespace=self.label_namespace,
                                                 label_encoding=self.label_encoding)

    @overrides
    def forward(self,  # type: ignore
                tokens: Dict[str, torch.LongTensor],
                tags: torch.LongTensor = None,
                metadata: List[Dict[str, Any]] = None,
                # pylint: disable=unused-argument
                **kwargs) -> Dict[str, torch.Tensor]:
        # pylint: disable=arguments-differ
        """
        Parameters
        ----------
        tokens : ``Dict[str, torch.LongTensor]``, required
            The output of ``TextField.as_array()``, which should typically be passed directly to a
            ``TextFieldEmbedder``. This output is a dictionary mapping keys to ``TokenIndexer``
            tensors.  At its most basic, using a ``SingleIdTokenIndexer`` this is: ``{"tokens":
            Tensor(batch_size, num_tokens)}``. This dictionary will have the same keys as were used
            for the ``TokenIndexers`` when you created the ``TextField`` representing your
            sequence.  The dictionary is designed to be passed directly to a ``TextFieldEmbedder``,
            which knows how to combine different word representations into a single vector per
            token in your input.
        tags : ``torch.LongTensor``, optional (default = ``None``)
            A torch tensor representing the sequence of integer gold class labels of shape
            ``(batch_size, num_tokens)``.
        metadata : ``List[Dict[str, Any]]``, optional, (default = None)
            metadata containg the original words in the sentence to be tagged under a 'words' key.

        Returns
        -------
        An output dictionary consisting of:

        logits : ``torch.FloatTensor``
            The logits that are the output of the ``tag_projection_layer``
        mask : ``torch.LongTensor``
            The text field mask for the input tokens
        tags : ``List[List[int]]``
            The predicted tags using the Viterbi algorithm.
        loss : ``torch.FloatTensor``, optional
            A scalar loss to be optimised. Only computed if gold label ``tags`` are provided.
        """

        subresults = [submodel(tokens, tags, metadata) for submodel in self.submodels]

        # batch_size = len(subresults[0]["tags"])

        return self.ensemble(subresults)

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics_to_return = {metric_name: metric.get_metric(reset) for
                             metric_name, metric in self.metrics.items()}

        if self.calculate_span_f1:
            f1_dict = self._f1_metric.get_metric(reset=reset)
            if self._verbose_metrics:
                metrics_to_return.update(f1_dict)
            else:
                metrics_to_return.update({
                    x: y for x, y in f1_dict.items() if
                    "overall" in x})
        return metrics_to_return

    # The logic here requires a custom from_params.
    @classmethod
    def from_params(cls, vocab: Vocabulary, params: Params) -> 'CrfTaggerEnsemble':  # type: ignore
        # pylint: disable=arguments-differ
        if vocab:
            raise ConfigurationError("vocab should be None")

        submodels = []
        paths = params.pop("submodels")
        for path in paths:
            submodels.append(load_archive(path).model)

        return cls(submodels=submodels)

    def ensemble(self, subresults: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """
        Identifies the best prediction given the results from the submodels.

        Parameters
        ----------
        index : int
            The index within this index to ensemble

        subresults : List[Dict[str, torch.Tensor]]

        Returns
        -------
        The index of the best submodel.
        """

        # Choose the highest average confidence span.

        best_paths = [submodel.crf.viterbi_tags(subresult['logits'], subresult['mask'])[0][1] for submodel, subresult in
                      zip(self.submodels, subresults)]

        # log_likelihoods = [-submodel.crf(subresult['logits'], torch.tensor(subresult['tags']), subresult['mask']) for
        #                    submodel, subresult in zip(self.submodels, subresults)]

        return subresults[np.argmax(best_paths)]
