from ...imports import *

__all__ = ["remove_trends"]


def remove_trends(
    self, method="median_filter", **kw
):  # model=None,win_length=None,polyorder=None,butter_cutoff=None,butter_fs=None, butter_order=9,
    """
    A quick tool to approximately remove astrophysical signals,
    usually by some combination of smoothing/filtering.

    Parameters
    ----------
    method : str
        What method should be used to make an approximate model
        for smooth trends that will then be subtracted off?

        `differences` will do an extremely rough filtering
        of replacing the fluxes with their first differences.
        Trends that are smooth relative to the noise will
        be removed this way, but sharp features will remain.
        Required keywords:
            None.

        `median_filter` is a wrapper for scipy.signal.median_filter.
        It smoothes each data point to the median of its surrounding
        points in time and/or wavelength. Required keywords:
            `size` = centered on each point, what shape rectangle
            should be used to select surrounding points for median?
            The dimensions are (nwavelengths, ntimes), so `size=(3,7)`
            means we'll take the median across three wavelengths and
            seven times. Default is `(1,5)`.

        `savgol_filter` is a wrapper for scipy.signal.savgol_filter.
        It applies a Savitzky-Golay filter for polynomial smoothing.
        Required keywords:
            `window_length` = the length of the filter window,
            which must be a positive odd integer. Default is `5`.
            `polyorder` = the order of the polynomial to use.
            Default is `2`.

        `custom` allow users to pass any fluxlike array of model
        values for an astrophysical signal to remove it. Required
        keywords:
            `model` = the (nwavelengths, ntimes) model array

    kw : dict
        Any additional keywords will be passed to the function
        that does the filtering. See `method` keyword for options.

    Returns
    -------
    removed : Rainbow
        The Rainbow with estimated signals removed.
    """

    # create a history entry for this action (before other variables are defined)
    h = self._create_history_entry("remove_trends", locals())

    # TODO, think about more careful treatment of uncertainties + good/bad data
    new = self._create_copy()

    if method == "differences":
        new.flux = np.sqrt(2) * np.gradient(new.flux, axis=0) + 1

    #    if method == "butter_highpass":
    #        for i in range (0,new.nwave):
    #            nyq = 0.5 * butter_fs
    #            normal_cutoff = butter_cutoff/nyq
    #            b, a = butter(butter_order, normal_cutoff, btype = "high", analog = False)
    #            butter_filt = filtfilt(b, a, new.flux[i,:])
    #            new.flux[i,:] = new.flux[i,:]/butter_filt
    #
    #    if method == "convolve":
    #        for i in range (0,new.nwave):
    #            box = np.ones(win_length)/win_length
    #            grad = np.convolve(new.flux[i,:], box, mode = "same")
    #            new.flux[i,:] = new.flux[i,:]/grad

    if method == "median_filter":
        kw_to_use = dict(size=(1, 11))
        kw_to_use.update(**kw)
        if "size" not in kw:
            warnings.warn(
                f"""
            You didn't supply all expected keywords for '{method}'.
            Relying on defaults, the values will be:
            {kw_to_use}
            """
            )
        medfilt = median_filter(new.flux, **kw_to_use)
        new.flux = new.flux / medfilt

    if method == "savgol_filter":
        kw_to_use = dict(window_length=11, polyorder=1)
        kw_to_use.update(**kw)
        if ("window_length" not in kw) or ("polyorder" not in kw):
            warnings.warn(
                f"""
            You didn't supply all expected keywords for '{method}'.
            Relying on defaults, the values will be:
            {kw_to_use}
            """
            )
        for i in range(new.nwave):
            savgolfilter = savgol_filter(new.flux[i, :], **kw_to_use)
            new.flux[i, :] = new.flux[i, :] / savgolfilter

    if method == "custom":
        if "model" not in kw:
            raise ValueError("You need a fluxlike `model` for this `custom` method")
        elif kw["model"].shape != new.flux.shape:
            raise ValueError("Your model doesn't match flux shape")
        else:
            new.flux = new.flux / kw["model"]

    # append the history entry to the new Rainbow
    new._record_history_entry(h)

    # return the new Rainbow
    return new
