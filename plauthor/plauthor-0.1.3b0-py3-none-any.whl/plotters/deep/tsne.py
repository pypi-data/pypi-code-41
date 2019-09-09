__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'
__date__ = '2019_04_25'

# libraries
import os
import numpy
import seaborn as sns
import sklearn
import moviepy.editor as mpy
from numpy import linalg
from sklearn.manifold import TSNE
from moviepy.video.io.bindings import mplfig_to_npimage
from plauthor.plotters.general import scatter


class TSNEAgent:
    """
    t-SNE Visualization Agent
    ==========
    The :class:`TSNEAgent` helps with providing the user with the t-sne related functionalities, allowing mechanisms
    such as making tsne movies, etc. This work is highly inspired by the t-SNE tutorial by oreillymedia in `https://github.com/oreillymedia/t-SNE-tutorial`.
    """
    # constructor
    def __init__(self, configurations=None):
        """
        The constructor of :class:`TSNEAgent` is this method.

        Parameters
        ----------
        configurations: `Dict`, optional (default=None)
        """
        self.random_state = 1994
        configurations = configurations or dict()
        self.configurations = configurations
        self.process_configurations()
        sns.set_style('darkgrid')
        sns.set_palette('muted')
        sns.set_context(
            "notebook",
            font_scale=1.5,
            rc={"lines.linewidth": 2.5}
        )
        self.tsne = None

    def process_configurations(self) -> None:
        """
        This function looks through the configuration file and
        finds the preferences and/or sets defaults
        """
        keys = [
            'tsne.projection_dimension',
            'tsne.perplexity',
            'tsne.early_exaggeration',
            'tsne.learning_rate',
            'tsne.number_of_iterations',
            'tsne.maximum_number_of_iterations_without_progress',
            'tsne.minimum_gradient_norm',
            'tsne.metric',
            'tsne.initialization',
            'tsne.verbose',
            'tsne.random_state',
            'tsne.method',
            'tsne.angle'
        ]
        default_values = [
            3,
            5.0,
            12.0,
            200.0,
            1000,
            300,
            1e-07,
            'euclidean',
            'random',
            1,
            self.random_state,
            'barnes_hut',
            0.5
        ]

        for i in range(len(keys)):
            if not keys[i] in self.configurations.keys():
                self.configurations[keys[i]] = default_values[i]

    def set_random_state(self, seed: int) -> None:
        """
        The :meth:`set_random_state` can be used to set the random state of the class.
        Parameters
        seed: `int`, required
            an integer to set the random seed for this module. It is better
            to fix a random seed in order to be able to recreate results.
        """
        self.random_state = seed

    def find_tsne_projections(
            self,
            X: numpy.ndarray,
            perplexity: float = None
    ) -> numpy.ndarray:
        """
        The :meth:`find_tsne_projections` helps with building the projections of tsne.
        Parameters
        ----------
        X: `numpy.ndarray`, required
            The data as a numpy array of shape: (number_of_data, element_dimension)
        perplexity: `float`, optional (default=None)
            If this value is provided, the perplexity determined by the configuration will be overrided. This
            parameter is here because it is probable for the user to try to have multiple perplexities tested,
            as it is a natural thing to do when it comes to t-SNE.
        Returns
        ----------
        The output of this function is a `numpy.ndarray` which has the shape equal to the number of points times
        the number of t-SNE components, as specified beforehand in the configurations.
        """

        if perplexity is not None:
            self.configurations['tsne.perplexity'] = perplexity

        # making sure X is in valid shape and size
        assert X.shape[0] > X.shape[1], "Really? Less data than data dimension?"
        assert len(X.shape) == 2, "X is of incorrect shape"
        X = X.astype('float')
        projections = TSNE(
            n_components=self.configurations['tsne.projection_dimension'],
            perplexity=self.configurations['tsne.perplexity'],
            early_exaggeration=self.configurations['tsne.early_exaggeration'],
            learning_rate=self.configurations['tsne.learning_rate'],
            n_iter=self.configurations['tsne.number_of_iterations'],
            n_iter_without_progress=self.configurations['tsne.maximum_number_of_iterations_without_progress'],
            min_grad_norm=self.configurations['tsne.minimum_gradient_norm'],
            metric=self.configurations['tsne.metric'],
            init=self.configurations['tsne.initialization'],
            verbose=self.configurations['tsne.verbose'],
            method=self.configurations['tsne.method'],
            angle=self.configurations['tsne.angle'],
            random_state=self.random_state
        ).fit_transform(X)

        return projections

    def make_a_tsne_movie(self, X: numpy.ndarray, y: numpy.ndarray, movie_path: str) -> None:
        """
        The :meth:`make_a_tsne_movie` helps with making a t-SNE movie. This is essentially useful
        when we have a slow-converging process, and having a movie can help shedding light on the path
        from bad locations to possibly good ones in the space.

        Parameters
        ----------
        X: `numpy.ndarray`, required
            The data as a numpy array of shape: (number_of_data, element_dimension)
        y: `numpy.ndarray`, required
            The one-dimensional array of labels.
        movie_path: `str`, required
            The filepath to the movie. Note that the folder should exist and the image should be in `.gif` format.

        Returns
        ----------
        The output of this function is a `numpy.ndarray` which has the shape equal to the number of points times
        the number of t-SNE components, as specified beforehand in the configurations.
        """
        y = y.astype('int')
        y = y - numpy.min(y)
        assert movie_path.endswith('.gif'), "The movie path is a path to your desired gif file."
        old_gradient_descent = sklearn.manifold.t_sne._gradient_descent

        def _gradient_descent(
                objective, p0, it, n_iter, n_iter_without_progress=30, momentum=0.5, learning_rate=1000.0,
                min_gain=0.01, min_grad_norm=1e-7, min_error_diff=1e-7, verbose=0, args=[], kwargs=None,
                n_iter_check=1):
            # The documentation of this function can be found in scikit-learn's code.
            p = p0.copy().ravel()
            update = numpy.zeros_like(p)
            gains = numpy.ones_like(p)
            error = numpy.finfo(numpy.float).max
            best_error = numpy.finfo(numpy.float).max
            best_iter = 0

            for i in range(it, n_iter):
                # We save the current position.
                positions.append(p.copy())

                new_error, grad = objective(p, *args)
                error_diff = numpy.abs(new_error - error)
                error = new_error
                grad_norm = linalg.norm(grad)

                if error < best_error:
                    best_error = error
                    best_iter = i
                elif i - best_iter > n_iter_without_progress:
                    break
                if min_grad_norm >= grad_norm:
                    break
                if min_error_diff >= error_diff:
                    break

                inc = update * grad >= 0.0
                dec = numpy.invert(inc)
                gains[inc] += 0.05
                gains[dec] *= 0.95
                numpy.clip(gains, min_gain, numpy.inf)
                grad *= gains
                update = momentum * update - learning_rate * grad
                p += update

            return p, error, i

        sklearn.manifold.t_sne._gradient_descent = _gradient_descent

        positions = []
        print('building tsne...\n')
        _ = self.find_tsne_projections(X)
        sklearn.manifold.t_sne._gradient_descent = old_gradient_descent
        X_iter = numpy.dstack(position.reshape(-1, 2) for position in positions)
        f, ax, sc, txts, number_of_classes = scatter(X_iter[..., -1], y)

        def frame_generation_protocol(t):
            i = int(t * 40)
            x = X_iter[..., i]
            sc.set_offsets(x)
            for class_index, txt in zip(range(number_of_classes), txts):
                xtext, ytext = numpy.median(x[y == class_index, :], axis=0)
                txt.set_x(xtext)
                txt.set_y(ytext)
            return mplfig_to_npimage(f)

        animation = mpy.VideoClip(
            frame_generation_protocol,
            duration=X_iter.shape[2] / 40.)

        animation.write_gif(os.path.abspath(movie_path), fps=20)
