import bilby
from bilby.core import likelihood

class GravitationalWaveTransientDistributed(bilby.likelihood.GravitationalWaveTransient):
    """ A gravitational-wave transient likelihood object

    This is the usual likelihood object to use for transient gravitational
    wave parameter estimation. It computes the log-likelihood in the frequency
    domain assuming a colored Gaussian noise model described by a power
    spectral density


    Parameters
    ----------
    interferometers: list, bilby.gw.detector.InterferometerList
        A list of `bilby.detector.Interferometer` instances - contains the
        detector data and power spectral densities
    waveform_generator: `bilby.waveform_generator.WaveformGenerator`
        An object which computes the frequency-domain strain of the signal,
        given some set of parameters
    distance_marginalization: bool, optional
        If true, marginalize over distance in the likelihood.
        This uses a look up table calculated at run time.
    time_marginalization: bool, optional
        If true, marginalize over time in the likelihood.
        This uses a FFT.
    phase_marginalization: bool, optional
        If true, marginalize over phase in the likelihood.
        This is done analytically using a Bessel function.
    priors: dict, optional
        If given, used in the distance and phase marginalization.
    distance_marginalization_lookup_table: (dict, str), optional
        If a dict, dictionary containing the lookup_table, distance_array,
        (distance) prior_array, and reference_distance used to construct
        the table.
        If a string the name of a file containing these quantities.
        The lookup table is stored after construction in either the
        provided string or a default location:
        '.distance_marginalization_lookup_dmin{}_dmax{}_n{}.npz'

    Returns
    -------
    Likelihood: `bilby.core.likelihood.Likelihood`
        A likelihood object, able to compute the likelihood of the data given
        some model parameters

    """

    _CalculatedSNRs = namedtuple('CalculatedSNRs',
                                 ['d_inner_h',
                                  'optimal_snr_squared',
                                  'complex_matched_filter_snr',
                                  'd_inner_h_squared_tc_array'])


    def __repr__(self):
        return self.__class__.__name__ + '(interferometers={},\n\twaveform_generator={},\n\ttime_marginalization={}, ' \
                                         'distance_marginalization={}, phase_marginalization={}, priors={})'\
            .format(self.interferometers, self.waveform_generator, self.time_marginalization,
                    self.distance_marginalization, self.phase_marginalization, self.priors)

    def log_likelihood_ratio(self):

        # Remember heron produces a dictionary with an array of waveforms for each polarisation, and not just a single sample.
        waveform_samples =\
            self.waveform_generator.frequency_domain_strain(self.parameters)

        if waveform_polarizations is None:
            return np.nan_to_num(-np.inf)

        d_inner_h = 0.
        optimal_snr_squared = 0.
        complex_matched_filter_snr = 0.
        d_inner_h_squared_tc_array = np.zeros(
            self.interferometers.frequency_array[0:-1].shape,
            dtype=np.complex128)

        for interferometer in self.interferometers:
            for waveform_polarizations in waveform_samples:
                per_detector_snr = self.calculate_snrs(
                    waveform_polarizations, interferometer)

                d_inner_h += per_detector_snr.d_inner_h
                optimal_snr_squared += per_detector_snr.optimal_snr_squared
                complex_matched_filter_snr += per_detector_snr.complex_matched_filter_snr

                if self.time_marginalization:
                    d_inner_h_squared_tc_array += per_detector_snr.d_inner_h_squared_tc_array

                

        if self.time_marginalization:

            if self.distance_marginalization:
                rho_mf_ref_tc_array, rho_opt_ref = self._setup_rho(
                    d_inner_h_squared_tc_array, optimal_snr_squared)
                if self.phase_marginalization:
                    dist_marged_log_l_tc_array = self._interp_dist_margd_loglikelihood(
                        abs(rho_mf_ref_tc_array), rho_opt_ref)
                else:
                    dist_marged_log_l_tc_array = self._interp_dist_margd_loglikelihood(
                        rho_mf_ref_tc_array.real, rho_opt_ref)
                log_l = logsumexp(dist_marged_log_l_tc_array,
                                  b=self.time_prior_array)
            elif self.phase_marginalization:
                log_l = logsumexp(self._bessel_function_interped(abs(
                    d_inner_h_squared_tc_array)),
                    b=self.time_prior_array) - optimal_snr_squared / 2
            else:
                log_l = logsumexp(
                    d_inner_h_squared_tc_array.real,
                    b=self.time_prior_array) - optimal_snr_squared / 2

        elif self.distance_marginalization:
            rho_mf_ref, rho_opt_ref = self._setup_rho(d_inner_h, optimal_snr_squared)
            if self.phase_marginalization:
                rho_mf_ref = abs(rho_mf_ref)
            log_l = self._interp_dist_margd_loglikelihood(rho_mf_ref.real, rho_opt_ref)[0]

        elif self.phase_marginalization:
            d_inner_h = self._bessel_function_interped(abs(d_inner_h))
            log_l = d_inner_h - optimal_snr_squared / 2

        else:
            log_l = d_inner_h.real - optimal_snr_squared / 2

        return log_l.real

    # This also needs to be changed
    def generate_posterior_sample_from_marginalized_likelihood(self):
        """
        Reconstruct the distance posterior from a run which used a likelihood
        which explicitly marginalised over time/distance/phase.

        See Eq. (C29-C32) of https://arxiv.org/abs/1809.02293

        Return
        ------
        sample: dict
            Returns the parameters with new samples.

        Notes
        -----
        This involves a deepcopy of the signal to avoid issues with waveform
        caching, as the signal is overwritten in place.
        """
        if any([self.phase_marginalization, self.distance_marginalization,
                self.time_marginalization]):
            signal_polarizations = copy.deepcopy(
                self.waveform_generator.frequency_domain_strain(
                    self.parameters))
        else:
            return self.parameters
        if self.time_marginalization:
            new_time = self.generate_time_sample_from_marginalized_likelihood(
                signal_polarizations=signal_polarizations)
            self.parameters['geocent_time'] = new_time
        if self.distance_marginalization:
            new_distance = self.generate_distance_sample_from_marginalized_likelihood(
                signal_polarizations=signal_polarizations)
            self.parameters['luminosity_distance'] = new_distance
        if self.phase_marginalization:
            new_phase = self.generate_phase_sample_from_marginalized_likelihood(
                signal_polarizations=signal_polarizations)
            self.parameters['phase'] = new_phase
        return self.parameters.copy()

    def generate_time_sample_from_marginalized_likelihood(
            self, signal_polarizations=None):
        """
        Generate a single sample from the posterior distribution for coalescence
        time when using a likelihood which explicitly marginalises over time.

        In order to resolve the posterior we artifically upsample to 16kHz.

        See Eq. (C29-C32) of https://arxiv.org/abs/1809.02293

        Parameters
        ----------
        signal_polarizations: dict, optional
            Polarizations modes of the template.

        Returns
        -------
        new_time: float
            Sample from the time posterior.
        """
        if signal_polarizations is None:
            signal_polarizations = \
                self.waveform_generator.frequency_domain_strain(self.parameters)
        n_time_steps = int(self.waveform_generator.duration * 16384)
        d_inner_h = np.zeros(n_time_steps, dtype=np.complex)
        psd = np.ones(n_time_steps)
        signal_long = np.zeros(n_time_steps, dtype=np.complex)
        data = np.zeros(n_time_steps, dtype=np.complex)
        h_inner_h = np.zeros(1)
        for ifo in self.interferometers:
            ifo_length = len(ifo.frequency_domain_strain)
            signal = ifo.get_detector_response(
                signal_polarizations, self.parameters)
            signal_long[:ifo_length] = signal
            data[:ifo_length] = np.conj(ifo.frequency_domain_strain)
            psd[:ifo_length] = ifo.power_spectral_density_array
            d_inner_h += np.fft.fft(signal_long * data / psd)
            h_inner_h += ifo.optimal_snr_squared(signal=signal).real

        if self.distance_marginalization:
            rho_mf_ref_tc_array, rho_opt_ref = self._setup_rho(
                d_inner_h, h_inner_h)
            if self.phase_marginalization:
                time_log_like = self._interp_dist_margd_loglikelihood(
                    abs(rho_mf_ref_tc_array), rho_opt_ref)
            else:
                time_log_like = self._interp_dist_margd_loglikelihood(
                    rho_mf_ref_tc_array.real, rho_opt_ref)
        elif self.phase_marginalization:
            time_log_like = (self._bessel_function_interped(abs(d_inner_h)) -
                             h_inner_h.real / 2)
        else:
            time_log_like = (d_inner_h.real - h_inner_h.real / 2)

        times = create_time_series(
            sampling_frequency=16384,
            starting_time=self.waveform_generator.start_time,
            duration=self.waveform_generator.duration)

        time_prior_array = self.priors['geocent_time'].prob(times)
        time_post = (
            np.exp(time_log_like - max(time_log_like)) * time_prior_array)

        keep = (time_post > max(time_post) / 1000)
        time_post = time_post[keep]
        times = times[keep]
        new_time = Interped(times, time_post).sample()
        return new_time

    def generate_distance_sample_from_marginalized_likelihood(
            self, signal_polarizations=None):
        """
        Generate a single sample from the posterior distribution for luminosity
        distance when using a likelihood which explicitly marginalises over
        distance.

        See Eq. (C29-C32) of https://arxiv.org/abs/1809.02293

        Parameters
        ----------
        signal_polarizations: dict, optional
            Polarizations modes of the template.
            Note: These are rescaled in place after the distance sample is
                  generated to allow further parameter reconstruction to occur.

        Returns
        -------
        new_distance: float
            Sample from the distance posterior.
        """
        if signal_polarizations is None:
            signal_polarizations = \
                self.waveform_generator.frequency_domain_strain(self.parameters)
        d_inner_h = 0
        h_inner_h = 0
        for interferometer in self.interferometers:
            per_detector_snr = self.calculate_snrs(
                signal_polarizations, interferometer)

            d_inner_h += per_detector_snr.d_inner_h
            h_inner_h += per_detector_snr.optimal_snr_squared

        d_inner_h_dist = (
            d_inner_h * self.parameters['luminosity_distance'] /
            self._distance_array)

        h_inner_h_dist = (
            h_inner_h * self.parameters['luminosity_distance']**2 /
            self._distance_array**2)

        if self.phase_marginalization:
            distance_log_like = (
                self._bessel_function_interped(abs(d_inner_h_dist)) -
                h_inner_h_dist.real / 2)
        else:
            distance_log_like = (d_inner_h_dist.real - h_inner_h_dist.real / 2)

        distance_post = (np.exp(distance_log_like - max(distance_log_like)) *
                         self.distance_prior_array)

        new_distance = Interped(
            self._distance_array, distance_post).sample()

        self._rescale_signal(signal_polarizations, new_distance)
        return new_distance

    def generate_phase_sample_from_marginalized_likelihood(
            self, signal_polarizations=None):
        """
        Generate a single sample from the posterior distribution for phase when
        using a likelihood which explicitly marginalises over phase.

        See Eq. (C29-C32) of https://arxiv.org/abs/1809.02293

        Parameters
        ----------
        signal_polarizations: dict, optional
            Polarizations modes of the template.

        Returns
        -------
        new_phase: float
            Sample from the phase posterior.

        Notes
        -----
        This is only valid when assumes that mu(phi) \propto exp(-2i phi).
        """
        if signal_polarizations is None:
            signal_polarizations = \
                self.waveform_generator.frequency_domain_strain(self.parameters)
        d_inner_h = 0
        h_inner_h = 0
        for interferometer in self.interferometers:
            per_detector_snr = self.calculate_snrs(
                signal_polarizations, interferometer)

            d_inner_h += per_detector_snr.d_inner_h
            h_inner_h += per_detector_snr.optimal_snr_squared

        phases = np.linspace(0, 2 * np.pi, 101)
        phasor = np.exp(-2j * phases)
        phase_log_post = d_inner_h * phasor - d_inner_h / 2
        phase_post = np.exp(phase_log_post.real - max(phase_log_post.real))
        new_phase = Interped(phases, phase_post).sample()
        return new_phase

    def _setup_rho(self, d_inner_h, optimal_snr_squared):
        rho_opt_ref = (optimal_snr_squared.real *
                       self.parameters['luminosity_distance'] ** 2 /
                       self._ref_dist ** 2.)
        rho_mf_ref = (d_inner_h * self.parameters['luminosity_distance'] /
                      self._ref_dist)
        return rho_mf_ref, rho_opt_ref

    def log_likelihood(self):
        return self.log_likelihood_ratio() + self.noise_log_likelihood()

    @property
    def _delta_distance(self):
        return self._distance_array[1] - self._distance_array[0]

    @property
    def _ref_dist(self):
        """ Smallest distance contained in priors """
        return self._distance_array[0]

    @property
    def _rho_opt_ref_array(self):
        """ Optimal filter snr at fiducial distance of ref_dist Mpc """
        return np.logspace(-5, 10, self._dist_margd_loglikelihood_array.shape[0])

    @property
    def _rho_mf_ref_array(self):
        """ Matched filter snr at fiducial distance of ref_dist Mpc """
        if self.phase_marginalization:
            return np.logspace(-5, 10, self._dist_margd_loglikelihood_array.shape[1])
        else:
            return np.hstack((-np.logspace(3, -3, self._dist_margd_loglikelihood_array.shape[1] / 2),
                              np.logspace(-3, 10, self._dist_margd_loglikelihood_array.shape[1] / 2)))

    def _setup_distance_marginalization(self, lookup_table=None):
        if isinstance(lookup_table, str) or lookup_table is None:
            self.cached_lookup_table_filename = lookup_table
            lookup_table = self.load_lookup_table(
                self.cached_lookup_table_filename)
        if isinstance(lookup_table, dict):
            if self._test_cached_lookup_table(lookup_table):
                self._dist_margd_loglikelihood_array = lookup_table[
                    'lookup_table']
            else:
                self._create_lookup_table()
        else:
            self._create_lookup_table()
        self._interp_dist_margd_loglikelihood = UnsortedInterp2d(
            self._rho_mf_ref_array, self._rho_opt_ref_array,
            self._dist_margd_loglikelihood_array)

    @property
    def cached_lookup_table_filename(self):
        if self._lookup_table_filename is None:
            dmin = self._distance_array[0]
            dmax = self._distance_array[-1]
            n = len(self._distance_array)
            self._lookup_table_filename = (
                '.distance_marginalization_lookup.npz'
                .format(dmin, dmax, n))
        return self._lookup_table_filename

    @cached_lookup_table_filename.setter
    def cached_lookup_table_filename(self, filename):
        if isinstance(filename, str):
            if filename[-4:] != '.npz':
                filename += '.npz'
        self._lookup_table_filename = filename

    def load_lookup_table(self, filename):
        if os.path.exists(filename):
            loaded_file = dict(np.load(filename))
            match, failure = self._test_cached_lookup_table(loaded_file)
            if match:
                logger.info('Loaded distance marginalisation lookup table from '
                            '{}.'.format(filename))
                return loaded_file
            else:
                logger.info('Loaded distance marginalisation lookup table does '
                            'not match for {}.'.format(failure))
                return None
        elif isinstance(filename, str):
            logger.info('Distance marginalisation file {} does not '
                        'exist'.format(filename))
            return None
        else:
            return None

    def cache_lookup_table(self):
        np.savez(self.cached_lookup_table_filename,
                 distance_array=self._distance_array,
                 prior_array=self.distance_prior_array,
                 lookup_table=self._dist_margd_loglikelihood_array,
                 reference_distance=self._ref_dist,
                 phase_marginalization=self.phase_marginalization)

    def _test_cached_lookup_table(self, loaded_file):
        pairs = dict(
            distance_array=self._distance_array,
            prior_array=self.distance_prior_array,
            reference_distance=self._ref_dist,
            phase_marginalization=self.phase_marginalization)
        for key in pairs:
            if key not in loaded_file:
                return False, key
            elif not np.array_equal(np.atleast_1d(loaded_file[key]),
                                    np.atleast_1d(pairs[key])):
                return False, key
        return True, None

    def _create_lookup_table(self):
        """ Make the lookup table """
        logger.info('Building lookup table for distance marginalisation.')

        self._dist_margd_loglikelihood_array = np.zeros((400, 800))
        for ii, rho_opt_ref in enumerate(self._rho_opt_ref_array):
            for jj, rho_mf_ref in enumerate(self._rho_mf_ref_array):
                optimal_snr_squared_array = rho_opt_ref * self._ref_dist ** 2. / self._distance_array ** 2
                d_inner_h_array = rho_mf_ref * self._ref_dist / self._distance_array
                if self.phase_marginalization:
                    d_inner_h_array =\
                        self._bessel_function_interped(abs(d_inner_h_array))
                self._dist_margd_loglikelihood_array[ii][jj] = \
                    logsumexp(d_inner_h_array - optimal_snr_squared_array / 2,
                              b=self.distance_prior_array * self._delta_distance)
        log_norm = logsumexp(0. / self._distance_array - 0. / self._distance_array ** 2.,
                             b=self.distance_prior_array * self._delta_distance)
        self._dist_margd_loglikelihood_array -= log_norm
        self.cache_lookup_table()

    def _setup_phase_marginalization(self):
        self._bessel_function_interped = interp1d(
            np.logspace(-5, 10, int(1e6)), np.logspace(-5, 10, int(1e6)) +
            np.log([i0e(snr) for snr in np.logspace(-5, 10, int(1e6))]),
            bounds_error=False, fill_value=(0, np.nan))

    def _setup_time_marginalization(self):
        delta_tc = 2 / self.waveform_generator.sampling_frequency
        self._times =\
            self.interferometers.start_time + np.linspace(
                0, self.interferometers.duration,
                int(self.interferometers.duration / 2 *
                    self.waveform_generator.sampling_frequency + 1))[1:]
        self.time_prior_array =\
            self.priors['geocent_time'].prob(self._times) * delta_tc

    @property
    def interferometers(self):
        return self._interferometers

    @interferometers.setter
    def interferometers(self, interferometers):
        self._interferometers = InterferometerList(interferometers)

    def _rescale_signal(self, signal, new_distance):
        for mode in signal:
            signal[mode] *= self._ref_dist / new_distance

    @property
    def meta_data(self):
        return dict(
            interferometers=self.interferometers.meta_data,
            time_marginalization=self.time_marginalization,
            phase_marginalization=self.phase_marginalization,
            distance_marginalization=self.distance_marginalization,
            waveform_arguments=self.waveform_generator.waveform_arguments,
            frequency_domain_source_model=str(
                self.waveform_generator.frequency_domain_source_model),
            sampling_frequency=self.waveform_generator.sampling_frequency,
            duration=self.waveform_generator.duration,
            start_time=self.waveform_generator.start_time)
